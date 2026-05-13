from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import uvicorn
import os
import logging

# تنظیم لاگر
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# توکن از محیط (الان فقط نیاز نیست، بعداً برای sendMessage استفاده می‌کنیم)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

app = FastAPI()

class TelegramUpdate(BaseModel):
    update_id: int
    message: dict | None = None
    edited_message: dict | None = None

@app.get("/")
def home():
    return {"message": "WhaleMind AI Telegram Webhook is running."}

@app.post("/telegram/webhook")
async def telegram_webhook(update: TelegramUpdate):
    try:
        if update.message:
            chat_id = update.message.get("chat", {}).get("id")
            text = update.message.get("text")  # این خط قبلاً syntax error داشت
            logger.info(f"Received message from chat_id {chat_id}: {text}")

        # پاسخ سریع به تلگرام
        return {"ok": True}
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
