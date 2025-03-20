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
exec gunicorn config.asgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --worker-class uvicorn.workers.UvicornWorker
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