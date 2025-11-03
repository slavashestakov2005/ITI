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
