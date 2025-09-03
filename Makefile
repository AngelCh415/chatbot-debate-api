# ---------- Variables ----------
DOCKER_IMAGE ?= chatbot-debate-api
DOCKER_TAG   ?= latest
DOCKER_NAME  ?= chatbot-debate-api
DOCKER_PORT  ?= 8000

# ---------- Help ----------
.PHONY: help install checks test test-cov cov-html run run-ai down clean

help:
	@echo "make            # show available commands"
	@echo "make install    # install dependencies"
	@echo "make checks     # run black + ruff + mypy"
	@echo "make test       # run pytest"
	@echo "make test-cov   # pytest with coverage >= 80%"
	@echo "make cov-html   # generate HTML coverage report"
	@echo "make run        # start in Docker (mock mode)"
	@echo "make run-ai     # start in Docker (AI mode with OpenAI)"
	@echo "make down       # stop Docker container"
	@echo "make clean      # clean caches/temp containers"

# ---------- Local ----------
install:
	poetry install

checks:
	poetry run black .
	poetry run ruff check . --fix
	poetry run mypy app tests

test:
	USE_AI=false poetry run pytest -v

test-cov:
	USE_AI=false poetry run pytest -v --cov=app --cov-report=term-missing --cov-fail-under=80

cov-html:
	poetry run pytest --cov=app --cov-report=html
	@echo "Open ./htmlcov/index.html in your browser"

# ---------- Docker ----------
run: ## run API + Redis in Docker (AI mode with OpenAI)
	@[ -n "$$OPENAI_API_KEY" ] || (echo "ERROR: set OPENAI_API_KEY" && exit 1)
	docker compose up --build


down: ## stop and remove containers
	docker compose down


clean: down ## stop & remove caches/containers
	- docker rm $(DOCKER_NAME) 2>/dev/null || true
	- docker image rm $(DOCKER_IMAGE):$(DOCKER_TAG) 2>/dev/null || true
	- docker image prune -f
	- rm -rf .pytest_cache .mypy_cache .ruff_cache
	- find . -type d -name "__pycache__" -exec rm -rf {} +

.PHONY: redis-up redis-down redis-logs

redis-up:
	docker run -d --name chatbot-redis -p 6379:6379 redis:7-alpine

redis-logs:
	docker logs -f chatbot-redis

redis-down:
	- docker rm -f chatbot-redis 2>/dev/null || true


