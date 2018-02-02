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
	$(BIN)/pip install pipenv
	$(BIN)/pipenv install --system

clean:
	rm -rf $(VENV)

test_dependencies:
	$(BIN)/pip install tox

test: build test_dependencies
	$(BIN)/tox

docker-build:
	docker build -t servicebook/dev:latest .

docker-run:
	docker run -i -p 5001:5001 servicebook/dev:latest
