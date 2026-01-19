.PHONY: venv-install venv-start venv-finish \
         lint format test cov pre-commit \
         docs \
         run clean

ifeq ($(OS),Windows_NT)
    IS_WINDOWS := 1
    VENV_ACTIVATE := .venv\Scripts\activate
    PYTHON := .venv\Scripts\python.exe
    PIP := .venv\Scripts\pip.exe
	RMDIR := rmdir .venv htmlcov /S /Q
else
    IS_WINDOWS := 0
    VENV_ACTIVATE := .venv/bin/activate
    PYTHON := .venv/bin/python
    PIP := .venv/bin/pip
	RMDIR := rm -rf .venv htmlcov
endif

IS_RECOMENDED_PYTHON := $(shell python3 -c 'import sys; print(1 if ".".join(map(str, sys.version_info[:2])) == 3.10 else 0)')

venv-install:
ifeq ($(IS_RECOMENDED_PYTHON), 1)
	python -m venv .venv
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r backend/requirements.txt
else
	@echo "Recommended python version is 3.10"
	@echo "Your default python version hasn't been tested"
	@echo "You can create venv and install requirements manually"
endif

venv-start:
	echo Run: $(VENV_ACTIVATE)

venv-finish:
	echo Run: deactivate

lint:
	python -m flake8 backend
	python -m isort --check-only backend
	python -m mypy backend

format:
	python -m black backend
	python -m isort backend

test:
	cd backend && python -m pytest

cov:
	python -m coverage run -m pytest
	python -m coverage report -m
	python -m coverage html

pre-commit:
	python -m pre_commit run --all-files

docs:
	cd backend && sphinx-apidoc -f -o docs/ .
	cd backend/docs && make clean && make html

run:
	cd backend && python -m uvicorn main:app --reload

clean:
	$(RMDIR)
