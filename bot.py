import os
import requests
import tempfile
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
)

# ==================== ENV ====================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# حافظه مکالمه (۵ پیام آخر)
conversation_memory = []

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN is missing!")

# ==================== API HELPERS ====================

def groq_chat(messages):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": messages,
        "temperature": 0.5
    }
    res = requests.post(url, headers=headers, json=payload, timeout=30)
    return res.json()

def groq_tts(text):
    """Convert text to speech (male voice)."""
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
    res = requests.post(url, headers=headers, json=payload, timeout=60)

    if res.status_code == 200:
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp.write(res.content)
        temp.close()
        return temp.name
    return None

def groq_whisper(audio_bytes):
    """Voice → Text"""
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    files = {"file": ("voice.ogg", audio_bytes)}
    data = {"model": "whisper-large-v3-turbo"}
    res = requests.post(url, headers=headers, files=files, data=data)
    return res.json().get("text", None)

# ==================== COMMANDS ====================

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
    await update.message.reply_text("دستورات: /start /help /price")

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bitcoin Price"""
    try:
        res = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        ).json()
        await update.message.reply_text(f"قیمت بیت‌کوین: {res['bitcoin']['usd']} دلار 💰")
    except:
        await update.message.reply_text("خطا در دریافت قیمت بیت‌کوین.")

# ==================== CHAT ====================

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text.strip()
    if len(user_msg) == 0:
        return

    # حافظه مکالمه
    conversation_memory.append({"role": "user", "content": user_msg})
    if len(conversation_memory) > 5:
        conversation_memory.pop(0)

    # حالت تایپ
    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    messages = [{"role": "system", "content": "You are a helpful Persian assistant."}]
    messages.extend(conversation_memory)

    data = groq_chat(messages)

    if "error" in data:
        await update.message.reply_text(str(data["error"]))
        return

    ai_text = data["choices"][0]["message"]["content"]
    conversation_memory.append({"role": "assistant", "content": ai_text})

    # ارسال متن
    await update.message.reply_text(ai_text)

    # ارسال ویس male
    audio_path = groq_tts(ai_text)
    if audio_path:
        await update.message.reply_voice(open(audio_path, "rb"))
        os.remove(audio_path)

async def ai_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.voice.get_file()
    voice_data = await file.download_as_bytearray()

    text = groq_whisper(voice_data)
    if not text:
        await update.message.reply_text("نتونستم ویس رو تبدیل کنم ❌")
        return

    await update.message.reply_text(f"متن ویس:\n{text}")
    update.message.text = text
    await ai_chat(update, context)

# ==================== BUTTONS ====================

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "chat":
        await q.message.reply_text("بزن بریم 💬")
    elif q.data == "voice":
        await q.message.reply_text("🎙 یه ویس ارسال کن")
    elif q.data == "price":
        await price(q, context)
    elif q.data == "settings":
        await q.message.reply_text("فعلاً تنظیم خاصی وجود نداره.")

# ==================== MAIN ====================

def main():
    print("Bot Super‑Turbo FINAL is running... 🔥")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))
    app.add_handler(MessageHandler(filters.VOICE, ai_voice))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.run_polling()


if __name__ == "__main__":
    main()
