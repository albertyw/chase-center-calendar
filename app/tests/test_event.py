from unittest import TestCase

from app.tests.test_chasecenter import EXAMPLE_RAW_EVENT
from app import chasecenter, event


class TestEvent(TestCase):
    def test_serialize(self) -> None:
        e = chasecenter.initialize_chase_event(EXAMPLE_RAW_EVENT)
        serialized = e.serialize()
        self.assertIn('San Francisco', serialized)
        self.assertIn('Impala', serialized)
        self.assertIn('2020-09-15T19:30:00-07:00', serialized)

    def test_deserialize(self) -> None:
        e = chasecenter.initialize_chase_event(EXAMPLE_RAW_EVENT)
        serialized = e.serialize()
        deserialized = event.Event.deserialize(serialized)
        self.assertEqual(e.id, deserialized.id)
        self.assertEqual(e.title, deserialized.title)
        self.assertEqual(e.date, deserialized.date)
