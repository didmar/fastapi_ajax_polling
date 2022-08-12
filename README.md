FastAPI AJAX polling
=====================

Minimal example of a web app that process tasks in the background,

with basic AJAX polling to check when the result is available.

Setup and usage
----------------

```bash
pip install -r requirements.txt
uvicorn app:app --reload
# Open http://127.0.0.1:8000 in your web browser
```