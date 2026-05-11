import telebot
import os

# گرفتن توکن از تنظیمات سرور
TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, """سلام! 👋
من OstadBot هستم.

فعلاً نسخه ساده من فعاله و می‌تونم:
• به سؤال‌های درسی جواب بدم
• تمرین‌ها رو حل کنم
• توضیح کوتاه بدم

سؤالت رو بفرست ✨
""")

@bot.message_handler(func=lambda message: True)
def echo(message):
    bot.reply_to(message, "✅ پیام شما دریافت شد. در حال پردازش...")

if __name__ == "__main__":
    bot.infinity_polling()
