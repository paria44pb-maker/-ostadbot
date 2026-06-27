from fastapi import FastAPI
from core.startup import init_app
from telegram.bot import start_bot

app = FastAPI()

@app.on_event("startup")
async def startup():
    await init_app()

    # مهم: جدا اجرا شود
    import asyncio
    asyncio.create_task(start_bot())

@app.get("/")
def home():
    return {"status": "CryptoPulse AI Running 🚀"}
