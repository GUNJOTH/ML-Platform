#!/bin/sh
set -eu

mkdir -p "${STORAGE_ROOT:-/data/storage}"

uv run alembic upgrade head
exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

