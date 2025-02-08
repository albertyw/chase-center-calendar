from __future__ import annotations

import copy
import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from varsnap import varsnap


TIMEZONE = ZoneInfo('America/Los_Angeles')


class Event():
    def __init__(self) -> None:
        self.id: Optional[str] = None
        self.slug: Optional[str] = None
        self.title: str = ''
        self.subtitle: Optional[str] = None
        self.date_string: str = ''
        self.date: datetime.datetime = datetime.datetime.now(tz=TIMEZONE)
        self.location_name: Optional[str] = None
        self.location_type: Optional[str] = None
        self.duration: int = 60

    def __str__(self) -> str:
        return f'{self.title} ({self.date_string})'

    def __lt__(self, other: Event) -> bool:
        return self.date < other.date

    @property
    @varsnap
    def is_future(self) -> bool:
        cutoff = datetime.datetime.now(TIMEZONE) - datetime.timedelta(days=1)
        return self.date > cutoff

    @property
    @varsnap
    def end(self) -> datetime.datetime:
        return self.date + datetime.timedelta(hours=self.duration)

    def serialize(self) -> dict[str, str]:
        data_dict = copy.deepcopy(self.__dict__)
        data_dict['date'] = data_dict['date'].isoformat()
        return data_dict

    @staticmethod
    def deserialize(data_dict: dict[str, str]) -> Event:
        event = Event()
        event.__dict__ = data_dict
        event.date = datetime.datetime.fromisoformat(data_dict['date'])
        return event
