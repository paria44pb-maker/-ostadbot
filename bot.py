import os
import logging
import sqlite3

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from groq import Groq

# ---------------- LOGGING ----------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# ---------------- DATABASE ----------------
DB_NAME = "memory.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            memory_key TEXT,
            memory_value TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_memory(user_id, key, value):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # اگر قبلاً وجود داشت آپدیت کن
    cur.execute("""
        SELECT id FROM memory
        WHERE user_id=? AND memory_key=?
    """, (str(user_id), key))

    existing = cur.fetchone()

    if existing:
        cur.execute("""
            UPDATE memory
            SET memory_value=?
            WHERE user_id=? AND memory_key=?
        """, (value, str(user_id), key))
    else:
        cur.execute("""
            INSERT INTO memory (
                user_id,
                memory_key,
                memory_value
            )
            VALUES (?, ?, ?)
        """, (str(user_id), key, value))

    conn.commit()
    conn.close()


def get_memory(user_id, key):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT memory_value
        FROM memory
        WHERE user_id=? AND memory_key=?
    """, (str(user_id), key))

    row = cur.fetchone()

    conn.close()

    if row:
        return row[0]

    return None


# ---------------- GROQ ----------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(
    api_key=GROQ_API_KEY
)

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 👋\n"
        "من OstadBot هستم.\n"
        "هر سوالی داری بپرس."
    )

# ---------------- CHAT ----------------
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_text = update.message.text
    user_id = update.effective_user.id

    # ذخیره اسم کاربر
    if "اسم من" in user_text:
        name = user_text.replace("اسم من", "").replace("است", "").strip()

        if name:
            save_memory(user_id, "name", name)

            await update.message.reply_text(
                f"خوشحالم {name} 😊\nاسمت یادم موند."
            )
            return

    # بازیابی اسم
    if "اسم من چیست" in user_text:
        saved_name = get_memory(user_id, "name")

        if saved_name:
            await update.message.reply_text(
                f"اسم شما {saved_name} است 😊"
            )
        else:
            await update.message.reply_text(
                "هنوز اسم شما را نمی‌دانم."
            )

        return

    # گرفتن حافظه
    saved_name = get_memory(user_id, "name")

    try:

        system_prompt = (
            "تو یک دستیار فارسی حرفه‌ای و دوستانه هستی. "
            "کامل، روان و طبیعی جواب بده. "
            "هیچوقت اسم کاربر را حدس نزن."
        )

        if saved_name:
            system_prompt += f"\nاسم کاربر {saved_name} است."

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_text
                }
            ],
            temperature=0.7,
            max_tokens=1024,
        )

        reply = completion.choices[0].message.content

    except Exception as e:
        logger.error(f"Groq Error: {e}")
        reply = "خطا در اتصال به هوش مصنوعی."

    await update.message.reply_text(reply)

# ---------------- MAIN ----------------
def main():

    token = os.getenv("BOT_TOKEN")

    if not token:
        logger.error("BOT_TOKEN not found")
        return

    if not GROQ_API_KEY:
        logger.error("GROQ_API_KEY not found")
        return

    # ساخت دیتابیس
    init_db()

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler
        )
    )

    logger.info("Bot started successfully")

    app.run_polling()

# ---------------- RUN ----------------
if __name__ == "__main__":
    main()
