# Chatbot Debate API

API desarrollada con **FastAPI** para gestionar debates entre usuarios y un bot.  
El bot está integrado con **OpenAI** y responde en **modo debate por defecto**: toma una postura y defiende/contra-argumenta de forma persuasiva, manteniéndose en el tema original de la conversación.

---

## 🚀 Instalación

Clona el repositorio e instala dependencias:

```bash
git clone <URL_DEL_REPO>
cd <NOMBRE_DEL_PROYECTO>
poetry install
```

## ⚙️ Configuración

Crea un archivo .env en la raíz del proyecto con las variables necesarias (usa .env.sample como referencia):

```bash
USE_AI=true

# Clave de OpenAI
OPENAI_API_KEY=tu_api_key_de_openai

# Modelo y parámetros
OPENAI_MODEL=gpt-4o-mini
OPENAI_TIMEOUT=15
MAX_TOKENS=400
TEMPERATURE=0.6

# (Opcional) Modo debug: si hay un error del LLM, devuelve el mensaje [DEBUG ...]
DEBUG=true
```

## ▶️ Ejecución

Modo mock (sin IA, rápido para desarrollo):
```bash
make run
# o
poetry run uvicorn app.main:app --reload --port 8000
```
Modo IA (Usa OpenAI):
```bash
make run-ai
```
La API quedará disponible en:

```bash

http://127.0.0.1:8000
```

## 🧰 Makefile (atajos útiles)

```bash
make            # muestra comandos disponibles
make install    # instala dependencias
make checks     # black + ruff + mypy
make test       # pytest
make test-cov   # pytest con coverage >= 80%
make cov-html   # genera reporte HTML de coverage
make run        # arranca en modo mock
make run-ai     # arranca en modo IA (OpenAI)
make clean      # limpia cachés/containers temporales
```