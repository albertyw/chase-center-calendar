from unittest import TestCase

from app import chasecenter, ical
from app.tests.test_chasecenter import EXAMPLE_RAW_EVENT


EXAMPLE_EVENT = chasecenter.Event(EXAMPLE_RAW_EVENT)


class TestGenerateCalendar(TestCase):
    def test_generate_empty(self) -> None:
        cal = str(ical.generate_calendar([]))
        self.assertIn('Chase Center Events', cal)
        self.assertIn('BEGIN:VCALENDAR', cal)
        self.assertIn('END:VCALENDAR', cal)
