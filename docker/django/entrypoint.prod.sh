#!/bin/bash

echo "PostgreSQL started"

_term() {
  echo "Received SIGTERM, shutting down gunicorn gracefully..."
  kill -TERM "$child"
}

# Set up signal trap
trap _term SIGTERM

python manage.py collectstatic --noinput
python manage.py makemigrations --noinput
python manage.py migrate --noinput
exec uvicorn config.asgi:application \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --reload-dir . \
    --reload-dir ./utils \
    --workers 3 \
# python -m gunicorn \
#     --bind 0.0.0.0:8000 \
#     --workers 3 \
#     --reload \
#     config.asgi:application

# Store process ID
child=$!

# Wait for process to terminate
wait "$child"

# Exit with the same code as the child process
exit $?