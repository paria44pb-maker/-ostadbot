import time
import telebot

from config import BOT_TOKEN
from math_engine import eval_expr
from memory import add_message, get_history, clear_history
from ai_engine import generate_answer

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

last_message_time = {}

def is_spam(user_id: int, cooldown: float = 1.5) -> bool:
    now = time.time()
    if user_id in last_message_time and (now - last_message_time[user_id] < cooldown):
        return True
    last_message_time[user_id] = now
    return False


@bot.message_handler(commands=["start"])
def start_handler(message):
    text = (
        "🎓 <b>سلام!</b>\n"
        "من <b>OstadBot</b> هستم؛ ربات هوش مصنوعی آموزشی و تخصصی.\n\n"
        "✅ آموزش از ابتدایی تا دانشگاه\n"
        "✅ حل تمرین و توضیح مفهومی\n"
        "✅ خلاصه‌سازی و آزمون‌سازی\n"
        "✅ کمک در برنامه‌نویسی\n\n"
        "دستورهای مهم:\n"
        "/help\n"
        "/quiz موضوع\n"
        "/summary موضوع\n"
        "/plan موضوع\n"
        "/code موضوع\n"
        "/clear\n\n"
        "سوالت را بفرست 👇"
    )
    bot.reply_to(message, text)


@bot.message_handler(commands=["help"])
def help_handler(message):
    text = (
        "📘 <b>راهنمای OstadBot</b>\n\n"
        "نمونه‌ها:\n"
        "• فتوسنتز چیست؟\n"
        "• این معادله را مرحله به مرحله حل کن: 2x + 3 = 11\n"
        "• برای دانش‌آموز کلاس هشتم توضیح بده\n"
        "• کد پایتون برای مرتب‌سازی بنویس\n\n"
        "دستورها:\n"
        "• /quiz ریاضی هشتم\n"
        "• /summary فصل اول زیست\n"
        "• /plan یادگیری پایتون\n"
        "• /code ماشین حساب با پایتون\n"
        "• /clear"
    )
    bot.reply_to(message, text)


@bot.message_handler(commands=["clear"])
def clear_handler(message):
    user_id = message.from_user.id
    clear_history(user_id)
    bot.reply_to(message, "🧹 حافظه مکالمه پاک شد.")


@bot.message_handler(commands=["quiz"])
def quiz_handler(message):
    topic = message.text.replace("/quiz", "", 1).strip()
    if not topic:
        bot.reply_to(message, "❗ بعد از /quiz موضوع را بنویس.\nمثال:\n<code>/quiz ریاضی هشتم</code>")
        return

    wait = bot.reply_to(message, "📝 در حال ساخت آزمون...")
    try:
        prompt = f"از موضوع «{topic}» 5 سوال تستی چهارگزینه‌ای با پاسخ صحیح و توضیح کوتاه بساز."
        answer = generate_answer(prompt, [])
        bot.edit_message_text(answer, message.chat.id, wait.message_id, parse_mode="HTML")
    except Exception as e:
        print(f"Quiz Error: {e}", flush=True)
        bot.edit_message_text("❌ خطا در ساخت آزمون.", message.chat.id, wait.message_id)


@bot.message_handler(commands=["summary"])
def summary_handler(message):
    topic = message.text.replace("/summary", "", 1).strip()
    if not topic:
        bot.reply_to(message, "❗ بعد از /summary موضوع را بنویس.\nمثال:\n<code>/summary فصل اول زیست</code>")
        return

    wait = bot.reply_to(message, "📚 در حال خلاصه‌سازی...")
    try:
        prompt = f"موضوع «{topic}» را به صورت خلاصه، آموزشی و دسته‌بندی‌شده توضیح بده."
        answer = generate_answer(prompt, [])
        bot.edit_message_text(answer, message.chat.id, wait.message_id, parse_mode="HTML")
    except Exception as e:
        print(f"Summary Error: {e}", flush=True)
        bot.edit_message_text("❌ خطا در خلاصه‌سازی.", message.chat.id, wait.message_id)


@bot.message_handler(commands=["plan"])
def plan_handler(message):
    topic = message.text.replace("/plan", "", 1).strip()
    if not topic:
        bot.reply_to(message, "❗ بعد از /plan موضوع را بنویس.\nمثال:\n<code>/plan یادگیری برنامه نویسی پایتون</code>")
        return

    wait = bot.reply_to(message, "📅 در حال طراحی برنامه مطالعه...")
    try:
        prompt = f"برای یادگیری «{topic}» یک برنامه مطالعه مرحله‌ای، واقعی و کاربردی طراحی کن."
        answer = generate_answer(prompt, [])
        bot.edit_message_text(answer, message.chat.id, wait.message_id, parse_mode="HTML")
    except Exception as e:
        print(f"Plan Error: {e}", flush=True)
        bot.edit_message_text("❌ خطا در ساخت برنامه مطالعه.", message.chat.id, wait.message_id)


@bot.message_handler(commands=["code"])
def code_handler(message):
    topic = message.text.replace("/code", "", 1).strip()
    if not topic:
        bot.reply_to(message, "❗ بعد از /code موضوع را بنویس.\nمثال:\n<code>/code ماشین حساب با پایتون</code>")
        return

    wait = bot.reply_to(message, "💻 در حال تولید کد...")
    try:
        prompt = f"برای موضوع «{topic}» کد کامل، تمیز و قابل اجرا بنویس و کوتاه توضیح بده."
        answer = generate_answer(prompt, [])
        bot.edit_message_text(answer, message.chat.id, wait.message_id, parse_mode="HTML")
    except Exception as e:
        print(f"Code Error: {e}", flush=True)
        bot.edit_message_text("❌ خطا در تولید کد.", message.chat.id, wait.message_id)


@bot.message_handler(func=lambda m: True, content_types=["text"])
def message_handler(message):
    user_id = message.from_user.id
    text = message.text.strip()

    if not text:
        bot.reply_to(message, "لطفاً یک پیام متنی بفرست.")
        return

    if is_spam(user_id):
        bot.reply_to(message, "⏳ کمی آرام‌تر پیام بفرست تا بهتر پاسخ بدهم.")
        return

    if len(text) > 1500:
        bot.reply_to(message, "✋ متن خیلی طولانی است. لطفاً در چند پیام کوتاه‌تر بفرست.")
        return

    if any(ch.isdigit() for ch in text) and any(op in text for op in "+-*/%^") and len(text) < 60:
        math_result = eval_expr(text)
        if math_result is not None:
            bot.reply_to(message, f"🔢 <b>نتیجه:</b>\n<code>{math_result}</code>")
            return

    add_message(user_id, f"کاربر: {text}")
    history = get_history(user_id)

    waiting = bot.reply_to(message, "🤖 در حال تحلیل و آماده‌سازی پاسخ آموزشی...")

    try:
        answer = generate_answer(text, history)
        add_message(user_id, f"ربات: {answer}")

        bot.edit_message_text(
            answer,
            chat_id=message.chat.id,
            message_id=waiting.message_id,
            parse_mode="HTML"
        )

    except Exception as e:
        print(f"AI Error: {e}", flush=True)
        bot.edit_message_text(
            "❌ در پردازش پاسخ خطای موقت رخ داد. لطفاً دوباره تلاش کن.",
            chat_id=message.chat.id,
            message_id=waiting.message_id
        )


print("🚀 OstadBot Full Pro is running...", flush=True)

while True:
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
    except Exception as e:
        print(f"Polling Error: {e}", flush=True)
        time.sleep(5)
