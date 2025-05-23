#!/bin/bash

_term() {
  echo "Received SIGTERM, shutting down gracefully..."
  kill -TERM "$child"
}

# Set up signal trap
trap _term SIGTERM


# Run Django management commands before starting the server
python manage.py collectstatic --noinput
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Check if a command was passed to the container
if [ $# -eq 0 ]; then
  # Use Django's logging configuration
  export PYTHONPATH=$PYTHONPATH:.
  export DJANGO_SETTINGS_MODULE=config.settings

  # Start uvicorn with custom logging configuration
  exec uvicorn config.asgi:application \
      --host 0.0.0.0 \
      --port 8000 \
      --reload \
      --reload-dir ./utils \
      --reload-dir ./static \
      --reload-dir ./templates \
      --reload-dir ./apps \
      --reload-include "*.py" \
      --reload-include "*.html" \
      --reload-include "*.js" \
      --reload-include "*.css" \
      --workers 3 \
      --log-config config/logging.json
else
  # A command was passed, execute it
  echo "Executing command: $@"
  exec "$@"
fi

# Note: The exec command replaces the current process,
# so the script will not continue past this point
