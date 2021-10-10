import datetime
import json
import random
from typing import List, Mapping, Optional, Union, cast

import pytz
import requests
import rollbar
from varsnap import varsnap


FieldValues = Union[None, str, bool, int]
RawEvent = Mapping[str, Mapping[str, FieldValues]]
# RawQueryResponse = Mapping[str, Mapping[str, Mapping[str, List[RawEvent]]]]
RawQueryResponse = List[RawEvent]

URL = "https://content-api-dot-chasecenter-com.appspot.com/graphql"
QUERY = """
{
  contentByType(id: "event") {
    items {
      fields {
        ... on event {
          id
          slug
          title
          subtitle
          date
          locationName
          locationType
          ticketRequired
          ticketAvailable
          ticketSoldOut
          hideRoadGame
          duration
        }
      }
    }
  }
}
"""
TIMEZONE = pytz.timezone('America/Los_Angeles')


class Event():
    def __init__(self) -> None:
        self.id: Optional[str] = None
        self.slug: Optional[str] = None
        self.title: str = ''
        self.subtitle: Optional[str] = None
        self.date_string: str = ''
        now = datetime.datetime.now()
        self.date: datetime.datetime = TIMEZONE.localize(now)
        self.location_name: Optional[str] = None
        self.location_type: Optional[str] = None
        self.ticket_required: bool = False
        self.ticket_available: bool = False
        self.ticket_sold_out: bool = False
        self.hide_road_game: bool = False
        self.duration: int = 60

    @staticmethod
    def initialize_chase(event_data: RawEvent) -> 'Event':
        event = Event()
        data = event_data['fields']
        event.id = cast(Optional[str], data['id'])
        event.slug = cast(Optional[str], data['slug'])
        event.title = cast(str, data['title'])
        event.subtitle = cast(Optional[str], data['subtitle'])
        event.date_string = cast(str, data['date'])
        date = datetime.datetime.fromisoformat(event.date_string)
        event.date = TIMEZONE.localize(date)
        event.location_name = cast(Optional[str], data['locationName'])
        event.location_type = cast(Optional[str], data['locationType'])
        event.ticket_required = cast(bool, data['ticketRequired'])
        event.ticket_available = cast(bool, data['ticketAvailable'])
        event.ticket_sold_out = cast(bool, data['ticketSoldOut'])
        event.hide_road_game = data['hideRoadGame'] == 'yes'
        event.duration = cast(int, data['duration'])
        return event

    @property  # type: ignore
    @varsnap
    def show(self) -> bool:
        if self.hide_road_game:
            return False
        return True

    @property  # type: ignore
    @varsnap
    def is_future(self) -> bool:
        cutoff = datetime.datetime.now(TIMEZONE) - datetime.timedelta(days=1)
        return self.date > cutoff

    @property  # type: ignore
    @varsnap
    def end(self) -> datetime.datetime:
        return self.date + datetime.timedelta(hours=self.duration)


def get_raw_events() -> RawQueryResponse:
    data = {
        'query': QUERY,
    }
    response = requests.post(URL, data=data)
    try:
        raw_response = response.json()
    except json.JSONDecodeError:
        rollbar.report_message('Cannot parse chasecenter json', 'warning')
        return []
    try:
        raw_query_response = raw_response['data']['contentByType']['items']
    except KeyError:
        rollbar.report_message('Received corrupt chasecenter json', 'warning')
        return []
    return cast(RawQueryResponse, raw_query_response)


CachedEvents: List[Event] = []
CachedEventsExpire = datetime.datetime.now()


def get_events() -> List[Event]:
    global CachedEvents, CachedEventsExpire
    if CachedEvents and CachedEventsExpire > datetime.datetime.now():
        return CachedEvents
    raw_events = get_raw_events()
    events = [Event.initialize_chase(e) for e in raw_events]
    events = sorted(events, key=lambda e: e.date)
    _refresh_cache(events)
    return events


def _refresh_cache(events: List[Event]) -> None:
    global CachedEvents, CachedEventsExpire
    CachedEvents = events
    cache_duration = datetime.timedelta(minutes=random.randint(30, 90))
    CachedEventsExpire = datetime.datetime.now() + cache_duration
