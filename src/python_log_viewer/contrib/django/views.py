"""
Django views for the log viewer.

Settings (all optional, set in ``settings.py``)::

    LOG_VIEWER_DIR              = BASE_DIR / "logs"  # path to log directory
    LOG_VIEWER_AUTO_REFRESH     = True
    LOG_VIEWER_REFRESH_TIMER    = 5000  # ms
    LOG_VIEWER_AUTO_SCROLL      = True
    LOG_VIEWER_COLORIZE         = True
    LOG_VIEWER_USERNAME         = None  # set both to enable Basic Auth
    LOG_VIEWER_PASSWORD         = None
    LOG_VIEWER_SUPERUSER_ACCESS = True  # allow Django superusers without Basic Auth
"""

from __future__ import annotations

import os
from functools import wraps

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from python_log_viewer.auth import check_credentials
from python_log_viewer.core import LogDirectory, LogReader
from python_log_viewer._html import render_html


# ---------------------------------------------------------------------------
# Lazy singletons – created once, reused across requests.
# ---------------------------------------------------------------------------

def _get_log_dir() -> LogDirectory:
    path = getattr(settings, "LOG_VIEWER_DIR", None)
    if path is None:
        path = os.path.join(settings.BASE_DIR, "logs")
    return LogDirectory(str(path))


def _get_reader() -> LogReader:
    return LogReader(_get_log_dir())


# ---------------------------------------------------------------------------
# Authentication decorator
# ---------------------------------------------------------------------------

def _basic_auth_required(view_func):
    """Decorator: enforce HTTP Basic Auth when credentials are configured.

    Authenticated Django superusers are allowed through automatically when
    ``LOG_VIEWER_SUPERUSER_ACCESS`` is ``True`` (the default).
    """

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        # Allow Django superusers to bypass Basic Auth
        superuser_access = getattr(settings, "LOG_VIEWER_SUPERUSER_ACCESS", True)
        if superuser_access:
            user = getattr(request, "user", None)
            if user is not None and getattr(user, "is_authenticated", False) and getattr(user, "is_superuser", False):
                return view_func(request, *args, **kwargs)

        username = getattr(settings, "LOG_VIEWER_USERNAME", None) or os.getenv("LOG_VIEWER_USERNAME")
        password = getattr(settings, "LOG_VIEWER_PASSWORD", None) or os.getenv("LOG_VIEWER_PASSWORD")

        if username and password:
            auth = request.META.get("HTTP_AUTHORIZATION", "")
            if not check_credentials(auth, username, password):
                return HttpResponse(
                    "Authentication required",
                    status=401,
                    headers={"WWW-Authenticate": 'Basic realm="Log Viewer"'},
                )

        return view_func(request, *args, **kwargs)

    return _wrapped


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

@_basic_auth_required
@require_GET
def log_viewer_page(request):
    """Serve the log viewer HTML page."""
    # Read the URL prefix from the request path
    # (strip trailing /api/... or trailing / to get the mount point)
    prefix = request.path.rstrip("/")

    html = render_html(
        base_url=prefix,
        auto_refresh=getattr(settings, "LOG_VIEWER_AUTO_REFRESH", True),
        refresh_timer=getattr(settings, "LOG_VIEWER_REFRESH_TIMER", 5000),
        auto_scroll=getattr(settings, "LOG_VIEWER_AUTO_SCROLL", True),
        colorize=getattr(settings, "LOG_VIEWER_COLORIZE", True),
    )
    return HttpResponse(html, content_type="text/html")


@_basic_auth_required
@require_GET
def get_log_files(request):
    """Return a list of available log files with metadata."""
    try:
        files = _get_log_dir().list_files()
        return JsonResponse(
            {"files": [{"name": f.name, "size": f.size, "modified": f.modified} for f in files]}
        )
    except Exception as e:
        return JsonResponse({"files": [], "error": str(e)})


@_basic_auth_required
@require_GET
def get_log_content(request):
    """Return log lines from the selected file as JSON."""
    try:
        result = _get_reader().read(
            file=request.GET.get("file", "app.log"),
            lines=int(request.GET.get("lines", "500")),
            level=request.GET.get("level", ""),
            search=request.GET.get("search", ""),
        )
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({"lines": [f"Error reading log file: {e}"], "total": 0})


@csrf_exempt
@_basic_auth_required
@require_http_methods(["DELETE"])
def delete_log_file(request):
    """Permanently delete a log file."""
    try:
        file_param = request.GET.get("file", "")
        if _get_log_dir().delete_file(file_param):
            return JsonResponse(
                {"success": True, "message": f"{os.path.basename(file_param)} deleted"}
            )
        return JsonResponse({"success": False, "error": "Invalid or missing file"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
@_basic_auth_required
@require_POST
def clear_log_file(request):
    """Clear the contents of a log file (truncate to 0 bytes)."""
    try:
        file_param = request.GET.get("file", "")
        if _get_log_dir().clear_file(file_param):
            return JsonResponse(
                {"success": True, "message": f"{os.path.basename(file_param)} cleared"}
            )
        return JsonResponse({"success": False, "error": "Invalid or missing file"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
