from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()

    # اگر پیام متنی وجود داشت
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text")

    if not text:
        return {"ok": True}

    print(f"Received message from chat_id {chat_id}: {text}")

    # پاسخ‌ها بر اساس دستور
    reply = handle_command(text)

    if reply:
        send_message(chat_id, reply)

    return {"ok": True}

def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

def handle_command(text):
    text = text.lower().strip()

    if text in ["/start", "سلام"]:
        return "سلام فرهاد 😄! من آماده‌ام. دستور‌هات رو بفرست 🚀"
    elif text == "/balance":
        return "موجودی حساب: ۲.۳۴ BTC 💰"
    elif text == "/buy":
        return "خرید انجام شد ✅"
    elif text == "/sell":
        return "فروش انجام شد 💸"
    else:
        return "دستور ناشناخته است. لطفاً از /start، /buy، /sell یا /balance استفاده کن."
