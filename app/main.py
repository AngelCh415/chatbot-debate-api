from fastapi import FastAPI

app = FastAPI(title="Chatbot Debate API")

@app.get("/")
def root():
    """Root endpoint of the Chatbot Debate API"""
    return {"message": "Hello from Chatbot Debate API"}
