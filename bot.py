import os
import logging
import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
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


def get_chat_history(user_id, limit=12):
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
        messages.append({"role": role, "content": content})

    return messages


# ---------------- AI CLIENT ----------------
client_groq = None


# ---------------- COMMAND ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "سلام فرهاد 👋\n"
        "من دستیار هوش مصنوعی هستم. هر سوالی داری بپرس."
    )


# ---------------- MESSAGE HANDLER ----------------
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global client_groq

    user_text = update.message.text
    user_id = update.effective_user.id

    history = get_chat_history(user_id)

    system_prompt = "تو یک دستیار هوش مصنوعی حرفه‌ای هستی. پاسخ‌ها را دقیق، واضح و منطقی ارائه کن."

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_text})

    reply = None

    # ---------- GROQ ----------
    try:
        completion = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=1024
        )
        reply = completion.choices[0].message.content
        logger.info("Reply from Groq")
    except Exception as e:
        logger.error(f"Groq error: {e}")

    # ---------- FALLBACK ----------
    if not reply:
        reply = "خطا در اتصال به Groq. لطفاً دوباره تلاش کنید."

    save_chat(user_id, "user", user_text)
    save_chat(user_id, "assistant", reply)

    await update.message.reply_text(reply)


# ---------------- MAIN ----------------
def main():
    global client_groq

    token = os.getenv("BOT_TOKEN")
    groq_key = os.getenv("GROQ_API_KEY")

    if not token:
        logger.error("❌ BOT_TOKEN not found")
        return

    # ---------- GROQ ----------
    if groq_key:
        try:
            client_groq = Groq(api_key=groq_key)
            logger.info("✅ Groq connected")
        except Exception as e:
            logger.error(f"❌ Groq connection failed: {e}")
    else:
        logger.error("❌ GROQ_API_KEY not found")
        return

    init_db()

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    logger.info("🚀 Bot started successfully")
    app.run_polling()


# ---------------- RUN ----------------
if __name__ == "__main__":
    main()
