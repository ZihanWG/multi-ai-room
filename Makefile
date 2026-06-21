.PHONY: install install-dev run compile lint typecheck test check

PYTHON := $(shell if [ -x .venv/bin/python ]; then printf ".venv/bin/python"; else printf "python"; fi)
STREAMLIT := $(shell if [ -x .venv/bin/streamlit ]; then printf ".venv/bin/streamlit"; else printf "streamlit"; fi)

install:
	$(PYTHON) -m pip install -r requirements.txt

install-dev:
	$(PYTHON) -m pip install -r requirements-dev.txt

run:
	$(STREAMLIT) run app.py

compile:
	$(PYTHON) -m py_compile app.py styles.py agents/*.py utils/*.py tests/*.py

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

typecheck:
	$(PYTHON) -m mypy .

test:
	$(PYTHON) -m unittest discover -s tests

check: compile lint typecheck test
