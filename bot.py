import os
import logging

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from groq import Groq

from market import get_price, get_24h
from analysis import analyze_market
from memory import save_user
from prompts import SYSTEM_PROMPT

# =====================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

# =====================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🤖 Crypto AI Pro فعال شد."
    )

# =====================================

async def crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.upper().strip()

    user_id = update.message.from_user.id

    symbol = text.replace("/", "")

    if not symbol.endswith("USDT"):
        symbol += "USDT"

    try:

        ticker = get_24h(symbol)

        price = float(ticker["lastPrice"])

        change = ticker["priceChangePercent"]

        volume = ticker["volume"]

        analysis = analyze_market(price, change)

        save_user(user_id, symbol)

        ai_prompt = f"""
ارز:
{symbol}

قیمت:
{price}

تغییر 24 ساعته:
{change}%

حجم:
{volume}

روند:
{analysis['trend']}

قدرت بازار:
{analysis['momentum']}

تحلیل حرفه‌ای کوتاه بده.
"""

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": ai_prompt
                }
            ]
        )

        ai_text = completion.choices[0].message.content

        response = f"""
📊 {symbol}

💰 Price:
{price}

📈 24h Change:
{change}%

🔥 Trend:
{analysis['trend']}

⚡ Momentum:
{analysis['momentum']}

📦 Volume:
{volume}

🧠 AI Analysis:
{ai_text}
"""

        await update.message.reply_text(response[:4000])

    except Exception as e:

        logger.error(e)

        await update.message.reply_text(
            "❌ خطا در تحلیل بازار."
        )

# =====================================

def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            crypto
        )
    )

    logger.info("Bot Started ✅")

    app.run_polling()

# =====================================

if __name__ == "__main__":
    main()
