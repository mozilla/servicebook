HERE = $(shell pwd)
VENV = .
VIRTUALENV = virtualenv
BIN = $(VENV)/bin
PYTHON = $(BIN)/python

INSTALL = $(BIN)/pip install --no-deps

.PHONY: all test

all: build

$(PYTHON):
	$(VIRTUALENV) $(VTENV_OPTS) $(VENV)

build: $(PYTHON)
	$(PYTHON) setup.py develop

clean:
	rm -rf $(VENV)

test_dependencies:
	$(BIN)/pip install flake8 tox

test: build test_dependencies
	$(BIN)/tox

docker-build:
	docker build -t servicebook/dev:latest .

docker-run:
	docker run -i -p 5000:5000 servicebook/dev:latest

version:
	$(BIN)/python create_version.py > version.json
