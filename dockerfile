# pull official base image
FROM python:3.11.4-slim-buster

# set work directory
RUN mkdir /app
WORKDIR /app

# set environment variables

# install dependencies
RUN pip install --upgrade pip
COPY ./docker/requirements.txt .
RUN pip install --no-cache-dir -r ./requirements.txt

# copy project
COPY . .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# RUN chmod +x /app/entrypoint.prod.sh

# CMD [ "/app/entrypoint.prod.sh" ]