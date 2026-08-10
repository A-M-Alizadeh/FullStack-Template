#!/bin/sh
set -eu

# Managed hosts inject DATABASE_URL; local compose uses POSTGRES_*.
if [ "${RUN_MIGRATIONS_ON_START:-true}" = "true" ]; then
  echo "Running database migrations..."
  alembic upgrade head
fi

exec "$@"
