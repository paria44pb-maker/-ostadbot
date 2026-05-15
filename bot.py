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

# ============ API HELPERS ============

def call_groq_chat(messages):
    """Chat completion با Groq"""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.1-70b-versatile",
        "messages": messages,
        "temperature": 0.4
    }
    res = requests.post(url, json=payload, headers=headers, timeout=30)
    return res.json()

def call_groq_tts(text):
    """تبدیل متن به صوت با Bark روی Groq"""
    url = "https://api.groq.com/openai/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "bark-small",
        "input": text,
        "voice": "female"
    }
    res = requests.post(url, json=payload, headers=headers, timeout=60)
    if res.status_code == 200:
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp.write(res.content)
        temp.close()
        return temp.name
    return None

def call_groq_whisper(audio_bytes):
    """تبدیل ویس کاربر به متن با Whisper روی Groq"""
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    files = {"file": ("voice.ogg", audio_bytes)}
    data = {"model": "whisper-large-v3-turbo"}
    res = requests.post(url, headers=headers, files=files, data=data)
    return res.json().get("text", None)


# ============ COMMANDS ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💬 چت هوشمند", callback_data="chat")],
        [InlineKeyboardButton("📈 قیمت بیت‌کوین", callback_data="price")],
        [InlineKeyboardButton("🎧 ویس بده", callback_data="voice")],
        [InlineKeyboardButton("⚙ تنظیمات", callback_data="settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "سلام فرهاد! 👋 ربات Super‑Turbo با Groq آماده‌ست 🌪",
        reply_markup=reply_markup
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("دستورات: /start /help /price /chat")


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        res = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        ).json()
        await update.message.reply_text(f"قیمت بیت‌کوین: {res['bitcoin']['usd']} دلار 💰")
    except Exception:
        await update.message.reply_text("خطا در دریافت قیمت بیت‌کوین.")


# ============ CHAT HANDLERS ============

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text.strip()

    if len(user_msg) < 2:
        await update.message.reply_text("لطفاً جمله کامل‌تر بنویس ❤️")
        return

    # اضافه به حافظه مکالمه
    conversation_memory.append({"role": "user", "content": user_msg})
    if len(conversation_memory) > 5:
        conversation_memory.pop(0)

    # نشان دادن حالت تایپ
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    # ارسال پیام‌ها به Groq
    messages = [{"role": "system", "content": "You are a Persian assistant."}] + conversation_memory
    data = call_groq_chat(messages)

    if "error" in data:
        await update.message.reply_text(f"Groq Error: {data['error']}")
        return

    ai_text = data["choices"][0]["message"]["content"]
    conversation_memory.append({"role": "assistant", "content": ai_text})

    # ارسال متن پاسخ
    await update.message.reply_text(ai_text)

    # تبدیل به صوت و ارسال
    audio_path = call_groq_tts(ai_text)
    if audio_path:
        await update.message.reply_voice(voice=open(audio_path, "rb"))
        os.remove(audio_path)


async def voice_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """وقتی کاربر ویس می‌فرستد"""
    voice_file = await update.message.voice.get_file()
    voice_bytes = await voice_file.download_as_bytearray()

    transcribed = call_groq_whisper(voice_bytes)
    if not transcribed:
        await update.message.reply_text("خطا در تبدیل ویس به متن ❌")
        return

    await update.message.reply_text(f"متن ویس: {transcribed}")
    update.message.text = transcribed
    await ai_chat(update, context)


# ============ CALLBACK BUTTONS ============
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "chat":
        await query.message.reply_text("✨ چت هوشمند فعال شد! بنویس:")
    elif query.data == "price":
        await price(query, context)
    elif query.data == "voice":
        await query.message.reply_text("🎙 یک ویس بفرست تا تبدیل به متن و پاسخ داده شود.")
    elif query.data == "settings":
        await query.message.reply_text("تنظیم خاصی فعلاً فعال نیست ⚙️")


# ============ MAIN ============
def main():
    print("Bot Super‑Turbo is running... 🔥")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))
    app.add_handler(MessageHandler(filters.VOICE, voice_input))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))
    app.add_handler(CommandHandler("chat", start))

    # callbacks
    app.add_handler(MessageHandler(filters.COMMAND, help_cmd))
    app.add_handler(CommandHandler("chat", start))
    app.run_polling()


if __name__ == "__main__":
    main()
