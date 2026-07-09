import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import requests
import tempfile
from unittest import TestCase, skip
from unittest.mock import MagicMock, patch

from app import cache, chasecenter
from app.event import TIMEZONE


EXAMPLE_RAW_EVENT: chasecenter.RawEvent = {
    "uid": "example id",
    "title": "Tame Impala",
    "metaTitle": "example subtitle",
    "datetime": "2025-01-23T03:00:00Z",
    "location": "Chase Center, San Francisco",
}


class TestEvent(TestCase):
    def test_init(self) -> None:
        event = chasecenter.initialize_chase_event(EXAMPLE_RAW_EVENT)
        data = EXAMPLE_RAW_EVENT
        self.assertEqual(event.id, data['uid'])
        self.assertEqual(event.title, data['title'])
        self.assertEqual(event.subtitle, data['metaTitle'])
        self.assertEqual(event.date_string, data['datetime'])
        expected = datetime(2025, 1, 22, 19, 0).replace(tzinfo=TIMEZONE)
        self.assertEqual(event.date, expected)
        self.assertEqual(event.location_name, data['location'])

    def test_is_future(self) -> None:
        event = chasecenter.initialize_chase_event(EXAMPLE_RAW_EVENT)
        event.date = datetime(3000, 1, 1, tzinfo=TIMEZONE)
        self.assertTrue(event.is_future)
        event.date = datetime(1000, 1, 1, tzinfo=TIMEZONE)
        self.assertFalse(event.is_future)

    def test_end(self) -> None:
        event = chasecenter.initialize_chase_event(EXAMPLE_RAW_EVENT)
        expected = datetime(2025, 1, 22, 22,0).replace(tzinfo=TIMEZONE)
        self.assertEqual(event.end, expected)


class TestGetRawEvents(TestCase):
    def setUp(self) -> None:
        self.mock_rollbar = MagicMock()
        self.original_rollbar = chasecenter.rollbar  # type: ignore[attr-defined]
        chasecenter.rollbar = self.mock_rollbar  # type: ignore[attr-defined]

    def tearDown(self) -> None:
        chasecenter.rollbar = self.original_rollbar  # type: ignore[attr-defined]

    @skip("Requires network access")
    def test_get_events(self) -> None:
        events = chasecenter.get_raw_events()
        self.assertGreater(len(events), 0)

    @patch('requests.post')
    def test_get_events_mock(self, mock_post: MagicMock) -> None:
        raw_event = {
            'results': {
                chasecenter.CLIENT_REQUEST_ID: {
                    'docs': [EXAMPLE_RAW_EVENT],
                },
            },
        }
        mock_post().json.return_value = raw_event
        events = chasecenter.get_raw_events()
        self.assertGreater(len(events), 0)

    @patch('requests.post')
    def test_get_events_http_error(self, mock_post: MagicMock) -> None:
        mock_post().raise_for_status.side_effect = requests.HTTPError()
        events = chasecenter.get_raw_events()
        self.assertEqual(len(events), 0)

    @patch('requests.post')
    def test_get_events_no_json(self, mock_post: MagicMock) -> None:
        mock_post().json.side_effect = json.JSONDecodeError("", "", 0)
        events = chasecenter.get_raw_events()
        self.assertEqual(len(events), 0)

    @patch('requests.post')
    def test_get_events_corrupt_json(self, mock_post: MagicMock) -> None:
        mock_post().json.return_value = {'asdf': 'qwer'}
        events = chasecenter.get_raw_events()
        self.assertEqual(len(events), 0)


def build_raw_event(uid: str, dt: str) -> chasecenter.RawEvent:
    event = copy.deepcopy(EXAMPLE_RAW_EVENT)
    event['uid'] = uid  # type: ignore
    event['datetime'] = dt  # type: ignore
    return event


def build_page_response(events: list[chasecenter.RawEvent]) -> dict[str, object]:
    return {
        'results': {
            chasecenter.CLIENT_REQUEST_ID: {'docs': events},
        },
    }


