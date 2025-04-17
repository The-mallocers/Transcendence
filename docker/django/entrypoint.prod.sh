#!/bin/bash

echo "PostgreSQL started"

_term() {
  echo "Received SIGTERM, shutting down gracefully..."
  kill -TERM "$child"
}

# Set up signal trap
trap _term SIGTERM

python manage.py collectstatic --noinput
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Check if a command was passed to the container
if [ $# -eq 0 ]; then
  # No command was passed, start the server
  echo "Starting server..."
  exec uvicorn config.asgi:application \
      --host 0.0.0.0 \
      --port 8000 \
      --reload \
      --reload-dir . \
      --reload-dir ./utils \
      --workers 3
else
  # A command was passed, execute it
  echo "Executing command: $@"
  exec "$@"
fi

# Note: The exec command replaces the current process,
# so the script will not continue past this point
