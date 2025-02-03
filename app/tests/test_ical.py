from datetime import datetime, timezone
from unittest import TestCase
from unittest.mock import patch
from zoneinfo import ZoneInfo

from app import chasecenter, ical
from app.tests.test_chasecenter import EXAMPLE_RAW_EVENT


EXAMPLE_EVENT = chasecenter.initialize_chase_event(EXAMPLE_RAW_EVENT)
TZ = ZoneInfo('America/Los_Angeles')


class TestGenerateCalendar(TestCase):
    def test_generate_empty(self) -> None:
        cal = ical.generate_calendar([], 'Chase Center')
        self.assertIn('Chase Center Events', cal)
        self.assertIn('BEGIN:VCALENDAR', cal)
        self.assertIn('END:VCALENDAR', cal)

    @patch('datetime.datetime')
    def test_generate(self, mock_now) -> None:
        mock_now.now.return_value = datetime(2025, 2, 2, 17, 48, tzinfo=TZ)
        cal = ical.generate_calendar([EXAMPLE_EVENT], 'Chase Center')
        self.assertIn('DTSTART:20250123T030000Z', cal)
        self.assertIn('DTEND:20250123T060000Z', cal)
        self.assertIn('SUMMARY:Tame Impala', cal)
        self.assertIn('DESCRIPTION:example subtitle', cal)
        self.assertIn('LOCATION:Chase Center\\, San Francisco', cal)
        # https://stackoverflow.com/questions/60560457/google-doesnt-sync-my-subscribed-ics-feed
        self.assertIn('SEQUENCE:1738547280', cal)
        self.assertIn('LAST-MODIFIED:20250203T014800Z', cal)


class TestDateString(TestCase):
    def test_date_string(self) -> None:
        dt = datetime(1998, 1, 18, 7, 30, tzinfo=timezone.utc)
        formatted = ical.date_string(dt)
        self.assertEqual(formatted, '19980118T073000Z')

    def test_tz_date_string(self) -> None:
        dt = datetime(1998, 1, 17, 23, 30).replace(tzinfo=TZ)
        formatted = ical.date_string(dt)
        self.assertEqual(formatted, '19980118T073000Z')
