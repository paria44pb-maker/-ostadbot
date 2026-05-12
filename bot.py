import os
import logging
import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
from openai import OpenAI

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
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            role TEXT,
            content TEXT
        )
    """)

    conn.commit()
    conn.close()

def save_chat(user_id, role, content):

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO chat_history (user_id, role, content)
        VALUES (?, ?, ?)
    """, (str(user_id), role, content))

    conn.commit()
    conn.close()

def get_chat_history(user_id, limit=10):

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT role, content
        FROM chat_history
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT ?
    """, (str(user_id), limit))

    rows = cur.fetchall()

    conn.close()

    rows.reverse()

    messages = []

    for role, content in rows:
        messages.append({
            "role": role,
            "content": content
        })

    return messages


# ---------------- AI CLIENTS ----------------
client_groq = None
client_deepseek = None


# ---------------- COMMAND ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "سلام 👋\n"
        "من یک ربات هوش مصنوعی هستم.\n"
        "هر سوالی داری بپرس."
    )


# ---------------- MESSAGE HANDLER ----------------
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global client_groq, client_deepseek

    user_text = update.message.text
    user_id = update.effective_user.id

    history = get_chat_history(user_id)

    system_prompt = "تو یک دستیار هوش مصنوعی فارسی هستی. پاسخ‌ها را دقیق، واضح و حرفه‌ای بده."

    messages = [
        {"role": "system", "content": system_prompt}
    ]

    messages.extend(history)

    messages.append({
        "role": "user",
        "content": user_text
    })

    reply = None

    # ---------- GROQ ----------
    if client_groq:
        try:

            completion = client_groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_tokens=1024
            )

            reply = completion.choices[0].message.content

        except Exception as e:
            logger.error(f"Groq error: {e}")

    # ---------- DEEPSEEK ----------
    if not reply and client_deepseek:
        try:

            completion = client_deepseek.chat.completions.create(
                model="deepseek-chat",
                messages=messages
            )

            reply = completion.choices[0].message.content

        except Exception as e:
            logger.error(f"DeepSeek error: {e}")

    if not reply:
        reply = "خطا در اتصال به مدل‌های هوش مصنوعی."

    save_chat(user_id, "user", user_text)
    save_chat(user_id, "assistant", reply)

    await update.message.reply_text(reply)


# ---------------- MAIN ----------------
def main():

    global client_groq, client_deepseek

    token = os.getenv("BOT_TOKEN")
    groq_key = os.getenv("GROQ_API_KEY")
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")

    if not token:
        logger.error("BOT_TOKEN not found")
        return

    if groq_key:
        try:
            client_groq = Groq(api_key=groq_key)
            logger.info("Groq connected")
        except Exception as e:
            logger.error(f"Groq connection failed: {e}")

    if deepseek_key:
        try:
            client_deepseek = OpenAI(
                api_key=deepseek_key,
                base_url="https://api.deepseek.com"
            )
            logger.info("DeepSeek connected")
        except Exception as e:
            logger.error(f"DeepSeek connection failed: {e}")

    if not client_groq and not client_deepseek:
        logger.error("No AI provider available")
        return

    init_db()

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler
        )
    )

    logger.info("Bot started")

    app.run_polling()


# ---------------- RUN ----------------
if __name__ == "__main__":
    main()
