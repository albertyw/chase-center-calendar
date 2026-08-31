import datetime
from typing import List, cast

from icalendar import Calendar, Event, vDatetime
from varsnap import varsnap

from app import event


# datetime.now() is not deterministic, so cannot use varsnap
# @varsnap
def generate_calendar(events: List[event.Event], location: str) -> bytes:
    modified = _get_modified()
    cal = Calendar()
    cal['summary'] = '%s Events' % location
    cal['version'] = '2.0'
    cal['prodid'] = '-//ChaseCenterCalendar.com//%s Calendar//EN' % location
    cal['x-wr-calname'] = '%s Events' % location
    cal['x-wr-caldesc'] = 'Events at the SF %s' % location
    cal['timezone'] = 'America/Los_Angeles'
    cal['x-wr-timezone'] = 'America/Los_Angeles'
    cal['x-published-ttl'] = 'PT1H'
    cal['refresh-interval'] = 'VALUE=DURATION:PT1H'
    for e in events:
        cal_event = generate_calendar_event(e, modified)
        cal.add_component(cal_event)
    return cast(bytes, cal.to_ical())


@varsnap
def generate_calendar_event(event: event.Event, modified: datetime.datetime) -> Event:
    cal_event = Event()
    cal_event['uid'] = event.id
    cal_event['dtstart'] = vDatetime(event.date.astimezone(datetime.timezone.utc))
    cal_event['dtend'] = vDatetime(event.end.astimezone(datetime.timezone.utc))
    cal_event['location'] = event.location_name
    cal_event['summary'] = event.title
    cal_event['description'] = event.subtitle
    cal_event['sequence'] = int(modified.timestamp())
    cal_event['dtstamp'] = vDatetime(modified)
    cal_event['last-modified'] = vDatetime(modified)
    return cal_event


def _get_modified() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)