class TestGetRawEventsPagination(TestCase):
    """get_raw_events pages until a short page, deduping across boundaries."""

    def setUp(self) -> None:
        self.mock_rollbar = MagicMock()
        self.original_rollbar = chasecenter.rollbar  # type: ignore[attr-defined]
        chasecenter.rollbar = self.mock_rollbar  # type: ignore[attr-defined]

    def tearDown(self) -> None:
        chasecenter.rollbar = self.original_rollbar  # type: ignore[attr-defined]

    def full_page(self, start: int) -> list[chasecenter.RawEvent]:
        return [
            build_raw_event(f'id{i}', f'2025-01-23T03:00:{i:02d}Z')
            for i in range(start, start + chasecenter.PAGE_SIZE)
        ]

    @patch('requests.post')
    def test_single_short_page_does_not_paginate(
        self, mock_post: MagicMock,
    ) -> None:
        mock_post().json.return_value = build_page_response([EXAMPLE_RAW_EVENT])
        mock_post.reset_mock()
        events = chasecenter.get_raw_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(mock_post.call_count, 1)

    @patch('requests.post')
    def test_reads_more_than_one_page(self, mock_post: MagicMock) -> None:
        page_1 = self.full_page(0)
        page_2 = [build_raw_event('tail', '2025-01-23T04:00:00Z')]
        mock_post().json.side_effect = [
            build_page_response(page_1),
            build_page_response(page_2),
        ]
        events = chasecenter.get_raw_events()
        self.assertEqual(len(events), chasecenter.PAGE_SIZE + 1)
        self.assertEqual(events[-1]['uid'], 'tail')

    @patch('requests.post')
    def test_full_final_page_stops_on_empty_page(
        self, mock_post: MagicMock,
    ) -> None:
        mock_post().json.side_effect = [
            build_page_response(self.full_page(0)),
            build_page_response([]),
        ]
        events = chasecenter.get_raw_events()
        self.assertEqual(len(events), chasecenter.PAGE_SIZE)

    @patch('requests.post')
    def test_does_not_duplicate_boundary_event(
        self, mock_post: MagicMock,
    ) -> None:
        page_1 = self.full_page(0)
        page_2 = [page_1[-1], build_raw_event('tail', '2025-01-23T04:00:00Z')]
        mock_post().json.side_effect = [
            build_page_response(page_1),
            build_page_response(page_2),
        ]
        events = chasecenter.get_raw_events()
        uids = [e['uid'] for e in events]
        self.assertEqual(len(uids), len(set(uids)))
        self.assertEqual(len(events), chasecenter.PAGE_SIZE + 1)

    @patch('requests.post')
    def test_stalled_pagination_breaks(self, mock_post: MagicMock) -> None:
        """A repeated full page must not loop forever."""
        page = self.full_page(0)
        mock_post().json.side_effect = [
            build_page_response(page),
            build_page_response(page),
        ]
        events = chasecenter.get_raw_events()
        self.assertEqual(len(events), chasecenter.PAGE_SIZE)
        self.assertTrue(self.mock_rollbar.report_message.called)

    @patch('requests.post')
    def test_advances_cutoff_to_last_event_datetime(
        self, mock_post: MagicMock,
    ) -> None:
        page_1 = self.full_page(0)
        mock_post().json.side_effect = [
            build_page_response(page_1),
            build_page_response([]),
        ]
        mock_post.reset_mock()
        chasecenter.get_raw_events()
        second_query = json.loads(mock_post.call_args_list[1].kwargs['data'])
        value = second_query[0]['query']['conditions'][0]['value']
        expected = datetime.fromisoformat('2025-01-23T03:00:59Z').isoformat()
        self.assertEqual(value, expected)


def to_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


