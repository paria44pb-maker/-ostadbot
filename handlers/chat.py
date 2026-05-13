from telegram import Update
from telegram.ext import ContextTypes

from ai.groq_ai import ask_groq

from memory.memory import (
    save_message,
    load_messages
)

SYSTEM_PROMPT = """
تو یک دستیار حرفه‌ای کریپتو هستی.
"""


async def chat(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    user_text = update.message.text

    save_message(user_id, "user", user_text)

    history = load_messages(user_id)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    messages.extend(history)

    response = ask_groq(messages)

    save_message(
        user_id,
        "assistant",
        response
    )

    await update.message.reply_text(response)
