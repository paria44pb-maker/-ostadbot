import os
import json
import time
import sqlite3
import logging
import requests
from groq import Groq
from openai import OpenAI

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO
)

logger = logging.getLogger("AI_BOT")

# =========================================================
# ENV VARIABLES
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

# =========================================================
# DATABASE
# =========================================================

DB_NAME = "memory.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        role TEXT,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def save_message(user_id, role, content):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)",
        (str(user_id), role, content)
    )

    conn.commit()
    conn.close()


def get_history(user_id, limit=8):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT role, content
        FROM messages
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT ?
    """, (str(user_id), limit))

    rows = cur.fetchall()

    conn.close()

    rows.reverse()

    history = []

    for role, content in rows:
        history.append({
            "role": role,
            "content": content
        })

    return history


def clear_history(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM messages WHERE user_id=?",
        (str(user_id),)
    )

    conn.commit()
    conn.close()


# =========================================================
# AI CLIENTS
# =========================================================

groq_client = None
openai_client = None

if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)

if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)

# =========================================================
# PROVIDERS STATUS
# =========================================================

provider_status = {
    "groq": True,
    "openai": True,
    "deepseek": True,
    "together": True
}

# =========================================================
# SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """
You are a powerful AI assistant.

Rules:
- Give accurate and professional answers.
- Be clear and structured.
- Use markdown when useful.
- Keep answers concise unless detailed explanation is needed.
"""

# =========================================================
# AI RESPONSE GENERATOR
# =========================================================

async def stream_ai_response(messages):

    # =====================================================
    # 1) GROQ
    # =====================================================

    if provider_status["groq"] and groq_client:

        try:
            stream = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                stream=True
            )

            for chunk in stream:

                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

            return

        except Exception as e:
            logger.error(f"GROQ ERROR: {e}")
            provider_status["groq"] = False

    # =====================================================
    # 2) OPENAI
    # =====================================================

    if provider_status["openai"] and openai_client:

        try:
            stream = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                stream=True
            )

            for chunk in stream:

                content = chunk.choices[0].delta.content

                if content:
                    yield content

            return

        except Exception as e:
            logger.error(f"OPENAI ERROR: {e}")
            provider_status["openai"] = False

    # =====================================================
    # 3) DEEPSEEK
    # =====================================================

    if provider_status["deepseek"] and DEEPSEEK_API_KEY:

        try:
            response = requests.post(
                "https://api.deepseek.com/chat/completions",
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": messages,
                    "stream": True
                },
                stream=True,
                timeout=60
            )

            for line in response.iter_lines():

                if line:

                    decoded = line.decode("utf-8")

                    if decoded.startswith("data: "):

                        data = decoded.replace("data: ", "")

                        if data == "[DONE]":
                            break

                        try:
                            payload = json.loads(data)

                            content = payload["choices"][0]["delta"].get("content")

                            if content:
                                yield content

                        except:
                            pass

            return

        except Exception as e:
            logger.error(f"DEEPSEEK ERROR: {e}")
            provider_status["deepseek"] = False

    # =====================================================
    # 4) TOGETHER AI
    # =====================================================

    if provider_status["together"] and TOGETHER_API_KEY:

        try:
            response = requests.post(
                "https://api.together.xyz/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {TOGETHER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "meta-llama/Llama-3-70b-chat-hf",
                    "messages": messages,
                    "stream": True
                },
                stream=True,
                timeout=60
            )

            for line in response.iter_lines():

                if line:

                    decoded = line.decode("utf-8")

                    if decoded.startswith("data: "):

                        data = decoded.replace("data: ", "")

                        if data == "[DONE]":
                            break

                        try:
                            payload = json.loads(data)

                            content = payload["choices"][0]["delta"].get("content")

                            if content:
                                yield content

                        except:
                            pass

            return

        except Exception as e:
            logger.error(f"TOGETHER ERROR: {e}")
            provider_status["together"] = False

    # =====================================================
    # FALLBACK MESSAGE
    # =====================================================

    yield "All AI providers are temporarily unavailable. Please try again later."


# =========================================================
# COMMANDS
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (
        "👋 Welcome\n\n"
        "This is an advanced AI assistant.\n"
        "Ask anything you want."
    )

    await update.message.reply_text(text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (
        "Available commands:\n\n"
        "/start - Start the bot\n"
        "/help - Show help message\n"
        "/reset - Clear conversation memory"
    )

    await update.message.reply_text(text)


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    clear_history(user_id)

    await update.message.reply_text(
        "Conversation memory cleared."
    )


# =========================================================
# MAIN MESSAGE HANDLER
# =========================================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    user_text = update.message.text

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )

    history = get_history(user_id)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    messages.extend(history)

    messages.append({
        "role": "user",
        "content": user_text
    })

    save_message(user_id, "user", user_text)

    sent_message = await update.message.reply_text(
        "Thinking..."
    )

    full_response = ""
    edit_counter = 0

    async for chunk in stream_ai_response(messages):

        full_response += chunk
        edit_counter += 1

        # جلوگیری از Rate Limit تلگرام
        if edit_counter % 8 == 0:

            try:
                await sent_message.edit_text(
                    full_response[:4000]
                )

            except:
                pass

    try:
        await sent_message.edit_text(
            full_response[:4000]
        )

    except:
        pass

    save_message(user_id, "assistant", full_response)


# =========================================================
# MAIN
# =========================================================

def main():

    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is missing")
        return

    init_db()

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("reset", reset_command))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    logger.info("BOT IS RUNNING")

    app.run_polling()


if __name__ == "__main__":
    main()