class FakeBackend:
    """Serves a fixed dataset honoring the cutoff operator and limit."""

    def __init__(self, events: list[chasecenter.RawEvent]) -> None:
        self.events = sorted(events, key=lambda e: to_utc(str(e['datetime'])))
        self.call_count = 0

    def post(self, url: str, headers: object, data: str) -> MagicMock:
        self.call_count += 1
        if self.call_count > 20:
            raise AssertionError('get_raw_events did not terminate')
        condition = json.loads(data)[0]['query']['conditions'][0]
        limit = json.loads(data)[0]['query']['limit']
        cutoff = to_utc(condition['value'])
        operator = condition['operator']

        def matches(event: chasecenter.RawEvent) -> bool:
            event_dt = to_utc(str(event['datetime']))
            if operator == '>=':
                return event_dt >= cutoff
            return event_dt > cutoff

        docs = [e for e in self.events if matches(e)][:limit]
        response = MagicMock()
        response.json.return_value = build_page_response(docs)
        return response


class TestGetRawEventsAgainstFakeBackend(TestCase):
    """End-to-end pagination against a backend that respects the query."""

    def setUp(self) -> None:
        self.mock_rollbar = MagicMock()
        self.original_rollbar = chasecenter.rollbar  # type: ignore[attr-defined]
        chasecenter.rollbar = self.mock_rollbar  # type: ignore[attr-defined]

    def tearDown(self) -> None:
        chasecenter.rollbar = self.original_rollbar  # type: ignore[attr-defined]

    def run_backend(
        self, events: list[chasecenter.RawEvent],
    ) -> list[chasecenter.RawEvent]:
        backend = FakeBackend(events)
        with patch('requests.post', side_effect=backend.post):
            return chasecenter.get_raw_events()

    def test_returns_every_event_exactly_once(self) -> None:
        events = [
            build_raw_event(f'id{i}', f'3000-01-01T00:{i // 60:02d}:{i % 60:02d}Z')
            for i in range(chasecenter.PAGE_SIZE * 2 + 5)
        ]
        result = self.run_backend(events)
        uids = [e['uid'] for e in result]
        self.assertEqual(sorted(uids), sorted(e['uid'] for e in events))
        self.assertEqual(len(uids), len(set(uids)))

    def test_event_sharing_page_boundary_datetime_is_not_skipped(self) -> None:
        """Two events at the page-boundary datetime must both be returned."""
        events = [
            build_raw_event(f'id{i}', f'3000-01-01T00:00:{i:02d}Z')
            for i in range(chasecenter.PAGE_SIZE - 1)
        ]
        boundary = f'3000-01-01T00:00:{chasecenter.PAGE_SIZE - 1:02d}Z'
        events.append(build_raw_event('boundary_a', boundary))
        events.append(build_raw_event('boundary_b', boundary))
        events.append(build_raw_event('tail', '3000-01-01T01:00:00Z'))
        result = self.run_backend(events)
        uids = [e['uid'] for e in result]
        self.assertIn('boundary_a', uids)
        self.assertIn('boundary_b', uids)
        self.assertIn('tail', uids)
        self.assertEqual(len(uids), len(set(uids)))

    def test_single_short_page(self) -> None:
        result = self.run_backend([build_raw_event('only', '3000-01-01T00:00:00Z')])
        self.assertEqual([e['uid'] for e in result], ['only'])

    def test_exactly_one_full_page(self) -> None:
        events = [
            build_raw_event(f'id{i}', f'3000-01-01T00:00:{i:02d}Z')
            for i in range(chasecenter.PAGE_SIZE)
        ]
        result = self.run_backend(events)
        self.assertEqual(len(result), chasecenter.PAGE_SIZE)

    def test_full_page_of_identical_datetimes_terminates(self) -> None:
        """A page that cannot advance the cutoff must not loop forever."""
        events = [
            build_raw_event(f'id{i}', '3000-01-01T00:00:00Z')
            for i in range(chasecenter.PAGE_SIZE + 5)
        ]
        result = self.run_backend(events)
        self.assertEqual(len(result), chasecenter.PAGE_SIZE)
        self.assertTrue(self.mock_rollbar.report_message.called)


