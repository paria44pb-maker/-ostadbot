import asyncio
from fastapi import FastAPI

from core.startup import init_app
from telegram.bot_runner import start_bot

app = FastAPI()

@app.on_event("startup")
async def startup():
    await init_app()

    # bot جدا اجرا می‌شود (بدون قفل کردن server)
    asyncio.create_task(start_bot())

@app.get("/")
def home():
    return {"status": "CryptoPulse SAFE RUNNING 🚀"}

@app.get("/health")
def health():
    return {"ok": True}
