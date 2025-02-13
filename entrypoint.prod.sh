#!/bin/bash

# echo "Waiting for postgres..."
# while ! nc -z db 5432; do
#   echo "waiting db"
#   sleep 0.1
# done

echo "PostgreSQL started"

python manage.py collectstatic --noinput
python manage.py migrate --noinput
python -m gunicorn --bind 0.0.0.0:8000 --workers 3 config.wsgi:application