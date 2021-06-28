from datetime import datetime
from typing import List, Mapping, Optional, Union, cast

import requests


FieldValues = Union[None, str, bool, int]
RawEvent = Mapping[str, Mapping[str, FieldValues]]
RawQueryResponse = Mapping[str, Mapping[str, Mapping[str, List[RawEvent]]]]

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


class Event():
    def __init__(self, event_data: RawEvent) -> None:
        data = event_data['fields']
        self.id = cast(Optional[str], data['id'])
        self.slug = cast(Optional[str], data['slug'])
        self.title = cast(str, data['title'])
        self.subtitle = cast(Optional[str], data['subtitle'])
        self.date_string = cast(str, data['date'])
        self.date = datetime.fromisoformat(self.date_string)
        self.location_name = cast(Optional[str], data['locationName'])
        self.location_type = cast(Optional[str], data['locationType'])
        self.ticket_required = cast(bool, data['ticketRequired'])
        self.ticket_available = cast(bool, data['ticketAvailable'])
        self.ticket_sold_out = cast(bool, data['ticketSoldOut'])
        self.hide_road_game = cast(Optional[bool], data['hideRoadGame'])
        self.duration = cast(int, data['duration'])


def get_raw_events() -> RawQueryResponse:
    data = {
        'query': QUERY,
    }
    response = requests.post(URL, data=data)
    return cast(RawQueryResponse, response.json())


def get_events() -> List[Event]:
    raw_data = get_raw_events()
    raw_events = raw_data['data']['contentByType']['items']
    events = [Event(e) for e in raw_events]
    return events
