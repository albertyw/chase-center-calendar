import json
import os
from pathlib import Path
import time
from typing import List, Optional

from app.event import Event


CACHE_DURATION = 60 * 60
CACHED_CHASECENTER = 'chasecenter'
CACHED_ORACLEPARK = 'oraclepark'
CACHED_CHASECENTER_ICS = 'chasecenter.ics'
CACHED_ORACLEPARK_ICS = 'oraclepark.ics'


def get_cache_file(name: str) -> Path:
    file_path = Path('/tmp') / name
    return file_path


def read_raw_cache(name: str) -> Optional[str]:
    path = get_cache_file(name)
    if not path.is_file():
        return None
    if time.time() - os.path.getmtime(path) > CACHE_DURATION:
        return None
    with open(path, 'r') as handle:
        data = handle.read()
    return data


def save_raw_cache(name: str, data: str) -> None:
    path = get_cache_file(name)
    with open(path, 'w') as handle:
        handle.write(data)


def read_cache(name: str) -> Optional[List[Event]]:
    data = read_raw_cache(name)
    if data is None:
        return data
    try:
        serialized_events = json.loads(data)
    except json.decoder.JSONDecodeError:
        return None
    events = [Event.deserialize(e) for e in serialized_events]
    return events


def save_cache(name: str, events: List[Event]) -> None:
    serialized_events = [e.serialize() for e in events]
    data = json.dumps(serialized_events)
    save_raw_cache(name, data)
