import os
import time
import hmac
import hashlib
import requests
import logging
from telegram import Bot

# ----------------------------
logging.basicConfig(level=logging.INFO)
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "@comedyclick"
ACCESS_ID = "YOUR_ACCESS_ID"
SECRET_KEY = "YOUR_SECRET_KEY"

bot = Bot(token=TELEGRAM_TOKEN)

async def send_telegram(msg):
    await bot.send_message(chat_id=CHAT_ID, text=msg[:4000])

def coinex_request(method, path, body=""):
    timestamp = str(int(time.time() * 1000))
    prepared = method + path + timestamp + body
    sign = hmac.new(SECRET_KEY.encode(), prepared.encode(), hashlib.sha256).hexdigest().lower()
    url = f"https://api.coinex.com{path}"
    headers = {
        "X-COINEX-KEY": ACCESS_ID,
        "X-COINEX-SIGN": sign,
        "X-COINEX-TIMESTAMP": timestamp,
        "Content-Type": "application/json"
    }
    if method == "GET":
        resp = requests.get(url, headers=headers)
    else:
        resp = requests.post(url, headers=headers, data=body)
    return resp.json()

async def test_connection():
    try:
        info = coinex_request("GET", "/v2/account/info")
        if info.get("code") == 0:
            await send_telegram("✅ اتصال به کوینکس برقرار است!")
            balance = coinex_request("GET", "/v2/account/balance")
            if balance.get("code") == 0:
                usdt = balance.get("data", {}).get("USDT", {}).get("available", 0)
                await send_telegram(f"💰 موجودی USDT: {usdt}")
        else:
            await send_telegram(f"❌ خطا: {info.get('message')}")
    except Exception as e:
        await send_telegram(f"🔥 خطای اتصال: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_connection())
