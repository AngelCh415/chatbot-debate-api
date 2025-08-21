"""Main application file for the Chatbot Debate API."""

from fastapi import FastAPI

from app.api import routes_chat, routes_health

app = FastAPI(title="Chatbot Debate API")

# Handlers
app.include_router(routes_health.router)
app.include_router(routes_chat.router)
