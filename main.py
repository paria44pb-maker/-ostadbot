import asyncio
import os
from fastapi import FastAPI

from config import Config

# Bot runner (اگر داری)
from telegram.bot_runner import start_bot

app = FastAPI(title="CryptoPulse AI")

# -------------------------
# Startup Event
# -------------------------
@app.on_event("startup")
async def startup():
    print("🚀 CryptoPulse starting...")

    # چک env بدون crash
    bot_token = os.getenv("BOT_TOKEN")

    if not bot_token:
        print("⚠️ WARNING: BOT_TOKEN not found (bot will NOT start)")
    else:
        print("✅ BOT_TOKEN loaded")

        # bot را در background اجرا کن
        asyncio.create_task(start_bot())

    print("✅ FastAPI started successfully")


# -------------------------
# Routes
# -------------------------
@app.get("/")
def home():
    return {
        "status": "CryptoPulse AI Running 🚀",
        "bot": "active" if os.getenv("BOT_TOKEN") else "inactive"
    }


@app.get("/health")
def health():
    return {
        "ok": True,
        "env": {
            "bot": bool(os.getenv("BOT_TOKEN")),
            "groq": bool(os.getenv("GROQ_API_KEY")),
        }
    }


# -------------------------
# Debug entry (Railway friendly)
# -------------------------
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8080))

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
