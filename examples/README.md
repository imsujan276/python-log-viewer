# Examples

Sample applications demonstrating `python-log-viewer` integration with each supported framework.

All examples use the shared `sample_logs/` directory which contains realistic log files.

| Example | Framework | Port | Command |
|---------|-----------|------|---------|
| [django_example](./django_example/) | Django | 8000 | `python manage.py runserver 8000` |
| [flask_example](./flask_example/) | Flask | 5000 | `python app.py` |
| [fastapi_example](./fastapi_example/) | FastAPI | 8000 | `uvicorn app:app --reload` |

**Default credentials for all examples:** `admin` / `admin`

## Quick Start

```bash
# 1. Install the package in editable mode with all extras
cd /path/to/python-log-viewer
pip install -e ".[all]"

# 2. Pick an example and run it
cd examples/flask_example
python app.py
```

Then open the URL shown in the terminal.
