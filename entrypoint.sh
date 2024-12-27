#!/bin/sh

# Apply database migrations
poetry run alembic upgrade head

# Start the server
poetry run fastapi run fast_zero/app.py --host 0.0.0.0