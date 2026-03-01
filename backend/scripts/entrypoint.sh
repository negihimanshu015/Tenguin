#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

echo "Collecting static files..."
python backend/manage.py collectstatic --noinput

echo "Running migrations..."
python backend/manage.py migrate --noinput

echo "Starting server..."
exec "$@"
