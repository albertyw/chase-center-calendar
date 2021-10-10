import datetime
from unittest import TestCase

import pytz

from app import chasecenter, ical
from app.tests.test_chasecenter import EXAMPLE_RAW_EVENT


EXAMPLE_EVENT = chasecenter.initialize_chase_event(EXAMPLE_RAW_EVENT)


class TestGenerateCalendar(TestCase):
    def test_generate_empty(self) -> None:
        cal = ical.generate_calendar([])
        self.assertIn('Chase Center Events', cal)
        self.assertIn('BEGIN:VCALENDAR', cal)
        self.assertIn('END:VCALENDAR', cal)

    def test_generate(self) -> None:
        cal = ical.generate_calendar([EXAMPLE_EVENT])
        self.assertIn('DTSTART:20200916T023000Z', cal)
        self.assertIn('DTEND:20200916T053000Z', cal)
        self.assertIn('SUMMARY:Tame Impala', cal)
        self.assertIn('DESCRIPTION:example subtitle', cal)
        self.assertIn('LOCATION:Chase Center\\, San Francisco', cal)


class TestDateString(TestCase):
    def test_date_string(self) -> None:
        dt = datetime.datetime(1998, 1, 18, 7, 30, tzinfo=pytz.utc)
        formatted = ical.date_string(dt)
        self.assertEqual(formatted, '19980118T073000Z')

    def test_tz_date_string(self) -> None:
        tz = pytz.timezone('America/Los_Angeles')
        dt = datetime.datetime(1998, 1, 17, 23, 30)
        dt = tz.localize(dt)
        formatted = ical.date_string(dt)
        self.assertEqual(formatted, '19980118T073000Z')
