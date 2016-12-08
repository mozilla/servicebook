# Servicebook
FROM python:3-slim

ADD . /code
RUN \
    apt-get update; \
    apt-get install -y python3-pip python3-venv git build-essential make; \
    apt-get install -y python3-dev libssl-dev libffi-dev

RUN \
    pip install -e /code ; \
    pip install -e git+https://github.com/tarekziade/smwogger#egg=smwogger


EXPOSE 5000
CMD rm -f /tmp/qa_projects.db; cd code; servicebook-import; servicebook
