from fastapi import FastAPI
from telegram import setup_bot
from core.startup import init_app

app = FastAPI()

@app.on_event("startup")
async def startup():
    await init_app()
    await setup_bot()

@app.get("/")
def home():
    return {"status": "CryptoPulse AI Running 🚀"}
