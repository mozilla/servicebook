# Servicebook
FROM python:3-slim

RUN apt-get update
RUN apt-get install -y git build-essential make libssl-dev libffi-dev python3-dev python3-venv
RUN addgroup --gid 10001 app
RUN adduser --gid 10001 --uid 10001 --home /app --shell /sbin/nologin --no-create-home --disabled-password --gecos we,dont,care,yeah app

WORKDIR /app
ADD ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
RUN pip install uwsgi

ADD . /app
RUN chown 10001:10001 -R /app

RUN python setup.py develop
RUN python create_version.py > version.json

USER app
EXPOSE 5001
CMD python init_db.py; uwsgi --ini uwsgi.ini
