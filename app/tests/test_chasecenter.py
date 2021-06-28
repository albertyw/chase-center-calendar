from datetime import datetime
from unittest import TestCase

from app import chasecenter


class TestGetRawEvents(TestCase):
    def test_get_events(self) -> None:
        events = chasecenter.get_raw_events()
        self.assertIn('data', events)
        self.assertIn('contentByType', events['data'])
        self.assertIn('items', events['data']['contentByType'])
        self.assertTrue(len(events['data']['contentByType']['items']) > 0)


class TestGetEvents(TestCase):
    def test_get_events(self) -> None:
        events = chasecenter.get_events()
        self.assertTrue(len(events) > 0)
        event = events[0]
        self.assertTrue(isinstance(event.title, str))
        self.assertTrue(isinstance(event.date_string, str))
        self.assertTrue(isinstance(event.date, datetime))
        self.assertTrue(isinstance(event.ticket_required, bool))
        self.assertTrue(isinstance(event.ticket_available, bool))
        self.assertTrue(isinstance(event.ticket_sold_out, bool))
        self.assertTrue(isinstance(event.duration, int))
