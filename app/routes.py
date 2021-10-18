from typing import Any

from flask import Blueprint, make_response, render_template
from varsnap import varsnap

from app import chasecenter, ical, oraclepark

handlers = Blueprint('handlers', __name__)


@handlers.route("/")
def index() -> Any:
    events = chasecenter.get_events()
    events = [e for e in events if e.show and e.is_future]
    return render_template("index.htm", events=events)


@handlers.route("/ical_view")
def ical_view() -> Any:
    return render_template("ical_view.htm")


@handlers.route("/chase_center")
def chase_center() -> Any:
    events = chasecenter.get_events()
    events = [e for e in events if e.show and e.is_future]
    return render_template("chase_center.htm", events=events)


@handlers.route("/chasecenter.ics")
def ical_file() -> Any:
    events = chasecenter.get_events()
    cal = ical.generate_calendar(events)
    response = make_response(cal)
    response.headers["Content-Disposition"] = \
        "attachment; filename=chasecenter.ics"
    return response


@handlers.route("/oracle_park")
def oracle_park() -> Any:
    events = oraclepark.get_events()
    events = [e for e in events if e.show and e.is_future]
    return render_template("oracle_park.htm", events=events)


@handlers.route("/oraclepark.ics")
def oracle_park_ics_file() -> Any:
    events = oraclepark.get_events()
    cal = ical.generate_calendar(events)
    response = make_response(cal)
    response.headers["Content-Disposition"] = \
        "attachment; filename=oraclepark.ics"
    return response


@handlers.route("/about")
@varsnap
def about() -> Any:
    return render_template("about.htm")
