import datetime
from typing import List

from icalendar import Calendar, Event
import pytz

from app import chasecenter


def generate_calendar(events: List[chasecenter.Event]) -> str:
    cal = Calendar()
    cal['summary'] = 'Chase Center Events'
    for event in events:
        cal_event = generate_calendar_event(event)
        cal.add_component(cal_event)
    return str(cal.to_ical().decode('utf-8'))


def generate_calendar_event(event: chasecenter.Event) -> Event:
    cal_event = Event()
    cal_event['uid'] = event.id
    cal_event['dtstart'] = date_string(event.date)
    cal_event['location'] = event.location_name
    cal_event['summary'] = event.title
    cal_event['description'] = event.subtitle
    return cal_event


def date_string(dt: datetime.datetime) -> str:
    utc = dt.astimezone(pytz.utc).replace(tzinfo=None)
    formatted = utc.isoformat()
    formatted = formatted.replace('-', '')
    formatted = formatted.replace(':', '')
    formatted += 'Z'
    return formatted
