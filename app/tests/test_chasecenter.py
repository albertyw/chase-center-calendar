from unittest import TestCase

from app import chasecenter


class TestGetRawEvents(TestCase):
    def test_get_events(self) -> None:
        events = chasecenter.get_raw_events()
        self.assertIn('data', events)
        self.assertIn('contentByType', events['data'])
        self.assertIn('items', events['data']['contentByType'])
        self.assertTrue(len(events['data']['contentByType']['items']) > 0)
