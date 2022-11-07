#!/usr/bin/make -f

PYTHON = python3.9

LC_ALL := en_US.UTF-8
LANG := en_US.UTF-8
PIP := 22.3
VENV := venv

export LC_ALL
export LANG

all: clean setup

info:
	@echo "take a look in Makefile to find out the commands"

setup:
	@echo "Creating virtual environment, if not already present"
	@test -d $(VENV) || $(PYTHON) -m venv $(VENV)

	@echo "Installing Python requirements"
	source $(VENV)/bin/activate && \
		$(PYTHON) -m pip install pip==$(PIP) && \
		$(PYTHON) -m pip install -r requirements.txt && \
		$(PYTHON) -m pip install -r requirements-dev.txt && \
		$(PYTHON) -m pip install -r requirements-api.txt && \
		deactivate

clean:
	@echo "Doing cleanup"
	-rm -rf $(VENV)

run-tests:
	@echo "Running tests..."
	pytest

.PHONY: all clean setup
