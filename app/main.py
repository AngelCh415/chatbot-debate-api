"""This file is part of the Chatbot Debate API project."""

from fastapi import FastAPI

app = FastAPI(title="Chatbot Debate API")


@app.get("/")
def root() -> dict:
    """Root endpoint of the Chatbot Debate API.

    Returns a welcome message.
    """
    return {"message": "Hello from Chatbot Debate API"}
