.PHONY: help install run test clean

help:
	@echo "make install - install dependencies"
	@echo "make run - run the API locally"
	@echo "make test - run tests"
	@echo "make clean - clean up"

install:
	poetry install

run:
	poetry run uvicorn app.main:app --reload --port 8000

test:
	poetry run pytest -v

clean:
	# Borra caches de Python en todo el proyecto
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache
