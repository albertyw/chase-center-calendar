from typing import Any

from flask import Blueprint, render_template
from varsnap import varsnap

from app import chasecenter

handlers = Blueprint('handlers', __name__)


@handlers.route("/")
def index() -> Any:
    events = chasecenter.get_events()
    events = [e for e in events if e.show]
    return render_template("index.htm", events=events)


@handlers.route("/about")
@varsnap
def about() -> Any:
    return render_template("about.htm")
