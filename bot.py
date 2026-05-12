from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
from config import BOT_TOKEN
from ai_engine import generate_answer
from memory import add_to_history, get_history, clear_history

updater = Updater(BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

def start(update, context):
    update.message.reply_text("سلام! 👋\nمن استادبات هستم. هر سوالی داری بپرس.")

def clear(update, context):
    user_id = update.message.chat_id
    clear_history(user_id)
    update.message.reply_text("حافظه پاک شد ✔")

def handle_message(update, context):
    user_id = update.message.chat_id
    user_text = update.message.text

    update.message.reply_text("در حال پردازش... ⏳")

    history = get_history(user_id)
    answer = generate_answer(user_text, history)

    add_to_history(user_id, user_text)
    add_to_history(user_id, answer)

    update.message.reply_text(answer)

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("clear", clear))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

updater.start_polling()
updater.idle()
