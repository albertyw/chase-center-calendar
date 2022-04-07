from typing import List

from bs4 import BeautifulSoup
from dateutil import parser as dateutilparser
import requests
from slugify import slugify
from varsnap import varsnap

from app import cache
from app.event import Event, TIMEZONE


URLS = [
    "https://dothebay.com/venues/oracle-park/events",
    "https://dothebay.com/venues/oracle-park/past_events",
]


def get_raw_events(url: str) -> List[BeautifulSoup]:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    event_divs = soup.find_all('div', class_='ds-events-group')
    return event_divs


@varsnap
def parse_event_div(event_div: BeautifulSoup) -> Event:
    event = Event()
    event.title = event_div.find_all(
        'span',
        class_='ds-listing-event-title-text',
    )[0].get_text()
    event.slug = slugify(event.title)
    event.subtitle = ''
    date_string = event_div.find_all(
        'meta',
        attrs={'itemprop': 'startDate'},
    )[0]['datetime']
    date = dateutilparser.isoparse(date_string)
    event.date = date.astimezone(TIMEZONE)
    event.date_string = event.date.isoformat()
    try:
        anchor = event_div.find_all('a', class_='ds-btn-ical')
        event.id = anchor[0]['data-ds-id']
    except IndexError:
        event.id = event.slug + event.date_string
    location = event_div.find_all('div', attrs={'itemprop': 'location'})[0]
    event.location_name = location.find_all(
        'span',
        attrs={'itemprop': 'name'},
    )[0].get_text()
    event.location_type = ''
    event.ticket_required = True
    event.ticket_available = True
    event.ticket_sold_out = False
    event.hide_road_game = False
    event.duration = 4
    return event


def get_events() -> List[Event]:
    events = cache.read_cache('oraclepark')
    if events:
        return events
    events = []
    event_ids: List[str] = []
    for url in URLS:
        event_divs = get_raw_events(url)
        for event_div in event_divs:
            event = parse_event_div(event_div)
            if event.id in event_ids:
                continue
            events.append(event)
            event_ids.append(event.id)
    cache.save_cache('oraclepark', events)
    return events
