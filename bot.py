import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN variable is missing!")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY variable is missing!")
import ast
import operator as op

ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.USub: op.neg,
}

def eval_expr(expression: str):
    try:
        node = ast.parse(expression, mode='eval').body
        return _eval(node)
    except Exception:
        return None

def _eval(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise TypeError("Only numbers are allowed")

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in ALLOWED_OPERATORS:
            raise TypeError("Operator not allowed")
        return ALLOWED_OPERATORS[op_type](_eval(node.left), _eval(node.right))
from collections import defaultdict, deque

user_histories = defaultdict(lambda: deque(maxlen=6))

def add_message(user_id, text):
    user_histories[user_id].append(text)

def get_history(user_id):
    return list(user_histories[user_id])

    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in ALLOWED_OPERATORS:
            raise TypeError("Unary operator not allowed")
        return ALLOWED_OPERATORS[op_type](_eval(node.operand))

    raise TypeError("Unsupported expression")
def detect_level(text: str) -> str:
    t = text.lower()

    if any(word in t for word in ["ابتدایی", "کودک", "بچه", "خیلی ساده"]):
        return "ابتدایی"

    if any(word in t for word in ["متوسطه", "راهنمایی", "هفتم", "هشتم", "نهم"]):
        return "متوسطه"

    if any(word in t for word in ["دبیرستان", "کنکور", "یازدهم", "دوازدهم", "تستی"]):
        return "دبیرستان"

    if any(word in t for word in ["دانشگاه", "مهندسی", "پروژه", "مقاله", "تحقیق دانشگاهی"]):
        return "دانشگاهی"

    return "عمومی"


def detect_request_type(text: str) -> str:
    t = text.lower()

    if any(word in t for word in ["حل کن", "محاسبه", "جواب", "مرحله به مرحله"]):
        return "حل مسئله"

    if any(word in t for word in ["توضیح", "یعنی چی", "مفهوم", "شرح"]):
        return "توضیح مفهومی"

    if any(word in t for word in ["تست", "سوال تستی", "چهارگزینه‌ای"]):
        return "تست"

    if any(word in t for word in ["خلاصه", "جمع‌بندی"]):
        return "خلاصه‌سازی"

    if any(word in t for word in ["پروژه", "تحقیق", "مقاله"]):
        return "پروژه"

    if any(word in t for word in ["کد", "برنامه نویسی", "python", "جاوا", "سی پلاس پلاس"]):
        return "برنامه‌نویسی"

    return "عمومی"
           import google.generativeai as genai
from config import GEMINI_API_KEY
from utils import detect_level, detect_request_type

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

SYSTEM_PROMPT = """
تو یک استاد هوش مصنوعی آموزشی بسیار حرفه‌ای هستی.
وظایف تو:
- پاسخ دقیق، علمی، ساختاریافته و کاملاً فارسی
- آموزش از ابتدایی تا دانشگاه
- توضیح مرحله‌به‌مرحله
- ساده‌سازی متناسب با سطح کاربر
- اگر سوال آموزشی است، با مثال توضیح بده
- اگر سوال مسئله‌ای است، مرحله‌ای حل کن
- اگر سوال برنامه‌نویسی است، کد تمیز و قابل اجرا بده
- از لحن آموزشی، حرفه‌ای و واضح استفاده کن
"""

def generate_answer(user_text: str, history: list[str]) -> str:
    level = detect_level(user_text)
    req_type = detect_request_type(user_text)

    history_text = "\n".join(history[-6:]) if history else "ندارد"

    prompt = f"""
{SYSTEM_PROMPT}

سطح کاربر: {level}
نوع درخواست: {req_type}

سابقه مکالمه:
{history_text}

سوال کاربر:
{user_text}

نحوه پاسخ:
1. مستقیم و دقیق جواب بده
2. اگر آموزشی بود مرحله‌ای توضیح بده
3. اگر لازم بود مثال بزن
4. اگر لازم بود نکات مهم را بولت‌وار بگو
5. پاسخ کاملاً فارسی باشد
"""
    response = model.generate_content(prompt)

    if hasattr(response, "text") and response.text:
        return response.text.strip()

    return "در حال حاضر پاسخ مناسبی پیدا نشد."
import time
import telebot

from config import BOT_TOKEN
from math_engine import eval_expr
from memory import add_message, get_history
from ai_engine import generate_answer

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ضد اسپم ساده
last_message_time = {}

def is_spam(user_id):
    now = time.time()
    if user_id in last_message_time and now - last_message_time[user_id] < 1.5:
        return True
    last_message_time[user_id] = now
    return False

@bot.message_handler(commands=["start"])
def start_handler(message):
    text = (
        "🎓 سلام!\n"
        "من <b>OstadBot</b> هستم؛ ربات هوش مصنوعی تخصصی و آموزشی.\n\n"
        "✅ آموزش از ابتدایی تا دانشگاه\n"
        "✅ توضیح مفهومی، حل تمرین، مثال، تست\n"
        "✅ برنامه‌نویسی، علوم، ریاضی، فیزیک و بیشتر\n\n"
        "سوالت رو بپرس 👇"
    )
    bot.reply_to(message, text)

@bot.message_handler(commands=["help"])
def help_handler(message):
    text = (
        "📌 راهنما:\n\n"
        "• سوال مفهومی بپرس: «فتوسنتز چیست؟»\n"
        "• حل مسئله بخواه: «این معادله را مرحله‌به‌مرحله حل کن»\n"
        "• سطح را مشخص کن: «برای دانش‌آموز ابتدایی توضیح بده»\n"
        "• برنامه‌نویسی بپرس: «کد پایتون برای مرتب‌سازی بنویس»"
    )
    bot.reply_to(message, text)

@bot.message_handler(func=lambda m: True, content_types=["text"])
def message_handler(message):
    user_id = message.from_user.id
    text = message.text.strip()

    if not text:
        bot.reply_to(message, "لطفاً پیام متنی بفرست.")
        return

    if is_spam(user_id):
        bot.reply_to(message, "⏳ کمی آرام‌تر پیام بفرست تا بهتر پاسخ بدهم.")
        return

    if len(text) > 1200:
        bot.reply_to(message, "✋ متن خیلی طولانی است. لطفاً کوتاه‌تر یا در چند پیام بفرست.")
        return

    # حل سریع ریاضی
    if any(ch.isdigit() for ch in text) and any(op in text for op in "+-*/%^") and len(text) < 50:
        math_result = eval_expr(text)
        if math_result is not None:
            bot.reply_to(message, f"🔢 نتیجه:\n<code>{math_result}</code>")
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
pyTelegramBotAPI
google-generativeai
worker: python bot.py
