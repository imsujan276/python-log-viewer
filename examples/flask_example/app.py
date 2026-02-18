"""
Flask example — python-log-viewer integration.

Run:
    pip install python-log-viewer[flask]
    python app.py

Then open http://localhost:5000/logs/
Credentials: admin / admin
"""

import os

from flask import Flask
from python_log_viewer.contrib.flask import create_log_viewer_blueprint

app = Flask(__name__)

# Point to the shared sample logs
SAMPLE_LOGS = os.path.join(os.path.dirname(__file__), "..", "sample_logs")

app.register_blueprint(
    create_log_viewer_blueprint(
        log_dir=SAMPLE_LOGS,
        url_prefix="/logs",
        username="admin",
        password="admin",
        auto_refresh=True,
        refresh_timer=5000,
        auto_scroll=True,
        colorize=True,
    )
)


@app.route("/")
def index():
    return '<h3>Flask + python-log-viewer</h3><p>Go to <a href="/logs/">/logs/</a></p>'


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
