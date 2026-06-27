from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
def home():
    return {
        "status": "ok",
        "bot_token": "YES" if os.getenv("BOT_TOKEN") else "NO"
    }
