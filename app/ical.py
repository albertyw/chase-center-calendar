import datetime
from typing import List

from icalendar import Calendar, Event
from varsnap import varsnap

from app import event


@varsnap
def generate_calendar(events: List[event.Event]) -> str:
    cal = Calendar()
    cal['summary'] = 'Chase Center Events'
    cal['version'] = '2.0'
    cal['prodid'] = '-//Albertyw.com//Chase Center Calendar//EN'
    cal['x-wr-calname'] = 'Chase Center Events'
    cal['x-wr-caldesc'] = 'Events at the SF Chase Center'
    cal['timezone'] = 'America/Los_Angeles'
    cal['x-wr-timezone'] = 'America/Los_Angeles'
    cal['x-published-ttl'] = 'PT1H'
    cal['refresh-interval'] = 'VALUE=DURATION:PT1H'
    for e in events:
        cal_event = generate_calendar_event(e)
        cal.add_component(cal_event)
    return str(cal.to_ical().decode('utf-8'))


@varsnap
def generate_calendar_event(event: event.Event) -> Event:
    cal_event = Event()
    cal_event['uid'] = event.id
    cal_event['dtstart'] = date_string(event.date)
    cal_event['dtend'] = date_string(event.end)
    cal_event['location'] = event.location_name
    cal_event['summary'] = event.title
    cal_event['description'] = event.subtitle
    cal_event['sequence'] = int(datetime.datetime.now().timestamp())
    cal_event['last-modified'] = date_string(datetime.datetime.now())
    return cal_event


@varsnap
def date_string(dt: datetime.datetime) -> str:
    utc = dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
    utc = utc.replace(microsecond=0)
    formatted = utc.isoformat()
    formatted = formatted.replace('-', '')
    formatted = formatted.replace(':', '')
    formatted += 'Z'
    return formatted
