#    ------- CONFIG -------

VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip


#    ------- RULES -------

install:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install flake8 mypy build

run:
	$(PYTHON) a_maze_ing.py config.txt

debug:
	$(PYTHON) -m pdb a_maze_ing.py config.txt

clean:
	rm -rf __pycache__ */__pycache__ .mypy_cache

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy --strict .

build:
	$(PYTHON) -m build

.PHONY: install run debug clean lint 
