.PHONY: help install run test clean lint format typecheck checks

help:
	@echo "make install   - install dependencies"
	@echo "make run       - run the API locally"
	@echo "make test      - run tests"
	@echo "make lint      - ruff lint (auto-fix)"
	@echo "make format    - black format"
	@echo "make typecheck - mypy type checking"
	@echo "make checks    - format + lint + typecheck"
	@echo "make clean     - remove caches"

install:
	poetry install

run:
	poetry run uvicorn app.main:app --reload --port 8000

test:
	poetry run pytest -v

lint:
	poetry run ruff check . --fix

format:
	poetry run black .

typecheck:
	poetry run mypy app tests

checks: format lint typecheck

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .ruff_cache

.PHONY: test-cov cov-html

test-cov:
	poetry run pytest -v --cov=app --cov-report=term-missing --cov-fail-under=80

cov-html:
	poetry run pytest --cov=app --cov-report=html
	@echo "Open ./htmlcov/index.html in your browser"
