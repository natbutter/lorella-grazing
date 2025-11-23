#!/bin/sh
exec gunicorn -k uvicorn.workers.UvicornWorker app.api:app -b 0.0.0.0:8000 --workers 1 --timeout 120
