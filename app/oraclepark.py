import copy
import csv
import datetime
from typing import List

from bs4 import BeautifulSoup
from dateutil import parser as dateutilparser
import requests
from slugify import slugify
from varsnap import varsnap

from app import cache
from app.event import Event, TIMEZONE


DOTHEBAY_URLS = [
    "https://dothebay.com/venues/oracle-park/events",
    "https://dothebay.com/venues/oracle-park/past_events",
]
TICKETING_URL = (
    "https://www.ticketing-client.com/ticketing-client/csv/GameTicketPromotionPrice.tiksrv?"
    "team_id=137&"
    "home_team_id=137&"
    "display_in=singlegame&"
    "ticket_category=Tickets&"
    "site_section=Default&"
    "sub_category=Default&"
    "leave_empty_games=true&"
    "event_type=T&"
    "year=%s&"
    "begin_date=%s0101"
)


def dothebay_get_raw_events(url: str) -> List[BeautifulSoup]:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    event_divs = soup.find_all('div', class_='ds-events-group')
    return event_divs


@varsnap
def dothebay_parse_event_div(event_div: BeautifulSoup) -> Event:
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


def ticketing_get_events() -> List[Event]:
    events: List[Event] = []
    year = datetime.datetime.now().year
    url = TICKETING_URL % (year, year)
    response = requests.get(url)
    reader = csv.DictReader(response.content.decode('utf-8').splitlines())
    for row in reader:
        event = Event()
        event.title = row['SUBJECT']
        event.slug = slugify(event.title)
        event.subtitle = row['DESCRIPTION']
        start_time = dateutilparser.parse(row['START DATE'] + ' ' + row['START TIME'])
        end_time = dateutilparser.parse(row['END DATE'] + ' ' + row['END TIME'])
        duration = round((end_time - start_time).seconds / 60 / 60)
        event.date = start_time
        event.date_string = event.date.isoformat()
        event.id = event.slug + event.date_string
        event.location_name = row['LOCATION']
        event.location_type = ''
        event.ticket_required = True
        event.ticket_available = True
        event.ticket_sold_out = False
        event.hide_road_game = False
        event.duration = duration
        if 'Oracle Park' not in event.location_name:
            continue
        events.append(event)
    return events


def deduplicate_events(
    ticketing_events: List[Event],
    dothebay_events: List[Event],
) -> List[Event]:
    events: List[Event] = copy.copy(ticketing_events)
    for dothebay_event in dothebay_events:
        for ticketing_event in ticketing_events:
            if ticketing_event.date.year != dothebay_event.date.year:
                events.append(dothebay_event)
                break
            if ticketing_event.date.month != dothebay_event.date.month:
                events.append(dothebay_event)
                break
            if ticketing_event.date.day != dothebay_event.date.day:
                events.append(dothebay_event)
                break
            other = ticketing_event.title.split(' at ')[0]
            if other not in dothebay_event.title:
                events.append(dothebay_event)
                break
    return events


def get_events() -> List[Event]:
    events = cache.read_cache(cache.CACHED_ORACLEPARK)
    if events:
        return events
    events = []
    event_ids: List[str] = []
    for url in DOTHEBAY_URLS:
        event_divs = dothebay_get_raw_events(url)
        for event_div in event_divs:
            event = dothebay_parse_event_div(event_div)
            if event.id in event_ids:
                continue
            events.append(event)
            event_ids.append(event.id)
    ticketing_events = ticketing_get_events()
    events = deduplicate_events(ticketing_events, events)
    cache.save_cache(cache.CACHED_ORACLEPARK, events)
    return events
