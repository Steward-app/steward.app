FROM python:3.6

RUN mkdir /srv
WORKDIR /srv
ADD . /srv/
RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["flask", "run", "-h", "0.0.0.0"]
