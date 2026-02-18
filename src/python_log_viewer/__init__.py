"""
python-log-viewer - A beautiful, real-time log viewer with a web UI.

Integrates with Django, Flask, and FastAPI.
"""

__version__ = "0.1.0"
__all__ = ["LogDirectory", "LogReader"]

from python_log_viewer.core import LogDirectory, LogReader  # noqa: F401
