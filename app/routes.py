from flask import Blueprint, Response, render_template, send_file
import rollbar
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
def chase_center() -> bytes:
    cached_page = cache.read_raw_cache(cache.CACHED_CHASECENTER_HTML)
    if not cached_page:
        events = chasecenter.get_events()
        events = [e for e in events if e.is_future]
        if len(events) == 0:
            rollbar.report_message('Chasecenter no events', 'error')
        page = render_template("chase_center.htm", events=events).encode('utf-8')
        cache.save_raw_cache(cache.CACHED_CHASECENTER_HTML, page)
    else:
        page = cached_page
    return page


@handlers.route("/chasecenter.ics")
def ical_file() -> Response:
    cached_file = cache.read_raw_cache(cache.CACHED_CHASECENTER_ICS)
    if not cached_file:
        events = chasecenter.get_events()
        if len(events) == 0:
            rollbar.report_message('Chasecenter no events', 'error')
        cal = ical.generate_calendar(events, 'Chase Center')
        cache.save_raw_cache(cache.CACHED_CHASECENTER_ICS, cal)
    return send_file(
        cache.get_cache_file(cache.CACHED_CHASECENTER_ICS),
        mimetype="text/calendar",
        as_attachment=True,
        download_name="chasecenter.ics",
    )


@handlers.route("/oracle_park")
def oracle_park() -> bytes:
    cached_page = cache.read_raw_cache(cache.CACHED_ORACLEPARK_HTML)
    if not cached_page:
        events = oraclepark.get_events()
        events = [e for e in events if e.is_future]
        if len(events) == 0:
            rollbar.report_message('Oracle Park no events', 'error')
        page = render_template("oracle_park.htm", events=events).encode('utf-8')
        cache.save_raw_cache(cache.CACHED_ORACLEPARK_HTML, page)
    else:
        page = cached_page
    return page


@handlers.route("/oraclepark.ics")
def oracle_park_ics_file() -> Response:
    cached_file = cache.read_raw_cache(cache.CACHED_ORACLEPARK_ICS)
    if not cached_file:
        events = oraclepark.get_events()
        if len(events) == 0:
            rollbar.report_message('Oracle Park no events', 'error')
        cal = ical.generate_calendar(events, 'Oracle Park')
        cache.save_raw_cache(cache.CACHED_ORACLEPARK_ICS, cal)
    return send_file(
        cache.get_cache_file(cache.CACHED_ORACLEPARK_ICS),
        mimetype="text/calendar",
        as_attachment=True,
        download_name="oraclepark.ics",
    )


@handlers.route("/about")
@varsnap
def about() -> str:
    return render_template("about.htm")
