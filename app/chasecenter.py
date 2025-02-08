import datetime
import json
from typing import List, Mapping, Optional, Union, cast

import requests
import rollbar
from slugify import slugify
from varsnap import varsnap

from app import cache
from app.event import Event, TIMEZONE


FieldValues = Union[None, str, bool, int]
RawEvent = Mapping[str, FieldValues]
RawQueryResponse = List[RawEvent]

URL = "https://t6ky1u2if62shkupuk.us-central1.gcp.squid.cloud/query/batchQueries"
HEADERS = {
    'content-type': 'application/json',
    'x-squid-clientid': '251798d9-6248-4b73-9c34-cc93be299472',
}
# This can probably be randomized
CLIENT_REQUEST_ID = "bac50ace-5928-4f88-b364-e69a3f84d3d4"
QUERY = [
  {
    "query": {
      "integrationId": "built_in_db",
      "collectionName": "events",
      "conditions": [
        {
          "fieldName": "datetime",
          "operator": ">",
          "value": "2025-01-21T05:00:27.557Z",
        },
      ],
      "limit": 60,
      "sortOrder": [
        {
          "asc": True,
          "fieldName": "datetime",
        },
      ],
    },
    "clientRequestId": CLIENT_REQUEST_ID,
    "subscribe": False,
  },
]


@varsnap
def initialize_chase_event(data: RawEvent) -> Event:
    event = Event()
    event.id = cast(Optional[str], data['uid'])
    event.title = cast(str, data['title'])
    event.slug = slugify(event.title)
    event.subtitle = cast(Optional[str], data['metaTitle'])
    event.date_string = cast(str, data['datetime'])
    date = datetime.datetime.fromisoformat(event.date_string)
    event.date = date.astimezone(tz=TIMEZONE)
    event.location_name = cast(Optional[str], data['location'])
    if event.location_name == 'home':
        event.location_name = 'Chase Center, San Francisco'
    event.duration = 3
    return event


def get_raw_events() -> RawQueryResponse:
    data = json.dumps(QUERY)
    response = requests.post(URL, headers=HEADERS, data=data)
    try:
        response.raise_for_status()
    except requests.HTTPError:
        rollbar.report_message('Chasecenter HTTP error', 'error')
        return []
    try:
        raw_response = response.json()
    except json.JSONDecodeError:
        rollbar.report_message('Cannot parse chasecenter json', 'error')
        return []
    try:
        raw_query_response = raw_response['results'][CLIENT_REQUEST_ID]['docs']
    except KeyError:
        rollbar.report_message('Received corrupt chasecenter json', 'error')
        return []
    return cast(RawQueryResponse, raw_query_response)


def get_events() -> List[Event]:
    events = cache.read_cache(cache.CACHED_CHASECENTER)
    if events:
        return events
    raw_events = get_raw_events()
    events = [initialize_chase_event(e) for e in raw_events]
    events = sorted(events, key=lambda e: e.date)
    events.sort()
    cache.save_cache(cache.CACHED_CHASECENTER, events)
    return events
