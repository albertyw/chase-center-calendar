from pathlib import Path
import tempfile
from unittest import TestCase
from unittest.mock import MagicMock, patch

from app.tests.test_chasecenter import EXAMPLE_RAW_EVENT
from app import cache, chasecenter


class TestSaveCache(TestCase):
    def setUp(self) -> None:
        e = chasecenter.initialize_chase_event(EXAMPLE_RAW_EVENT)
        self.events = [e]
        self.mock_file = tempfile.NamedTemporaryFile()

    def tearDown(self) -> None:
        self.mock_file.close()

    @patch('app.cache.get_cache_file')
    def test_save_cache(self, mock_file: MagicMock) -> None:
        mock_file.return_value = Path(self.mock_file.name)
        cache.save_cache('chasecenter', self.events)
        self.assertTrue(cache.get_cache_file('chasecenter').is_file())


class TestReadCache(TestCase):
    def setUp(self) -> None:
        e = chasecenter.initialize_chase_event(EXAMPLE_RAW_EVENT)
        self.events = [e]
        self.mock_file = tempfile.NamedTemporaryFile()

    def tearDown(self) -> None:
        self.mock_file.close()

    @patch('app.cache.get_cache_file')
    def test_read_cache(self, mock_file: MagicMock) -> None:
        mock_file.return_value = Path(self.mock_file.name)
        cache.save_cache('chasecenter', self.events)
        events = cache.read_cache('chasecenter')
        self.assertEqual(len(self.events), len(events))
        self.assertEqual(self.events[0].id, events[0].id)
        self.assertEqual(self.events[0].title, events[0].title)
        self.assertEqual(self.events[0].date, events[0].date)
