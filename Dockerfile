FROM python:3.8-slim

RUN mkdir /app
WORKDIR /app
ADD . /app/

RUN pip install -r requirements.txt

ENTRYPOINT gunicorn -b 0.0.0.0:$PORT "app:load('prod')" -- --flagfile=prod.flags
