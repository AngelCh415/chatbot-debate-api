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
## 📡 Endpoints principales
GET /

Verificación de salud.

Ejemplo (curl):
```bash
curl -s http://127.0.0.1:8000/
```

Posible respuesta:

{ "status": "ok", "message": "Chatbot Debate API is running" }
POST /chat

Inicia o continúa una conversación de debate.

Si no envías conversation_id, se crea uno nuevo.

El bot se mantiene en el tema original y no cambia de postura.

El historial retorna hasta 5 mensajes por lado (más recientes al final).
Request (iniciar):
```bash


curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": null,
    "message": "I think the Earth is flat"
  }'

```
Respuesta (ejemplo):
```bash



{
  "conversation_id": "82f0151d-...-239e3e26835d",
  "message": [
    { "role": "user", "message": "I think the Earth is flat" },
    { "role": "bot",  "message": "I strongly disagree with the notion that the Earth is flat. Scientific evidence..." }
  ]
}
```
Request (continuar):
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "82f0151d-...-239e3e26835d",
    "message": "Yes, but I dont see the curvature on the earth"
  }'
  ```

## 🧪 Pruebas y cobertura
Tests unitarios:
```bash
make test
```
Cobertura (mínimo 80% + reporte HTML opcional):
```bash
make test-cov
make cov-html   # abre ./htmlcov/index.html
```
Durante los tests forzamos USE_AI=false para no llamar a la red.

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