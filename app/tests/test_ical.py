from datetime import datetime, timezone
from unittest import TestCase
from unittest.mock import MagicMock, patch

from app import chasecenter, ical
from app.tests.test_chasecenter import EXAMPLE_RAW_EVENT


EXAMPLE_EVENT = chasecenter.initialize_chase_event(EXAMPLE_RAW_EVENT)


class TestGenerateCalendar(TestCase):
    def test_generate_empty(self) -> None:
        cal = ical.generate_calendar([], 'Chase Center')
        self.assertIn('Chase Center Events', cal)
        self.assertIn('BEGIN:VCALENDAR', cal)
        self.assertIn('END:VCALENDAR', cal)

    @patch('app.ical._get_modified')
    def test_generate(self, mock_modified: MagicMock) -> None:
        mock_modified.return_value = datetime(2025, 2, 2, 17, 48, tzinfo=timezone.utc)
        cal = ical.generate_calendar([EXAMPLE_EVENT], 'Chase Center')
        self.assertIn('DTSTART:20250123T030000Z', cal)
        self.assertIn('DTEND:20250123T060000Z', cal)
        self.assertIn('SUMMARY:Tame Impala', cal)
        self.assertIn('DESCRIPTION:example subtitle', cal)
        self.assertIn('LOCATION:Chase Center\\, San Francisco', cal)
        # https://stackoverflow.com/questions/60560457/google-doesnt-sync-my-subscribed-ics-feed
        self.assertIn('SEQUENCE:1738518480', cal)
        self.assertIn('DTSTAMP:20250202T174800Z', cal)
        self.assertIn('LAST-MODIFIED:20250202T174800Z', cal)
