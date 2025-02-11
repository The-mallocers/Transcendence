# pull official base image
FROM python:3.11.4-slim-buster

# set work directory
RUN mkdir /app
WORKDIR /app


# Install system dependencies including SQLite and PostgreSQL client
RUN apt-get update && apt-get install -y \
    build-essential \
    sqlite3 \
    libsqlite3-dev \
    libpq-dev \
    gcc \
	netcat \
    && rm -rf /var/lib/apt/lists/*

# set environment variables

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r ./requirements.txt
RUN pip install djangorestframework
RUN pip install django-extensions
RUN pip install gunicorn
RUN pip install psycopg2

# copy project
COPY . .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN chmod +x /app/entrypoint.prod.sh

CMD [ "/app/entrypoint.prod.sh" ]