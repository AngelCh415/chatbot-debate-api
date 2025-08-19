# Chatbot Debate API

API desarrollada con **FastAPI** para gestionar debates entre usuarios y un bot.  
Actualmente, el bot responde con mensajes simulados (mock) para validar la estructura de la conversación y los endpoints.  
En etapas siguientes se integrará con la API de **OpenAI (ChatGPT)** para generar respuestas dinámicas e inteligentes.

## Endpoints principales

- `GET /` → Verificación de salud de la API.  
- `POST /chat` → Inicia o continúa una conversación de debate.  
  - Si no se envía un `conversation_id`, se crea uno nuevo.  
  - El tema y la postura inicial se extraen del **primer mensaje del usuario**.  
  - Ejemplo: `"explain why Pepsi is better than Coke"` → Tema: *Pepsi vs. Coke*, postura: *pro Pepsi*.

## Ejemplo de uso (mock actual)

```json
POST /chat
{
  "conversation_id": null,
  "message": "explain why Pepsi is better than Coke"
}
