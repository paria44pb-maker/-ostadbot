import os
import sqlite3
import logging

from groq import Groq
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================================
# تنظیمات
# =========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

client = Groq(api_key=GROQ_API_KEY)

# =========================================
# DATABASE
# =========================================

conn = sqlite3.connect("memory.db", check_same_thread=False)

cursor = conn.cursor()

# پیام‌های اخیر
cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    user_id INTEGER,
    role TEXT,
    content TEXT
)
""")

# حافظه بلندمدت
cursor.execute("""
CREATE TABLE IF NOT EXISTS memory (
    user_id INTEGER PRIMARY KEY,
    summary TEXT
)
""")

conn.commit()

# =========================================
# MEMORY FUNCTIONS
# =========================================

def save_message(user_id, role, content):

    cursor.execute(
        "INSERT INTO messages VALUES (?, ?, ?)",
        (user_id, role, content)
    )

    conn.commit()


def get_recent_messages(user_id, limit=12):

    cursor.execute("""
    SELECT role, content
    FROM messages
    WHERE user_id=?
    ORDER BY rowid DESC
    LIMIT ?
    """, (user_id, limit))

    rows = cursor.fetchall()

    rows.reverse()

    return [
        {
            "role": role,
            "content": content
        }
        for role, content in rows
    ]


def get_summary(user_id):

    cursor.execute(
        "SELECT summary FROM memory WHERE user_id=?",
        (user_id,)
    )

    row = cursor.fetchone()

    return row[0] if row else ""


def save_summary(user_id, summary):

    cursor.execute("""
    INSERT OR REPLACE INTO memory (user_id, summary)
    VALUES (?, ?)
    """, (user_id, summary))

    conn.commit()


def clear_memory(user_id):

    cursor.execute(
        "DELETE FROM messages WHERE user_id=?",
        (user_id,)
    )

    cursor.execute(
        "DELETE FROM memory WHERE user_id=?",
        (user_id,)
    )

    conn.commit()

# =========================================
# خلاصه‌سازی هوشمند
# =========================================

def update_summary(user_id):

    messages = get_recent_messages(user_id, 30)

    text = "\n".join([
        f"{m['role']}: {m['content']}"
        for m in messages
    ])

    try:

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": """
خلاصه‌ای کوتاه و مفید از اطلاعات مهم کاربر بساز.
فقط اطلاعات مهم را نگه دار.
"""
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        )

        summary = completion.choices[0].message.content

        save_summary(user_id, summary)

    except Exception as e:
        logger.error(e)

# =========================================
# COMMANDS
# =========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🤖 ربات حرفه‌ای هوش مصنوعی فعال شد."
    )


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id

    clear_memory(user_id)

    await update.message.reply_text(
        "✅ حافظه کاملاً پاک شد."
    )

# =========================================
# CHAT
# =========================================

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id

    user_text = update.message.text

    await update.message.chat.send_action("typing")

    try:

        summary = get_summary(user_id)

        recent_messages = get_recent_messages(user_id)

        messages = [
            {
                "role": "system",
                "content": f"""
تو یک دستیار حرفه‌ای فارسی هستی.

حافظه بلندمدت کاربر:
{summary}

قوانین:
- طبیعی صحبت کن
- حافظه را حفظ کن
- اطلاعات مهم کاربر را به خاطر بسپار
"""
            }
        ]

        messages.extend(recent_messages)

        messages.append({
            "role": "user",
            "content": user_text
        })

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages
        )

        answer = completion.choices[0].message.content

        save_message(user_id, "user", user_text)
        save_message(user_id, "assistant", answer)

        # هر 10 پیام خلاصه بروزرسانی شود
        cursor.execute("""
        SELECT COUNT(*) FROM messages
        WHERE user_id=?
        """, (user_id,))

        count = cursor.fetchone()[0]

        if count % 10 == 0:
            update_summary(user_id)

        await update.message.reply_text(answer[:4000])

    except Exception as e:

        logger.error(e)

        await update.message.reply_text(
            "❌ خطا در اتصال به هوش مصنوعی."
        )

# =========================================
# MAIN
# =========================================

def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset_command))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            chat
        )
    )

    logger.info("Bot Started ✅")

    app.run_polling()

# =========================================

if __name__ == "__main__":
    main()
