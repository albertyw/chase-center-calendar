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
        self.ticket_required: bool = False
        self.ticket_available: bool = False
        self.ticket_sold_out: bool = False
        self.hide_road_game: bool = False
        self.duration: int = 60

    @property
    @varsnap
    def show(self) -> bool:
        if self.hide_road_game:
            return False
        return True

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
