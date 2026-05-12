import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from config import BOT_TOKEN
from ai_engine import generate_answer
from memory import add_to_history, get_history, clear_history

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام 👋 من استادبات هستم؛ آماده‌ام پاسخ بدم.")

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    clear_history(user_id)
    await update.message.reply_text("✅ حافظه پاک شد.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    text = update.message.text
    await update.message.reply_text("در حال پردازش... ⏳")

    history = get_history(user_id)
    answer = generate_answer(text, history)

    add_to_history(user_id, text)
    add_to_history(user_id, answer)

    await update.message.reply_text(answer)

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("clear", clear))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    asyncio.run(app.run_polling())
