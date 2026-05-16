import os
import requests
import tempfile

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

conversation_memory = []

# ---------------- GROQ CHAT
def groq_chat(messages):

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "temperature": 0.5
    }

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=20)
        return r.json()
    except Exception as e:
        print("GROQ CHAT ERROR:", e)
        return {}


# ---------------- TEXT TO SPEECH
def groq_tts(text):

    url = "https://api.groq.com/openai/v1/audio/speech"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "bark-small",
        "input": text,
        "voice": "male"
    }

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=30)

        if r.status_code == 200:

            temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")

            temp.write(r.content)

            temp.close()

            return temp.name

    except Exception as e:
        print("TTS ERROR:", e)

    return None


# ---------------- VOICE TO TEXT
def groq_whisper(audio_bytes):

    url = "https://api.groq.com/openai/v1/audio/transcriptions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }

    files = {
        "file": ("voice.ogg", audio_bytes)
    }

    data = {
        "model": "whisper-large-v3-turbo"
    }

    try:
        r = requests.post(url, headers=headers, files=files, data=data, timeout=40)
        return r.json().get("text")
    except Exception as e:
        print("WHISPER ERROR:", e)
        return None


# ---------------- PRICE
async def crypto_price(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        nob = requests.get(
            "https://api.nobitex.ir/market/stats",
            timeout=10
        ).json()["stats"]

        btc = nob.get("btc-rls", {}).get("latest", "-")
        eth = nob.get("eth-rls", {}).get("latest", "-")
        usdt = nob.get("usdt-rls", {}).get("latest", "-")
        xrp = nob.get("xrp-rls", {}).get("latest", "-")
        ton = nob.get("ton-rls", {}).get("latest", "-")

        cg = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,tether,ripple,the-open-network&vs_currencies=usd",
            timeout=10
        ).json()

        btc_usd = cg["bitcoin"]["usd"]
        eth_usd = cg["ethereum"]["usd"]
        usdt_usd = cg["tether"]["usd"]
        xrp_usd = cg["ripple"]["usd"]
        ton_usd = cg["the-open-network"]["usd"]

        msg = f"""
📊 بازار کریپتو

🇮🇷 نوبیتکس

BTC : {btc}
ETH : {eth}
USDT : {usdt}
XRP : {xrp}
TON : {ton}

🌍 بازار جهانی

BTC : {btc_usd} $
ETH : {eth_usd} $
USDT : {usdt_usd} $
XRP : {xrp_usd} $
TON : {ton_usd} $
"""

        if update.message:
            await update.message.reply_text(msg)

        elif update.callback_query:
            await update.callback_query.message.reply_text(msg)

    except Exception as e:

        print("PRICE ERROR:", e)

        if update.message:
            await update.message.reply_text("خطا در دریافت قیمت بازار")

        elif update.callback_query:
            await update.callback_query.message.reply_text("خطا در دریافت قیمت بازار")


# ---------------- TOP 10
async def top_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        data = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1",
            timeout=10
        ).json()

        msg = "🔥 10 ارز برتر بازار\n\n"

        for coin in data:

            name = coin["name"]

            price = coin["current_price"]

            msg += f"{name} : {price}$\n"

        await update.message.reply_text(msg)

    except Exception as e:

        print("TOP10 ERROR:", e)

        await update.message.reply_text("خطا در دریافت داده بازار")


# ---------------- MARKET ANALYSIS
async def market_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        data = requests.get(
            "https://api.coingecko.com/api/v3/global",
            timeout=10
        ).json()

        cap = data["data"]["total_market_cap"]["usd"]

        btc_dom = data["data"]["market_cap_percentage"]["btc"]

        msg = f"""
🧠 تحلیل سریع بازار

ارزش کل بازار:
{cap:,.0f} $

Dominance BTC:
{btc_dom:.2f} %
"""

        await update.message.reply_text(msg)

    except Exception as e:

        print("ANALYSIS ERROR:", e)

        await update.message.reply_text("خطا در تحلیل بازار")


# ---------------- START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [

        [InlineKeyboardButton("📊 قیمت بازار", callback_data="price")],

        [InlineKeyboardButton("🔥 10 ارز برتر", callback_data="top")],

        [InlineKeyboardButton("🧠 تحلیل بازار", callback_data="analysis")],

        [InlineKeyboardButton("🎧 ارسال ویس", callback_data="voice")],

        [InlineKeyboardButton("💬 چت هوشمند", callback_data="chat")]

    ]

    await update.message.reply_text(

        "سلام فرهاد 👋\nربات کریپتو فعال شد",

        reply_markup=InlineKeyboardMarkup(keyboard)

    )


# ---------------- CHAT
async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_text = update.message.text

    conversation_memory.append({"role": "user", "content": user_text})

    if len(conversation_memory) > 5:

        conversation_memory.pop(0)

    messages = [

        {"role": "system", "content": "You are a helpful Persian crypto assistant."},

        *conversation_memory

    ]

    answer = groq_chat(messages)

    if "choices" not in answer:

        await update.message.reply_text("خطا در پاسخ AI")

        return

    text = answer["choices"][0]["message"]["content"]

    await update.message.reply_text(text)

    audio = groq_tts(text)

    if audio:

        await update.message.reply_voice(open(audio, "rb"))

        os.remove(audio)


# ---------------- VOICE
async def ai_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):

    file = await update.message.voice.get_file()

    voice_bytes = await file.download_as_bytearray()

    text = groq_whisper(voice_bytes)

    if not text:

        await update.message.reply_text("خطا در تبدیل ویس")

        return

    update.message.text = text

    await ai_chat(update, context)


# ---------------- BUTTON
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query

    await q.answer()

    if q.data == "price":

        await crypto_price(update, context)

    elif q.data == "top":

        await top_crypto(update, context)

    elif q.data == "analysis":

        await market_analysis(update, context)

    elif q.data == "voice":

        await q.message.reply_text("یک ویس بفرست")

    elif q.data == "chat":

        await q.message.reply_text("چت فعال شد")


# ---------------- MAIN
def main():

    if not TELEGRAM_TOKEN:
        print("ERROR: TELEGRAM_TOKEN not set")
        return

    print("Bot starting...")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CallbackQueryHandler(callback))

    app.add_handler(MessageHandler(filters.VOICE, ai_voice))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))

    app.run_polling()


if __name__ == "__main__":
    main()
