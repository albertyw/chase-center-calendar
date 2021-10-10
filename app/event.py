import datetime
from typing import Optional

import pytz
from varsnap import varsnap


TIMEZONE = pytz.timezone('America/Los_Angeles')


class Event():
    def __init__(self) -> None:
        self.id: Optional[str] = None
        self.slug: Optional[str] = None
        self.title: str = ''
        self.subtitle: Optional[str] = None
        self.date_string: str = ''
        now = datetime.datetime.now()
        self.date: datetime.datetime = TIMEZONE.localize(now)
        self.location_name: Optional[str] = None
        self.location_type: Optional[str] = None
        self.ticket_required: bool = False
        self.ticket_available: bool = False
        self.ticket_sold_out: bool = False
        self.hide_road_game: bool = False
        self.duration: int = 60

    @property  # type: ignore
    @varsnap
    def show(self) -> bool:
        if self.hide_road_game:
            return False
        return True

    @property  # type: ignore
    @varsnap
    def is_future(self) -> bool:
        cutoff = datetime.datetime.now(TIMEZONE) - datetime.timedelta(days=1)
        return self.date > cutoff

    @property  # type: ignore
    @varsnap
    def end(self) -> datetime.datetime:
        return self.date + datetime.timedelta(hours=self.duration)
