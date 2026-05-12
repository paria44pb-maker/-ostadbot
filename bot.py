import os
import logging
import sqlite3
import requests

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from groq import Groq

# =========================================
# Logging
# =========================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# =========================================
# ENV
# =========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN تنظیم نشده")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY تنظیم نشده")

# =========================================
# AI Client
# =========================================

client = Groq(api_key=GROQ_API_KEY)

# =========================================
# Database
# =========================================

conn = sqlite3.connect("memory.db", check_same_thread=False)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    favorite_coin TEXT
)
""")

conn.commit()

# =========================================
# Memory Functions
# =========================================

def save_user(user_id, coin):

    cursor.execute("""
    INSERT OR REPLACE INTO users
    VALUES (?, ?)
    """, (user_id, coin))

    conn.commit()


def get_user(user_id):

    cursor.execute("""
    SELECT favorite_coin
    FROM users
    WHERE user_id=?
    """, (user_id,))

    return cursor.fetchone()

# =========================================
# Market Data
# =========================================

def get_market_data(symbol):

    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"

    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        raise Exception("خطا در دریافت اطلاعات بازار")

    data = response.json()

    return {
        "price": data["lastPrice"],
        "change": data["priceChangePercent"],
        "volume": data["volume"]
    }

# =========================================
# Analysis
# =========================================

def analyze_market(change):

    change = float(change)

    if change > 3:
        trend = "Strong Bullish"

    elif change > 0:
        trend = "Bullish"

    elif change < -3:
        trend = "Strong Bearish"

    else:
        trend = "Bearish"

    return trend

# =========================================
# Commands
# =========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
🤖 Crypto AI Bot فعال شد

نمونه:
btc
eth
sol
bnb
"""

    await update.message.reply_text(text)

# =========================================
# Main Chat
# =========================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        user_id = update.message.from_user.id

        text = update.message.text.upper().strip()

        symbol = text.replace("/", "")

        if not symbol.endswith("USDT"):
            symbol += "USDT"

        market = get_market_data(symbol)

        save_user(user_id, symbol)

        trend = analyze_market(market["change"])

        prompt = f"""
ارز:
{symbol}

قیمت:
{market['price']}

تغییر 24 ساعته:
{market['change']}%

حجم:
{market['volume']}

روند:
{trend}

یک تحلیل کوتاه حرفه‌ای فارسی بده.
"""

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": """
تو یک تحلیلگر حرفه‌ای ارز دیجیتال هستی.

تحلیل‌ها:
- کوتاه
- دقیق
- حرفه‌ای
- فارسی
باشند.
"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=300
        )

        ai_text = completion.choices[0].message.content

        response = f"""
📊 {symbol}

💰 Price:
{market['price']}

📈 24h Change:
{market['change']}%

🔥 Trend:
{trend}

📦 Volume:
{market['volume']}

🧠 AI Analysis:
{ai_text}
"""

        await update.message.reply_text(response[:4000])

    except Exception as e:

        logger.error(e)

        await update.message.reply_text(
            "❌ خطا در تحلیل بازار یا اتصال."
        )

# =========================================
# Main
# =========================================

def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    logger.info("Bot Started ✅")

    app.run_polling()

# =========================================

if __name__ == "__main__":
    main()
