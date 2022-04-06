import json
from pathlib import Path
from typing import List

from app.event import Event


def get_cache_file(name: str) -> Path:
    file_path = Path('/tmp') / name
    return file_path


def read_cache(name: str) -> List[Event]:
    path = get_cache_file(name)
    with open(path, 'r') as handle:
        data = handle.read()
    serialized_events = json.loads(data)
    events = [Event.deserialize(e) for e in serialized_events]
    return events


def save_cache(name: str, events: List[Event]) -> None:
    serialized_events = [e.serialize() for e in events]
    data = json.dumps(serialized_events)
    path = get_cache_file(name)
    with open(path, 'w') as handle:
        handle.write(data)
