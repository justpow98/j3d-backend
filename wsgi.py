"""Production WSGI entrypoint.

`app.py` is invoked directly (`python app.py`) for local dev, which runs
Flask's single-threaded/single-process built-in server via `app.run()`. That
server was also being used in production, which meant any single slow
outbound request (an unresponsive printer, a slow third-party API) blocked
every other request on the site until it timed out. Gunicorn with multiple
workers/threads avoids that.
"""
import os
from app import create_app

app = create_app(os.getenv('FLASK_CONFIG', 'production'))
