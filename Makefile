.PHONY: install run compile test check

PYTHON := $(shell if [ -x .venv/bin/python ]; then printf ".venv/bin/python"; else printf "python"; fi)
STREAMLIT := $(shell if [ -x .venv/bin/streamlit ]; then printf ".venv/bin/streamlit"; else printf "streamlit"; fi)

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(STREAMLIT) run app.py

compile:
	$(PYTHON) -m py_compile app.py agents/*.py utils/*.py tests/*.py

test:
	$(PYTHON) -m unittest discover -s tests

check: compile test
