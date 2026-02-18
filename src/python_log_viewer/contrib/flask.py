"""
Flask integration for python-log-viewer.

Usage::

    from flask import Flask
    from python_log_viewer.contrib.flask import create_log_viewer_blueprint

    app = Flask(__name__)
    app.register_blueprint(
        create_log_viewer_blueprint(
            log_dir="./logs",
            url_prefix="/logs",
            username="admin",
            password="secret",
        )
    )
"""

from __future__ import annotations

import os
from functools import wraps
from typing import Optional

from python_log_viewer.core import LogDirectory, LogReader
from python_log_viewer._html import render_html


def create_log_viewer_blueprint(
    log_dir: str = "./logs",
    url_prefix: str = "/logs",
    username: Optional[str] = None,
    password: Optional[str] = None,
    auto_refresh: bool = True,
    refresh_timer: int = 5000,
    auto_scroll: bool = True,
    colorize: bool = True,
):
    """Create and return a Flask :class:`~flask.Blueprint` for the log viewer.

    Parameters
    ----------
    log_dir:
        Path to the directory containing log files.
    url_prefix:
        URL prefix to mount the blueprint at (e.g. ``/logs``).
    username / password:
        Enable HTTP Basic Auth when both are provided.
    auto_refresh / refresh_timer / auto_scroll / colorize:
        UI defaults.
    """
    from flask import Blueprint, jsonify, request, Response

    from python_log_viewer.auth import check_credentials

    directory = LogDirectory(log_dir)
    reader = LogReader(directory)
    bp = Blueprint("log_viewer", __name__, url_prefix=url_prefix)

    # ---- auth decorator -------------------------------------------------

    def _auth_required(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if username and password:
                auth = request.headers.get("Authorization", "")
                if not check_credentials(auth, username, password):
                    return Response(
                        "Authentication required",
                        401,
                        {"WWW-Authenticate": 'Basic realm="Log Viewer"'},
                    )
            return fn(*args, **kwargs)
        return wrapper

    # ---- routes ---------------------------------------------------------

    @bp.route("/", methods=["GET"])
    @_auth_required
    def index():
        html = render_html(
            base_url=url_prefix,
            auto_refresh=auto_refresh,
            refresh_timer=refresh_timer,
            auto_scroll=auto_scroll,
            colorize=colorize,
        )
        return Response(html, content_type="text/html")

    @bp.route("/api/files", methods=["GET"])
    @_auth_required
    def api_files():
        files = directory.list_files()
        return jsonify({"files": [{"name": f.name, "size": f.size, "modified": f.modified} for f in files]})

    @bp.route("/api/content", methods=["GET"])
    @_auth_required
    def api_content():
        result = reader.read(
            file=request.args.get("file", "app.log"),
            lines=int(request.args.get("lines", "500")),
            level=request.args.get("level", ""),
            search=request.args.get("search", ""),
        )
        return jsonify(result)

    @bp.route("/api/file", methods=["DELETE"])
    @_auth_required
    def api_delete():
        file_param = request.args.get("file", "")
        if directory.delete_file(file_param):
            return jsonify({"success": True, "message": f"{os.path.basename(file_param)} deleted"})
        return jsonify({"success": False, "error": "Invalid or missing file"}), 404

    @bp.route("/api/clear", methods=["POST"])
    @_auth_required
    def api_clear():
        file_param = request.args.get("file", "")
        if directory.clear_file(file_param):
            return jsonify({"success": True, "message": f"{os.path.basename(file_param)} cleared"})
        return jsonify({"success": False, "error": "Invalid or missing file"}), 404

    return bp
