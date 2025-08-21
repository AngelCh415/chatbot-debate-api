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
	USE_AI=false poetry run pytest -v

test-cov:
	USE_AI=false poetry run pytest -v --cov=app --cov-report=term-missing --cov-fail-under=80


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

run-ai:
	USE_AI=true poetry run uvicorn app.main:app --reload --port 8000

env-example:
	@cp -n .env.sample .env || true
	@echo "Created .env (if not existed). Update OPENAI_API_KEY before run-ai."

# ---------- Docker ----------
DOCKER_IMAGE ?= chatbot-debate-api
DOCKER_TAG   ?= latest
DOCKER_NAME  ?= chatbot-debate-api
DOCKER_PORT  ?= 8000

.PHONY: docker-build docker-run docker-run-mock docker-run-ai docker-shell docker-logs docker-stop docker-clean docker-push

docker-build:  ## Build local Docker image
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .

docker-run: docker-run-mock ## Alias to mock

docker-run-mock: ## Run container in mock mode (no OpenAI)
	docker run --rm -d --name $(DOCKER_NAME) \
		-p $(DOCKER_PORT):8000 \
		-e USE_AI=false \
		$(DOCKER_IMAGE):$(DOCKER_TAG)

docker-run-ai-fg: ## Run AI mode in foreground (no --rm) to see logs
	@[ -n "$$OPENAI_API_KEY" ] || (echo "ERROR: set OPENAI_API_KEY in your environment" && exit 1)
	docker run --name $(DOCKER_NAME) \
		-p $(DOCKER_PORT):8000 \
		-e USE_AI=true \
		-e OPENAI_API_KEY="$$OPENAI_API_KEY" \
		$(DOCKER_IMAGE):$(DOCKER_TAG)

docker-ps: ## Show all containers related to this project
	docker ps -a | sed -n '1p;/$(DOCKER_NAME)/p'

docker-inspect: ## Inspect state of the named container
	docker inspect $(DOCKER_NAME) --format='ExitCode={{.State.ExitCode}} Status={{.State.Status}} Started={{.State.StartedAt}} Finished={{.State.FinishedAt}}' || true


docker-shell: ## Open a shell inside the running container
	docker exec -it $(DOCKER_NAME) /bin/bash

docker-logs: ## Tail logs
	docker logs -f $(DOCKER_NAME)

docker-stop: ## Stop container
	- docker stop $(DOCKER_NAME)

docker-clean: docker-stop ## Remove dangling images/containers
	- docker rm $(DOCKER_NAME) 2>/dev/null || true
	- docker image prune -f

docker-push: ## Push to registry (set REGISTRY=user_or_registry)
	@[ -n "$(REGISTRY)" ] || (echo "ERROR: set REGISTRY=myuser or registry.example.com/myproj" && exit 1)
	docker tag $(DOCKER_IMAGE):$(DOCKER_TAG) $(REGISTRY)/$(DOCKER_IMAGE):$(DOCKER_TAG)
	docker push $(REGISTRY)/$(DOCKER_IMAGE):$(DOCKER_TAG)

