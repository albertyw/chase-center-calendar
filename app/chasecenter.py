import datetime
import json
from typing import List, Mapping, Optional, Union, cast

import requests
import rollbar
from varsnap import varsnap

from app import cache
from app.event import Event, TIMEZONE


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


@varsnap
def initialize_chase_event(event_data: RawEvent) -> Event:
    event = Event()
    data = event_data['fields']
    event.id = cast(Optional[str], data['id'])
    event.slug = cast(Optional[str], data['slug'])
    event.title = cast(str, data['title'])
    event.subtitle = cast(Optional[str], data['subtitle'])
    event.date_string = cast(str, data['date'])
    date = datetime.datetime.fromisoformat(event.date_string)
    event.date = date.replace(tzinfo=TIMEZONE)
    event.location_name = cast(Optional[str], data['locationName'])
    event.location_type = cast(Optional[str], data['locationType'])
    event.ticket_required = cast(bool, data['ticketRequired'])
    event.ticket_available = cast(bool, data['ticketAvailable'])
    event.ticket_sold_out = cast(bool, data['ticketSoldOut'])
    event.hide_road_game = data['hideRoadGame'] == 'yes'
    event.duration = cast(int, data['duration'])
    return event


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


def get_events() -> List[Event]:
    events = cache.read_cache(cache.CACHED_CHASECENTER)
    if events:
        return events
    raw_events = get_raw_events()
    events = [initialize_chase_event(e) for e in raw_events]
    events = sorted(events, key=lambda e: e.date)
    cache.save_cache(cache.CACHED_CHASECENTER, events)
    return events
