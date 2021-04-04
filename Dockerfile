FROM python:3.8-slim

RUN mkdir /app
WORKDIR /app
ADD . /app/

RUN pip3 install poetry
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

ENTRYPOINT poetry run gunicorn -b 0.0.0.0:$PORT "app:load('prod')" -- --flagfile=prod.flags
