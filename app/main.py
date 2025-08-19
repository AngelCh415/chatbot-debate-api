from fastapi import FastAPI

app = FastAPI(title="Chatbot Debate API")

@app.get("/")
def root():
    return {"message": "Hello from Chatbot Debate API"}
