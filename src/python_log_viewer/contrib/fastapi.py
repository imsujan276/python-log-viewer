"""
FastAPI integration for python-log-viewer.

Usage::

    from fastapi import FastAPI
    from python_log_viewer.contrib.fastapi import create_log_viewer_router

    app = FastAPI()
    app.include_router(
        create_log_viewer_router(
            log_dir="./logs",
            prefix="/logs",
            username="admin",
            password="secret",
        )
    )
"""

from __future__ import annotations

import os
from typing import Optional

from python_log_viewer.core import LogDirectory, LogReader
from python_log_viewer._html import render_html

_ALLOWED_DEFAULT_LINES = {0, 100, 250, 500, 1000}


def _normalize_default_lines(value: int) -> int:
    try:
        value_int = int(value)
    except (TypeError, ValueError):
        return 100
    return value_int if value_int in _ALLOWED_DEFAULT_LINES else 100


def create_log_viewer_router(
    log_dir: str = "./logs",
    prefix: str = "/logs",
    username: Optional[str] = None,
    password: Optional[str] = None,
    auto_refresh: bool = True,
    refresh_timer: int = 5000,
    auto_scroll: bool = True,
    colorize: bool = True,
    default_lines: int = 100,
):
    """Create and return a FastAPI :class:`~fastapi.APIRouter`.

    Parameters
    ----------
    log_dir:
        Path to the directory containing log files.
    prefix:
        URL prefix to mount the router at (e.g. ``/logs``).
    username / password:
        Enable HTTP Basic Auth when both are provided.
    auto_refresh / refresh_timer / auto_scroll / colorize / default_lines:
        UI defaults.
    """
    from fastapi import APIRouter, Depends, HTTPException, Query, Request
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.security import HTTPBasic, HTTPBasicCredentials

    from python_log_viewer.auth import check_credentials as _check

    import secrets as _secrets

    directory = LogDirectory(log_dir)
    reader = LogReader(directory)
    router = APIRouter(prefix=prefix, tags=["python-log-viewer"])
    default_lines = _normalize_default_lines(default_lines)

    # ---- auth dependency ------------------------------------------------

    _security = HTTPBasic(auto_error=False)

    async def _verify(credentials: Optional[HTTPBasicCredentials] = Depends(_security)):
        if username and password:
            if credentials is None:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication required",
                    headers={"WWW-Authenticate": 'Basic realm="Log Viewer"'},
                )
            if not (
                _secrets.compare_digest(credentials.username, username)
                and _secrets.compare_digest(credentials.password, password)
            ):
                raise HTTPException(
                    status_code=401,
                    detail="Invalid credentials",
                    headers={"WWW-Authenticate": 'Basic realm="Log Viewer"'},
                )

    # ---- routes ---------------------------------------------------------

    _html_page = render_html(
        base_url=prefix,
        auto_refresh=auto_refresh,
        refresh_timer=refresh_timer,
        auto_scroll=auto_scroll,
        colorize=colorize,
        default_lines=default_lines,
    )

    @router.get("/", response_class=HTMLResponse, dependencies=[Depends(_verify)])
    async def index():
        return _html_page

    @router.get("/api/files", dependencies=[Depends(_verify)])
    async def api_files():
        files = directory.list_files()
        return {"files": [{"name": f.name, "size": f.size, "modified": f.modified} for f in files]}

    @router.get("/api/content", dependencies=[Depends(_verify)])
    async def api_content(
        file: str = Query("app.log"),
        lines: int = Query(default_lines),
        level: str = Query(""),
        search: str = Query(""),
        page: int = Query(1),
    ):
        return reader.read(file=file, lines=lines, level=level, search=search, page=page)

    @router.delete("/api/file", dependencies=[Depends(_verify)])
    async def api_delete(file: str = Query("")):
        if directory.delete_file(file):
            return {"success": True, "message": f"{os.path.basename(file)} deleted"}
        return JSONResponse({"success": False, "error": "Invalid or missing file"}, status_code=404)

    @router.post("/api/clear", dependencies=[Depends(_verify)])
    async def api_clear(file: str = Query("")):
        if directory.clear_file(file):
            return {"success": True, "message": f"{os.path.basename(file)} cleared"}
        return JSONResponse({"success": False, "error": "Invalid or missing file"}, status_code=404)

    # Catch-all for deep-link support (e.g. /logs/workers/celery.log)
    @router.get("/{file_path:path}", response_class=HTMLResponse, dependencies=[Depends(_verify)])
    async def index_with_file(file_path: str):
        return _html_page

    return router
