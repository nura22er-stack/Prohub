"""Compatibility entry point for Render/Gunicorn.

Render services that still have the old start command `gunicorn app:app`
configured can import this module successfully. The actual webhook app lives in
`webhook_server.py`.
"""

from webhook_server import flask_app


app = flask_app
