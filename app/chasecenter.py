from typing import List, Mapping, Optional, Union, cast

import requests


FieldValues = Union[Optional[str], str, Optional[bool], bool, float]
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


def get_raw_events() -> RawQueryResponse:
    data = {
        'query': QUERY,
    }
    response = requests.post(URL, data=data)
    return cast(RawQueryResponse, response.json())
