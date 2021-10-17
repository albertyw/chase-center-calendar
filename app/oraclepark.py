import datetime
import random
from typing import List

from bs4 import BeautifulSoup
from dateutil import parser as dateutilparser
import requests
from slugify import slugify
from varsnap import varsnap

from app.event import Event, TIMEZONE


URL = "https://dothebay.com/venues/oracle-park/events"


def get_raw_events() -> List[BeautifulSoup]:
    response = requests.get(URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    event_divs = soup.find_all('div', class_='ds-events-group')
    return event_divs


@varsnap
def parse_event_div(event_div: BeautifulSoup) -> Event:
    event = Event()
    event.id = event_div.find_all('a', class_='ds-btn-ical')[0]['data-ds-id']
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


CachedEvents: List[Event] = []
CachedEventsExpire = datetime.datetime.now()


def get_events() -> List[Event]:
    global CachedEvents, CachedEventsExpire
    if CachedEvents and CachedEventsExpire > datetime.datetime.now():
        return CachedEvents
    event_divs = get_raw_events()
    events: List[Event] = []
    for event_div in event_divs:
        event = parse_event_div(event_div)
        events.append(event)
    _refresh_cache(events)
    return events


def _refresh_cache(events: List[Event]) -> None:
    global CachedEvents, CachedEventsExpire
    CachedEvents = events
    cache_duration = datetime.timedelta(minutes=random.randint(30, 90))
    CachedEventsExpire = datetime.datetime.now() + cache_duration
