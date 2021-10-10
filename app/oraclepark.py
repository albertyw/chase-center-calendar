from typing import Any, List

import requests

from app.event import Event


URL = "https://dothebay.com/venues/oracle-park/events"


def get_raw_events() -> Any:
    response = requests.get(URL)
    print(response.content)
    return response.content


def get_events() -> List[Event]:
    get_raw_events()
    return []


if __name__ == '__main__':
    get_raw_events()
