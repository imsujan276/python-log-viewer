"""
FastAPI example — python-log-viewer integration.

Run:
    pip install python-log-viewer[fastapi]
    uvicorn app:app --host 0.0.0.0 --port 8000 --reload

Then open http://localhost:8000/logs/
Credentials: admin / admin
"""

import os

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from python_log_viewer.contrib.fastapi import create_log_viewer_router

app = FastAPI(title="FastAPI + python-log-viewer example")

# Point to the shared sample logs
SAMPLE_LOGS = os.path.join(os.path.dirname(__file__), "..", "sample_logs")

app.include_router(
    create_log_viewer_router(
        log_dir=SAMPLE_LOGS,
        prefix="/logs",
        username="admin",
        password="admin",
        auto_refresh=True,
        refresh_timer=5000,
        auto_scroll=True,
        colorize=True,
    )
)


@app.get("/", response_class=HTMLResponse)
async def index():
    return '<h3>FastAPI + python-log-viewer</h3><p>Go to <a href="/logs/">/logs/</a></p>'
