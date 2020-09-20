FROM python:alpine

RUN mkdir /app
WORKDIR /app
ADD . /app/
RUN builddeps='gcc musl-dev build-base libffi-dev' \
  && apk add --no-cache --virtual .build-deps $builddeps \
  && pip install -r requirements.txt \
  && apk del .build-deps

EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
