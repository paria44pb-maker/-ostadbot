import os
import asyncio
from fastapi import FastAPI

app = FastAPI(title="CryptoPulse ULTRA AI")


# optional bot import (SAFE)
try:
    from telegram.bot_runner import start_bot
    BOT_OK = True
except Exception:
    BOT_OK = False


@app.on_event("startup")
async def startup():
    print("🚀 CryptoPulse ULTRA starting...")

    if os.getenv("BOT_TOKEN") and BOT_OK:
        asyncio.create_task(start_bot())
        print("🤖 Bot started in background")
    else:
        print("⚠️ Bot disabled")


@app.get("/")
def home():
    return {
        "status": "ULTRA CryptoPulse AI 🚀",
        "bot": bool(os.getenv("BOT_TOKEN"))
    }


@app.get("/health")
def health():
    return {
        "ok": True,
        "env": {
            "bot": bool(os.getenv("BOT_TOKEN")),
            "groq": bool(os.getenv("GROQ_API_KEY"))
        }
    }
