# Servicebook
FROM python:3-slim

RUN \
    apt-get update; \
    apt-get install -y python3-pip python3-venv git build-essential make; \
    apt-get install -y python3-dev libssl-dev libffi-dev

WORKDIR /code
ADD ./requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt

ADD . /code
RUN python setup.py develop


EXPOSE 5001
CMD rm -f /tmp/qa_projects.db; servicebook-import; servicebook
