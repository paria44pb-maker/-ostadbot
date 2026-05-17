import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from groq import Groq

# تنظیمات اولیه
TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# فرمان /start با دکمه شیشه‌ای
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✨ چت با هوش مصنوعی", callback_data='chat_mode')],
        [InlineKeyboardButton("📚 راهنما", callback_data='help')],
        [InlineKeyboardButton("🌐 وبسایت", url='https://groq.com')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "سلام! من ربات هوش مصنوعی هستم که با Groq کار می‌کنم.\n"
        "از دکمه‌های زیر استفاده کن:",
        reply_markup=reply_markup
    )

# مدیریت کلیک روی دکمه‌ها
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'chat_mode':
        await query.edit_message_text("حالت چت فعال شد! هر پیامی بدی، جواب می‌دم.")
    elif query.data == 'help':
        await query.edit_message_text(
            "🚀 راهنما:\n"
            "- /start برای نمایش منو\n"
            "- هر سوالی بپرسی، با Groq جواب می‌دم\n"
            "- از دکمه‌های شیشه‌ای زیر پیام‌ها استفاده کن",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 برگشت", callback_data='back')]
            ])
        )
    elif query.data == 'back':
        await start(update, context)

# مدیریت پیام‌های کاربر و ارسال به Groq
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.chat.send_action(action="typing")
    
    try:
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": user_message}],
            temperature=0.7,
            max_tokens=1024
        )
        bot_reply = completion.choices[0].message.content
        
        # دکمه‌های شیشه‌ای زیر پاسخ
        keyboard = [
            [InlineKeyboardButton("🔄 سوال جدید", callback_data='chat_mode')],
            [InlineKeyboardButton("👍 پسندیدم", callback_data='like')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(bot_reply, reply_markup=reply_markup)
    
    except Exception as e:
        await update.message.reply_text(f"خطا در ارتباط با Groq: {str(e)}")

# تابع اصلی
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("ربات آماده اجراست...")
    app.run_polling()

if __name__ == '__main__':
    main()
