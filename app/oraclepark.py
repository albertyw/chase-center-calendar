import datetime
from typing import cast, List, Optional

from bs4 import BeautifulSoup
from dateutil import parser as dateutilparser
import requests

from app.event import Event, TIMEZONE


URL = "https://dothebay.com/venues/oracle-park/events"


def get_raw_events() -> List[BeautifulSoup]:
    response = requests.get(URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    event_divs = soup.find_all('div', class_='ds-events-group')
    return event_divs


def parse_event_div(event_div: BeautifulSoup) -> Event:
    event = Event()
    event.id = cast(Optional[str], event_div.find_all('a', class_='ds-btn-ical')[0]['data-ds-id'])
    event.title = cast(str, event_div.find_all('span', attrs={'itemprop': 'name'})[0].get_text())
    event.slug = cast(Optional[str], event.title)
    event.subtitle = cast(Optional[str], event.title)
    event.date_string = cast(str, event_div.find_all('meta', attrs={'itemprop': 'startDate'})[0]['datetime'])
    date = dateutilparser.isoparse(event.date_string)
    event.date = date.astimezone(TIMEZONE)
    event.date_string = event.date.isoformat()
    location = event_div.find_all('div', attrs={'itemprop': 'location'})[0]
    event.location_name = cast(Optional[str], location.find_all('span', attrs={'itemprop': 'name'})[0].get_text())
    event.location_type = ''
    event.ticket_required = True
    event.ticket_available = True
    event.ticket_sold_out = False
    event.hide_road_game = False
    event.duration = 4
    return event


def get_events() -> List[Event]:
    event_divs = get_raw_events()
    events: List[Event] = []
    for event_div in event_divs:
        event = parse_event_div(event_div)
        events.append(event)
    print(events[0].__dict__)
    return events


if __name__ == '__main__':
    get_events()
