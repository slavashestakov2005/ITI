.PHONY: lint format test

lint:
	cd backend && python -m flake8
	cd backend && python -m isort --check-only .

format:
	cd backend && python -m black .
	cd backend && python -m isort .

pre-commit:
	python -m pre_commit run --all-files

test:
	cd backend && python -m pytest

run:
	cd backend && python -m uvicorn main:app --reload

docs:
	cd backend/docs && make clean && make html

docs-modules:
	cd backend && sphinx-apidoc -f -o docs/ .
