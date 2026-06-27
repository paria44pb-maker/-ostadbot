import asyncio
import logging
from fastapi import FastAPI

from core.startup import init_app
from telegram.bot import start_bot

# =========================
# LOGGING
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("CryptoPulse")

# =========================
# APP
# =========================
app = FastAPI(title="CryptoPulse AI")

# =========================
# STARTUP EVENT
# =========================
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting CryptoPulse AI...")

    # 1. init core systems (db, cache, etc.)
    await init_app()

    # 2. start telegram bot in background (NON-BLOCKING)
    asyncio.create_task(start_bot())

    logger.info("✅ Startup completed")

# =========================
# HEALTH CHECK
# =========================
@app.get("/")
def home():
    return {
        "status": "running",
        "service": "CryptoPulse AI",
        "version": "ULTRA"
    }

# =========================
# READY CHECK (Railway friendly)
# =========================
@app.get("/health")
def health():
    return {
        "status": "ok"
    }
