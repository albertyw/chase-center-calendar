from datetime import datetime, timedelta
import json
from unittest import TestCase
from unittest.mock import MagicMock, patch

from app import chasecenter
from app.event import TIMEZONE


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
        event = chasecenter.initialize_chase_event(EXAMPLE_RAW_EVENT)
        data = EXAMPLE_RAW_EVENT['fields']
        self.assertEqual(event.id, data['id'])
        self.assertEqual(event.slug, data['slug'])
        self.assertEqual(event.title, data['title'])
        self.assertEqual(event.subtitle, data['subtitle'])
        self.assertEqual(event.date_string, data['date'])
        expected = datetime(2020, 9, 15, 19, 30).replace(tzinfo=TIMEZONE)
        self.assertEqual(event.date, expected)
        self.assertEqual(event.location_name, data['locationName'])
        self.assertEqual(event.location_type, data['locationType'])
        self.assertEqual(event.ticket_required, data['ticketRequired'])
        self.assertEqual(event.ticket_available, data['ticketAvailable'])
        self.assertEqual(event.ticket_sold_out, data['ticketSoldOut'])
        self.assertEqual(event.hide_road_game, False)
        self.assertEqual(event.duration, data['duration'])

    def test_show(self) -> None:
        event = chasecenter.initialize_chase_event(EXAMPLE_RAW_EVENT)
        self.assertTrue(event.show)
        event.hide_road_game = True
        self.assertFalse(event.show)

    def test_is_future(self) -> None:
        event = chasecenter.initialize_chase_event(EXAMPLE_RAW_EVENT)
        event.date = datetime(3000, 1, 1, tzinfo=TIMEZONE)
        self.assertTrue(event.is_future)
        event.date = datetime(1000, 1, 1, tzinfo=TIMEZONE)
        self.assertFalse(event.is_future)

    def test_end(self) -> None:
        event = chasecenter.initialize_chase_event(EXAMPLE_RAW_EVENT)
        expected = datetime(2020, 9, 15, 22, 30).replace(tzinfo=TIMEZONE)
        self.assertEqual(event.end, expected)


class TestGetRawEvents(TestCase):
    def test_get_events(self) -> None:
        events = chasecenter.get_raw_events()
        self.assertTrue(len(events) > 0)

    @patch('requests.post')
    def test_get_events_no_json(self, mock_post: MagicMock) -> None:
        mock_post.json.side_effect = json.JSONDecodeError
        events = chasecenter.get_raw_events()
        self.assertEqual(len(events), 0)

    @patch('requests.post')
    def test_get_events_corrupt_json(self, mock_post: MagicMock) -> None:
        mock_post.json.return_value = {'asdf': 'qwer'}
        events = chasecenter.get_raw_events()
        self.assertEqual(len(events), 0)


class TestGetEvents(TestCase):
    def setUp(self) -> None:
        chasecenter.CachedEvents = []
        chasecenter.CachedEventsExpire = datetime.now()

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

    @patch('app.chasecenter.get_raw_events')
    def test_get_cached_events(self, mock_get_raw_events: MagicMock) -> None:
        event = chasecenter.initialize_chase_event(EXAMPLE_RAW_EVENT)
        chasecenter.CachedEvents = [event]
        chasecenter.CachedEventsExpire += timedelta(days=1)
        events = chasecenter.get_events()
        self.assertEqual(events, [event])
        self.assertEqual(chasecenter.CachedEvents, [event])
        self.assertFalse(mock_get_raw_events.called)

    @patch('app.chasecenter.get_raw_events')
    def test_caches_events(self, mock_get_raw_events: MagicMock) -> None:
        mock_get_raw_events.return_value = [EXAMPLE_RAW_EVENT]
        events_1 = chasecenter.get_events()
        self.assertTrue(mock_get_raw_events.called)
        mock_get_raw_events.reset_mock()
        events_2 = chasecenter.get_events()
        self.assertFalse(mock_get_raw_events.called)
        self.assertEqual(events_1, events_2)
