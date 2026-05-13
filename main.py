from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import uvicorn
import os
import logging

# تنظیمات لاگر
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # حتما این را در .env داشته باش

app = FastAPI()

class TelegramUpdate(BaseModel):
    update_id: int
    message: dict = None
    edited_message: dict = None
    # (می‌توانی بقیه فیلدها را اضافه کنی اگر لازم است)

@app.get("/")
def home():
    return {"message": "WhaleMind AI Telegram Webhook is running."}

@app.post(f"/telegram/webhook")
async def telegram_webhook(update: TelegramUpdate):
    try:
        if update.message:
            chat_id = update.message.get("chat", {}).get("id")
            text = update.message.get("text
