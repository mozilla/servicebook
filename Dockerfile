# Servicebook
FROM python:3-slim

RUN apt-get update
RUN apt-get install -y git build-essential make libssl-dev libffi-dev python3-dev python3-venv
RUN addgroup --gid 10001 app
RUN adduser --gid 10001 --uid 10001 --home /app --shell /sbin/nologin --no-create-home --disabled-password --gecos we,dont,care,yeah app

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
RUN pip install uwsgi

COPY . /app
RUN chown 10001:10001 -R /app

RUN python setup.py develop
COPY version.json /app/version.json

USER app
EXPOSE 5001
ENTRYPOINT ["/app/entrypoint.sh"]
CMD start