import datetime
import random
from typing import List, Mapping, Optional, Union, cast

import pytz
import requests
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
    def __init__(self, event_data: RawEvent) -> None:
        data = event_data['fields']
        self.id = cast(Optional[str], data['id'])
        self.slug = cast(Optional[str], data['slug'])
        self.title = cast(str, data['title'])
        self.subtitle = cast(Optional[str], data['subtitle'])
        self.date_string = cast(str, data['date'])
        self.date = datetime.datetime.fromisoformat(self.date_string)
        self.date = TIMEZONE.localize(self.date)
        self.location_name = cast(Optional[str], data['locationName'])
        self.location_type = cast(Optional[str], data['locationType'])
        self.ticket_required = cast(bool, data['ticketRequired'])
        self.ticket_available = cast(bool, data['ticketAvailable'])
        self.ticket_sold_out = cast(bool, data['ticketSoldOut'])
        self.hide_road_game = data['hideRoadGame'] == 'yes'
        self.duration = cast(int, data['duration'])

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
    raw_response = response.json()
    raw_query_response = raw_response['data']['contentByType']['items']
    return cast(RawQueryResponse, raw_query_response)


CachedEvents: List[Event] = []
CachedEventsExpire = datetime.datetime.now()


def get_events() -> List[Event]:
    global CachedEvents, CachedEventsExpire
    if CachedEvents and CachedEventsExpire > datetime.datetime.now():
        return CachedEvents
    raw_events = get_raw_events()
    events = [Event(e) for e in raw_events]
    events = sorted(events, key=lambda e: e.date)
    _refresh_cache(events)
    return events


def _refresh_cache(events: List[Event]) -> None:
    global CachedEvents, CachedEventsExpire
    CachedEvents = events
    cache_duration = datetime.timedelta(minutes=random.randint(30, 90))
    CachedEventsExpire = datetime.datetime.now() + cache_duration
