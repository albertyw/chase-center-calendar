from datetime import datetime
from unittest import TestCase

from app import chasecenter


EXAMPLE_RAW_EVENT = {
    "fields": {
        "id": "example id",
        "slug": None,
        "title": "Tame Impala",
        "subtitle": "example subtitle",
        "date": "2020-09-15T19:30",
        "locationName": "Chase Center, San Francisco",
        "locationType": "arena",
        "ticketRequired": True,
        "ticketAvailable": True,
        "ticketSoldOut": False,
        "hideRoadGame": None,
        "duration": 3,
    }
}


class TestEvent(TestCase):
    def test_init(self) -> None:
        event = chasecenter.Event(EXAMPLE_RAW_EVENT)
        data = EXAMPLE_RAW_EVENT['fields']
        self.assertEqual(event.id, data['id'])
        self.assertEqual(event.slug, data['slug'])
        self.assertEqual(event.title, data['title'])
        self.assertEqual(event.subtitle, data['subtitle'])
        self.assertEqual(event.date_string, data['date'])
        expected = chasecenter.TIMEZONE.localize(datetime(2020, 9, 15, 19, 30))
        self.assertEqual(event.date, expected)
        self.assertEqual(event.location_name, data['locationName'])
        self.assertEqual(event.location_type, data['locationType'])
        self.assertEqual(event.ticket_required, data['ticketRequired'])
        self.assertEqual(event.ticket_available, data['ticketAvailable'])
        self.assertEqual(event.ticket_sold_out, data['ticketSoldOut'])
        self.assertEqual(event.hide_road_game, False)
        self.assertEqual(event.duration, data['duration'])

    def test_show(self) -> None:
        event = chasecenter.Event(EXAMPLE_RAW_EVENT)
        event.date = datetime(3000, 1, 1, tzinfo=chasecenter.TIMEZONE)
        self.assertTrue(event.show)
        event.date = datetime(1000, 1, 1, tzinfo=chasecenter.TIMEZONE)
        self.assertFalse(event.show)
        event.date = datetime(3000, 1, 1, tzinfo=chasecenter.TIMEZONE)
        event.hide_road_game = True
        self.assertFalse(event.show)

    def test_end(self) -> None:
        event = chasecenter.Event(EXAMPLE_RAW_EVENT)
        expected = chasecenter.TIMEZONE.localize(datetime(2020, 9, 15, 22, 30))
        self.assertEqual(event.end, expected)


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
