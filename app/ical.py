from typing import List

from icalendar import Calendar

from app import chasecenter


def generate_calendar(events: List[chasecenter.Event]) -> str:
    cal = Calendar()
    cal['summary'] = 'Chase Center Events'
    return str(cal.to_ical().decode('utf-8'))
