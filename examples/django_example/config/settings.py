"""
Minimal Django settings for the python-log-viewer example.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "example-secret-key-do-not-use-in-production"

DEBUG = True

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "python_log_viewer.contrib.django",
]

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"

# ---------------------------------------------------------------------------
# Log Viewer settings
# ---------------------------------------------------------------------------

# Point to the sample logs directory (one level up → examples/sample_logs/)
LOG_VIEWER_DIR = os.path.join(BASE_DIR, "..", "sample_logs")

# UI defaults (all optional — these are the defaults)
LOG_VIEWER_AUTO_REFRESH = True
LOG_VIEWER_REFRESH_TIMER = 5000  # milliseconds
LOG_VIEWER_AUTO_SCROLL = True
LOG_VIEWER_COLORIZE = True

# Authentication (comment out to disable)
LOG_VIEWER_USERNAME = "admin"
LOG_VIEWER_PASSWORD = "admin"

# Allow Django superusers to bypass Basic Auth (default: True)
LOG_VIEWER_SUPERUSER_ACCESS = True