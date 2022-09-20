from flask import Blueprint, Response, make_response, render_template
from varsnap import varsnap

from app import cache, chasecenter, ical, oraclepark

handlers = Blueprint('handlers', __name__)


@handlers.route("/")
def index() -> str:
    return render_template("index.htm")


@handlers.route("/ical_view")
def ical_view() -> str:
    return render_template("ical_view.htm")


@handlers.route("/chase_center")
def chase_center() -> str:
    events = chasecenter.get_events()
    events = [e for e in events if e.show and e.is_future]
    page = render_template("chase_center.htm", events=events)
    return page


@handlers.route("/chasecenter.ics")
def ical_file() -> Response:
    cached_cal = cache.read_raw_cache(cache.CACHED_CHASECENTER_ICS)
    if not cached_cal:
        events = chasecenter.get_events()
        cal = ical.generate_calendar(events)
        cache.save_raw_cache(cache.CACHED_CHASECENTER_ICS, cal)
    else:
        cal = cached_cal
    response = make_response(cal)
    response.headers["Content-Disposition"] = \
        "attachment; filename=chasecenter.ics"
    return response


@handlers.route("/oracle_park")
def oracle_park() -> str:
    events = oraclepark.get_events()
    events = [e for e in events if e.show and e.is_future]
    page = render_template("oracle_park.htm", events=events)
    return page


@handlers.route("/oraclepark.ics")
def oracle_park_ics_file() -> Response:
    cached_cal = cache.read_raw_cache(cache.CACHED_ORACLEPARK_ICS)
    if not cached_cal:
        events = oraclepark.get_events()
        cal = ical.generate_calendar(events)
        cache.save_raw_cache(cache.CACHED_ORACLEPARK_ICS, cal)
    else:
        cal = cached_cal
    response = make_response(cal)
    response.headers["Content-Disposition"] = \
        "attachment; filename=oraclepark.ics"
    return response


@handlers.route("/about")
@varsnap
def about() -> str:
    return render_template("about.htm")
