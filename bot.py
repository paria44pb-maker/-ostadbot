import os
import requests
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters
)

# ===============================
# ENV VARIABLES
# ===============================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("ERROR: TELEGRAM_TOKEN not found")

if not DEEPSEEK_API_KEY:
    print("WARNING: DEEPSEEK_API_KEY not found — smart replies disabled")



# ===============================
# GET BITCOIN PRICE (Coingecko)
# ===============================
def get_btc_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        data = requests.get(url).json()
        return data["bitcoin"]["usd"]
    except:
        return None



# ===============================
# SMART REPLY (DeepSeek API)
# ===============================
def smart_reply(user_msg: str) -> str:
    """
    پاسخ هوشمند با DeepSeek
    """
    if not DEEPSEEK_API_KEY:
        return "فرهاد: کلید DeepSeek تنظیم نشده. فقط پاسخ ساده می‌دم 😊"

    try:
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "تو یک ربات تلگرام فارسی هستی. پاسخ کوتاه، مودب و دوستانه بده."},
                {"role": "user", "content": user_msg}
            ]
        }

        res = requests.post(url, json=payload, headers=headers, timeout=20)
        data = res.json()

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"خطا در DeepSeek: {e}"



# ===============================
# COMMANDS
# ===============================

# /start
async def start(update, context):
    await update.message.reply_text(
        "سلام فرهاد! نسخه پرو ربات با موفقیت روشن شد 🤖🔥\n"
        "برای راهنمایی دستور /help را بزن."
    )


# /help
async def help_command(update, context):
    await update.message.reply_text(
        "📌 دستورات ربات:\n"
        "/start - شروع ربات\n"
        "/price - قیمت بیت‌کوین\n"
        "/help - راهنما\n\n"
        "پیام عادی = پاسخ هوشمند DeepSeek 😎"
    )


# /price
async def price(update, context):
    price = get_btc_price()
    if price:
        await update.message.reply_text(f"💰 قیمت بیت‌کوین الان: {price} دلار")
    else:
        await update.message.reply_text("خطا در دریافت قیمت!")    



# ===============================
# MESSAGE HANDLER (AI)
# ===============================
async def ai_handler(update, context):
    user_text = update.message.text

    # چاپ در Railway لاگ
    print(f"USER: {user_text}")

    response = smart_reply(user_text)
    await update.message.reply_text(response)



# ===============================
# MAIN APP
# ===============================
def main():
    print("🚀 Bot is running (PRO EDITION)...")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("price", price))

    # Smart reply
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_handler))

    app.run_polling()



if __name__ == "__main__":
    main()
 requirements.txt (حتماً همین دقیق)
