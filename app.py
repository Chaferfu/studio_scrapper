import flask
from Session import Session

import main


app = flask.Flask(__name__)


@app.route("/")
def index():
    request = flask.request
    week_offset = int(request.args.get("week_offset", 0))
    week_only = bool(request.args.get("week_only", False))
    min_duration = int(request.args.get("min_duration", 0))
    min_hour = int(request.args.get("min_hour", 0))
    return Session.to_html(main.studio_scrap(week_offset, week_only, min_duration, min_hour))

app.run()