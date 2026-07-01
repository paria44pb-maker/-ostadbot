from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "online", "message": "CryptoPulse AI is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
