FROM python:3.13.0a3-slim

RUN mkdir /app
WORKDIR /app
ADD . /app/

RUN apt update && apt install -y curl
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python

RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

ENTRYPOINT ["/app/entrypoint.sh" ]
