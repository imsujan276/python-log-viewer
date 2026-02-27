# python-log-viewer 
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/python-log-viewer?period=total&units=NONE&left_color=BLACK&right_color=GREEN&left_text=Downloads)](https://pepy.tech/projects/python-log-viewer)

A beautiful, real-time log viewer with a dark-themed web UI. Browse, search, filter, clear, and delete log files — all from your browser.

Integrates seamlessly with **Django**, **Flask**, and **FastAPI**.

## Preview

![Log Viewer Preview](https://raw.githubusercontent.com/imsujan276/python-log-viewer/main/screenshots/preview.png)

## Support

If you like the package and find it helpful, you can [Buy Me MO:MO](https://buymemomo.com/sujang). 

---

## Features

- 📁 **File browser** — sidebar with folder tree, file sizes
- 🔍 **Search & filter** — full-text search, log-level filtering (DEBUG / INFO / WARNING / ERROR)
- 🎨 **Colour-coded** — log levels highlighted with subtle background colours
- 🔄 **Auto-refresh** — configurable live-tail (5s, 10s, 30s, 1m, or manual)
- 📜 **Line limits** — last 500 / 1000 / 2500 / 5000 / all entries
- 🗑️ **File actions** — clear (truncate) or delete log files with confirmation modals
- 🔒 **Basic Auth** — optional HTTP Basic Authentication
- 📱 **Responsive** — works on mobile with a slide-out sidebar
---

## Installation

```bash
pip install python-log-viewer
```

### Framework extras

```bash
pip install python-log-viewer[django]    # Django integration
pip install python-log-viewer[flask]     # Flask integration
pip install python-log-viewer[fastapi]   # FastAPI integration
pip install python-log-viewer[all]       # All frameworks
```

---

## Django Integration

### 1. Install

```bash
pip install python-log-viewer[django]
```

### 2. Add to `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    # ...
    "python_log_viewer.contrib.django",
]
```

### 3. Include URLs

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    # ...
    path("logs/", include("python_log_viewer.contrib.django.urls")),
]
```

### 4. Configure (optional)

Add any of these to your `settings.py`:

```python
# Path to your log directory (default: BASE_DIR / "logs")
LOG_VIEWER_DIR = BASE_DIR / "logs"

# UI defaults
LOG_VIEWER_AUTO_REFRESH  = True    # enable auto-refresh
LOG_VIEWER_REFRESH_TIMER = 5000    # refresh interval in ms
LOG_VIEWER_AUTO_SCROLL   = True    # auto-scroll to bottom
LOG_VIEWER_COLORIZE      = True    # colour-coded log levels
LOG_VIEWER_DEFAULT_LINES = 100     # default line limit (100, 250, 500, 1000, 0=all)

# Authentication (optional — leave unset to disable)
LOG_VIEWER_USERNAME = "admin"
LOG_VIEWER_PASSWORD = "secret"

# Allow logged-in Django superusers to bypass Basic Auth (default: True)
LOG_VIEWER_SUPERUSER_ACCESS = True
```

Then visit `http://localhost:8000/logs/` in your browser.

---

## Flask Integration

### 1. Install

```bash
pip install python-log-viewer[flask]
```

### 2. Register the blueprint

```python
from flask import Flask
from python_log_viewer.contrib.flask import create_log_viewer_blueprint

app = Flask(__name__)

app.register_blueprint(
    create_log_viewer_blueprint(
        log_dir="./logs",
        url_prefix="/logs",
        username="admin",      # optional
        password="secret",     # optional
    )
)

if __name__ == "__main__":
    app.run(debug=True)
```

Then visit `http://localhost:5000/logs/` in your browser.

**Blueprint parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `log_dir` | `"./logs"` | Path to log directory |
| `url_prefix` | `"/logs"` | URL prefix |
| `username` | `None` | Basic-Auth username |
| `password` | `None` | Basic-Auth password |
| `auto_refresh` | `True` | Enable auto-refresh |
| `refresh_timer` | `5000` | Refresh interval (ms) |
| `auto_scroll` | `True` | Auto-scroll to bottom |
| `colorize` | `True` | Colour-coded levels |
| `default_lines` | `100` | Default line limit (100, 250, 500, 1000, 0=all) |

---

## FastAPI Integration

### 1. Install

```bash
pip install python-log-viewer[fastapi]
```

### 2. Include the router

```python
from fastapi import FastAPI
from python_log_viewer.contrib.fastapi import create_log_viewer_router

app = FastAPI()

app.include_router(
    create_log_viewer_router(
        log_dir="./logs",
        prefix="/logs",
        username="admin",      # optional
        password="secret",     # optional
    )
)
```

Then visit `http://localhost:8000/logs/` in your browser.

**Router parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `log_dir` | `"./logs"` | Path to log directory |
| `prefix` | `"/logs"` | URL prefix |
| `username` | `None` | Basic-Auth username |
| `password` | `None` | Basic-Auth password |
| `auto_refresh` | `True` | Enable auto-refresh |
| `refresh_timer` | `5000` | Refresh interval (ms) |
| `auto_scroll` | `True` | Auto-scroll to bottom |
| `colorize` | `True` | Colour-coded levels |
| `default_lines` | `100` | Default line limit (100, 250, 500, 1000, 0=all) |

---

## Using the Core API Directly

The core classes have **zero dependencies** and can be used in any Python application:

```python
from python_log_viewer.core import LogDirectory, LogReader

# Point to your log directory
log_dir = LogDirectory("/var/log/myapp")

# List all files
for f in log_dir.list_files():
    print(f"{f.name}  {f.size} bytes  modified={f.modified}")

# Read and filter log entries
reader = LogReader(log_dir)
result = reader.read(
    file="app.log",
    lines=100,
    level="ERROR",
    search="database",
)
print(f"Total matching entries: {result['total']}")
for line in result["lines"]:
    print(line)

# File operations
log_dir.clear_file("app.log")    # truncate to 0 bytes
log_dir.delete_file("old.log")   # permanently remove
```

---

## Environment Variables

Configuration can be set via environment variables (useful for Docker / CI):

| Variable | Description |
|----------|-------------|
| `LOG_VIEWER_USERNAME` | Basic-Auth username |
| `LOG_VIEWER_PASSWORD` | Basic-Auth password |

---

## Development

```bash
# Clone
git clone https://github.com/imsujan276/python-log-viewer.git
cd python-log-viewer

# Install in editable mode
pip install -e ".[all]"
```

---

## License

MIT
