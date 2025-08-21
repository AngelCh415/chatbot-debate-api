FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install Poetry and configure to install into system (no venv)
RUN pip install --no-cache-dir poetry && poetry config virtualenvs.create false

# Install deps first (cache layer)
COPY pyproject.toml poetry.lock* /app/
RUN poetry install --only main --no-root

# Copy app code
COPY app /app/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
