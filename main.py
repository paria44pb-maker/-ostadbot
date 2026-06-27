import asyncio
import os
from fastapi import FastAPI

# bot runner (اختیاری)
try:
    from telegram.bot_runner import start_bot
    BOT_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Bot import failed: {e}")
    BOT_AVAILABLE = False


app = FastAPI(title="CryptoPulse AI")


# -------------------------
# Startup
# -------------------------
@app.on_event("startup")
async def startup():
    print("🚀 CryptoPulse starting...")

    if os.getenv("BOT_TOKEN") and BOT_AVAILABLE:
        print("✅ Starting bot...")
        asyncio.create_task(start_bot())
    else:
        print("⚠️ Bot disabled (missing token or module)")

    print("✅ API started")


# -------------------------
# Routes
# -------------------------
@app.get("/")
def home():
    return {
        "status": "CryptoPulse AI Running 🚀",
        "bot": bool(os.getenv("BOT_TOKEN"))
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
# Railway entry
# -------------------------
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8080))

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port
    )
