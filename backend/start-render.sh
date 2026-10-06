#!/bin/sh
set -e

echo "Running Django database migrations..."
python manage.py migrate --noinput

if [ "${SEED_HOTEL_ON_STARTUP:-false}" = "true" ]; then
    echo "SEED_HOTEL_ON_STARTUP=true - running initial hotel seed..."
    python manage.py seed_hotel
else
    echo "SEED_HOTEL_ON_STARTUP is not true - skipping hotel seed."
fi

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120