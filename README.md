# Chatbot Debate API

API built with **FastAPI** to manage debates between users and a bot.  
The bot is integrated with **OpenAI** and responds in **debate mode by default**: it takes a stance and argues persuasively while staying on the original topic of the conversation.

---

## 🚀 Installation

Clone the repository and install dependencies:

```bash
git clone <REPO_URL>
cd <PROJECT_NAME>
poetry install
```

## ⚙️ Configuration

Create a .env file at the project root with the required variables (use .env.sample as a reference):

```bash
USE_AI=true

# OpenAI Key
OPENAI_API_KEY=your_open_ai_key

# Model and parameters
OPENAI_MODEL=gpt-4o-mini
OPENAI_TIMEOUT=15
MAX_TOKENS=400
TEMPERATURE=0.6

# (Optional) Debug mode: if the LLM fails, return [DEBUG ...] message
DEBUG=true
```

## ▶️ Run

Mock mode (no AI, fast for development):
```bash
make run
# or
poetry run uvicorn app.main:app --reload --port 8000
```
AI mode (using OpenAI):
```bash
make run-ai
```
The API will be available at:

```bash

http://127.0.0.1:8000
```
## 📡 Main Endpoints
GET /

Health check.

Example (curl):
```bash
curl -s http://127.0.0.1:8000/
```

Possible response:


{ "status": "ok", "message": "Chatbot Debate API is running" }


POST /chat

Start or continue a debate conversation.

If no conversation_id is provided, a new one is created.

The bot sticks to the original topic and does not switch stance.

The history returns up to 5 messages per side (most recent at the end).
Request (iniciar):
```bash


curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": null,
    "message": "I think the Earth is flat"
  }'

```
Response (example):
```bash



{
  "conversation_id": "82f0151d-...-239e3e26835d",
  "message": [
    { "role": "user", "message": "I think the Earth is flat" },
    { "role": "bot",  "message": "I strongly disagree with the notion that the Earth is flat. Scientific evidence..." }
  ]
}
```
Request (continue):
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "82f0151d-...-239e3e26835d",
    "message": "Yes, but I dont see the curvature on the earth"
  }'
  ```

## 🧪 Tests & Coverage

Run unit tests:
```bash
make test
```
Run with coverage (minimum 80% + optional HTML report):
```bash
make test-cov
make cov-html   # open ./htmlcov/index.html
```
During tests, USE_AI=false is enforced to avoid real API calls.


## 🧰 Makefile (useful shortcuts)

```bash
make            # show available commands
make install    # install dependencies
make checks     # run black + ruff + mypy
make test       # run pytest
make test-cov   # pytest with coverage >= 80%
make cov-html   # generate HTML coverage report
make run        # start in mock mode
make run-ai     # start in AI mode (OpenAI)
make clean      # clean caches/temp containers

```