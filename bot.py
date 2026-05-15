import os
import requests
import tempfile
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes
)

# ========== ENV ==========
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN not found!")

conversation_memory = []


# ========== GROQ API ==========
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
    r = requests.post(url, json=payload, headers=headers, timeout=30)
    return r.json()


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
    r = requests.post(url, json=payload, headers=headers, timeout=60)

    if r.status_code == 200:
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp.write(r.content)
        temp.close()
        return temp.name
    return None


def groq_whisper(audio_bytes):
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    files = {"file": ("voice.ogg", audio_bytes)}
    data = {"model": "whisper-large-v3-turbo"}
    r = requests.post(url, headers=headers, files=files, data=data)
    return r.json().get("text", None)


# ========== COMMANDS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💬 چت هوشمند", callback_data="chat")],
        [InlineKeyboardButton("🎧 ارسال ویس", callback_data="voice")],
        [InlineKeyboardButton("📈 قیمت بیت‌کوین", callback_data="price")],
        [InlineKeyboardButton("⚙ تنظیمات", callback_data="settings")]
    ]
    await update.message.reply_text(
        "سلام فرهاد! 👋 نسخه Super‑Turbo فعال شد 🌪",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start /help /price")


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        ).json()
        await update.message.reply_text(
            f"قیمت بیت‌کوین: {data['bitcoin']['usd']} دلار 💰"
        )
    except:
        await update.message.reply_text("خطا در دریافت قیمت.")


# ========== CHAT ==========
async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()

    # حافظه مکالمه
    conversation_memory.append({"role": "user", "content": user_text})
    if len(conversation_memory) > 5:
        conversation_memory.pop(0)

    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    messages = [
        {"role": "system", "content": "You are a helpful Persian assistant."},
        *conversation_memory
    ]

    answer = groq_chat(messages)

    if "error" in answer:
        await update.message.reply_text(str(answer["error"]))
        return

    bot_text = answer["choices"][0]["message"]["content"]
    conversation_memory.append({"role": "assistant", "content": bot_text})

    await update.message.reply_text(bot_text)

    # TTS male
    audio_path = groq_tts(bot_text)
    if audio_path:
        await update.message.reply_voice(open(audio_path, "rb"))
        os.remove(audio_path)


async def ai_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.voice.get_file()
    voice_bytes = await file.download_as_bytearray()

    text = groq_whisper(voice_bytes)

    if not text:
        await update.message.reply_text("خطا در تبدیل ویس ❌")
        return

    await update.message.reply_text(f"متن ویس:\n{text}")
    update.message.text = text
    await ai_chat(update, context)


# ========== BUTTONS ==========
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "chat":
        await q.message.reply_text("چت هوشمند فعال شد 💬")
    elif q.data == "voice":
        await q.message.reply_text("یک ویس بفرست 🎙")
    elif q.data == "price":
        await price(q, context)
    else:
        await q.message.reply_text("تنظیم خاصی نیست.")


# ========== MAIN ==========
def main():
    print("Super‑Turbo with llama‑3.1‑8b‑instant is running...")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("price", price))

    app.add_handler(CallbackQueryHandler(callback))

    app.add_handler(MessageHandler(filters.VOICE, ai_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))

    app.run_polling()


if __name__ == "__main__":
    main()