class TestBuildQuery(TestCase):
    def test_defaults_to_seven_days_ago(self) -> None:
        query = chasecenter.build_query(None)
        value = query[0]['query']['conditions'][0]['value']  # type: ignore
        cutoff = datetime.fromisoformat(value)
        delta = datetime.now() - cutoff
        self.assertAlmostEqual(delta.total_seconds(), 7 * 86400, delta=60)

    def test_uses_supplied_cutoff(self) -> None:
        cutoff = datetime(2025, 5, 1, 12, 0)
        query = chasecenter.build_query(cutoff)
        value = query[0]['query']['conditions'][0]['value']  # type: ignore
        self.assertEqual(value, cutoff.isoformat())

    def test_does_not_mutate_module_query(self) -> None:
        chasecenter.build_query(datetime(2025, 5, 1, 12, 0))
        value = chasecenter.QUERY[0]['query']['conditions'][0]['value']  # type: ignore
        self.assertEqual(value, 'TODO')

    def test_cutoff_is_inclusive(self) -> None:
        query = chasecenter.build_query(None)
        operator = query[0]['query']['conditions'][0]['operator']  # type: ignore
        self.assertEqual(operator, '>=')


class TestGetEvents(TestCase):
    def setUp(self) -> None:
        self.mock_file = tempfile.NamedTemporaryFile()

    def tearDown(self) -> None:
        self.mock_file.close()

    @patch('app.chasecenter.get_raw_events')
    @patch('app.cache.get_cache_file')
    def test_get_events(
        self,
        mock_file: MagicMock,
        mock_get_raw_events: MagicMock,
    ) -> None:
        mock_get_raw_events.return_value = [EXAMPLE_RAW_EVENT]
        mock_file.return_value = Path(self.mock_file.name)
        events = chasecenter.get_events()
        self.assertGreater(len(events), 0)
        event = events[0]
        self.assertTrue(isinstance(event.title, str))
        self.assertTrue(isinstance(event.date_string, str))
        self.assertTrue(isinstance(event.date, datetime))
        self.assertTrue(isinstance(event.duration, int))

    @patch('app.chasecenter.get_raw_events')
    @patch('app.cache.get_cache_file')
    def test_get_cached_events(
        self,
        mock_file: MagicMock,
        mock_get_raw_events: MagicMock,
    ) -> None:
        mock_file.return_value = Path(self.mock_file.name)
        event = chasecenter.initialize_chase_event(EXAMPLE_RAW_EVENT)
        cache.save_cache(cache.CACHED_CHASECENTER, [event])
        events = chasecenter.get_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].id, event.id)
        self.assertFalse(mock_get_raw_events.called)

    @patch('app.chasecenter.get_raw_events')
    @patch('app.cache.get_cache_file')
    def test_caches_events(
        self,
        mock_file: MagicMock,
        mock_get_raw_events: MagicMock,
    ) -> None:
        mock_file.return_value = Path(self.mock_file.name)
        mock_get_raw_events.return_value = [EXAMPLE_RAW_EVENT]
        events_1 = chasecenter.get_events()
        self.assertTrue(mock_get_raw_events.called)
        mock_get_raw_events.reset_mock()
        events_2 = chasecenter.get_events()
        self.assertFalse(mock_get_raw_events.called)
        self.assertEqual(len(events_1), len(events_2))
        self.assertEqual(events_1[0].id, events_2[0].id)

    @patch('app.chasecenter.get_raw_events')
    @patch('app.cache.get_cache_file')
    def test_ignores_away_events(
        self,
        mock_file: MagicMock,
        mock_get_raw_events: MagicMock,
    ) -> None:
        mock_file.return_value = Path(self.mock_file.name)
        away_event = copy.deepcopy(EXAMPLE_RAW_EVENT)
        away_event['location'] = 'away'  # type: ignore
        mock_get_raw_events.return_value = [EXAMPLE_RAW_EVENT, away_event]
        events = chasecenter.get_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].location_name, EXAMPLE_RAW_EVENT['location'])
