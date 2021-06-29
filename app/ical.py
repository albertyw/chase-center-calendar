import datetime
from typing import List

from icalendar import Calendar
import pytz

from app import chasecenter


def generate_calendar(events: List[chasecenter.Event]) -> str:
    cal = Calendar()
    cal['summary'] = 'Chase Center Events'
    return str(cal.to_ical().decode('utf-8'))


def date_string(dt: datetime.datetime) -> str:
    utc = dt.astimezone(pytz.utc).replace(tzinfo=None)
    formatted = utc.isoformat()
    formatted = formatted.replace('-', '')
    formatted = formatted.replace(':', '')
    formatted += 'Z'
    return formatted
