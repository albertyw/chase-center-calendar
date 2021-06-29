from typing import Any

from flask import Blueprint, render_template
from varsnap import varsnap

from app import chasecenter, ical

handlers = Blueprint('handlers', __name__)


@handlers.route("/")
def index() -> Any:
    events = chasecenter.get_events()
    events = [e for e in events if e.show]
    return render_template("index.htm", events=events)


@handlers.route("/ical_view")
def ical_view() -> Any:
    events = chasecenter.get_events()
    cal = ical.generate_calendar(events)
    return render_template("ical_view.htm", cal=cal)


@handlers.route("/about")
@varsnap
def about() -> Any:
    return render_template("about.htm")
