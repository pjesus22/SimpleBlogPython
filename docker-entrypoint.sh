#!/bin/sh
set -e

# Run migrations only if SQLite database doesn't exist (or use a different check for your DB)
if [ ! -f "/var/data/db.sqlite3" ]; then
  echo "Running initial database migrations..."
  python manage.py migrate --noinput
fi

exec "$@"
