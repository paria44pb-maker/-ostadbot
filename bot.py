import os
import telebot
import time
import ast
import operator as op
import google.generativeai as genai
from collections import defaultdict, deque

# --------------------------------------------------
# Configuration
# --------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

bot = telebot.TeleBot(BOT_TOKEN)

# --------------------------------------------------
# Memory (lightweight – free tier friendly)
# --------------------------------------------------
user_memory = defaultdict(lambda: deque(maxlen=4))

# --------------------------------------------------
# Safe Math Engine
# --------------------------------------------------
OPS = {
    ast.Add: op.add, ast.Sub: op.sub,
    ast.Mult: op.mul, ast.Div: op.truediv,
    ast.Pow: op.pow, ast.USub: op.neg,
}

def eval_expr(expr):
    try:
        node = ast.parse(expr, mode="eval").body
        return eval_node(node)
    except:
        return None

def eval_node(node):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        return OPS[type(node.op)](eval_node(node.left), eval_node(node.right))
    if isinstance(node, ast.UnaryOp):
        return OPS[type(node.op)](eval_node(node.operand))
    raise TypeError

# --------------------------------------------------
# Utility: Level Detection
# --------------------------------------------------
def detect_level(text):
    if any(w in text for w in ["کودک", "ابتدایی", "خیلی ساده"]):
        return "ابتدایی"
    if any(w in text for w in ["کنکور", "دبیرستان", "تست"]):
        return "دبیرستان"
    if any(w in text for w in ["دانشگاه", "مهندسی", "پروژه", "مقاله"]):
        return "دانشگاهی"
    return "عمومی"

# --------------------------------------------------
# Handlers
# --------------------------------------------------
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "🎓 سلام!\n"
        "من «استاد بوت» هستم؛ ربات هوش مصنوعی آموزشی 🤖📚\n\n"
        "✅ آموزش از ابتدایی تا دانشگاه\n"
        "✅ توضیح مفهومی، حل تمرین، مثال\n"
        "✅ ریاضی، علوم، برنامه‌نویسی و بیشتر\n\n"
        "سطحت رو بگو یا مستقیم سوالت رو بپرس 👇"
    )

@bot.message_handler(func=lambda m: True)
def handle(message):
    text = message.text.strip()
    uid = message.from_user.id

    # Anti-spam / limits
    if len(text) > 400:
        bot.reply_to(message, "✋ سوال خیلی طولانیه؛ لطفاً خلاصه‌تر بنویس.")
        return

    # Math first (free & fast)
    if any(c.isdigit() for c in text) and any(o in text for o in "+-*/^") and len(text) < 30:
        res = eval_expr(text)
        if res is not None:
            bot.reply_to(message, f"🔢 پاسخ ریاضی:\n{res}")
            return

    # Memory update
    user_memory[uid].append(text)
    history = "\n".join(user_memory[uid])

    level = detect_level(text)

    thinking = bot.reply_to(message, "🤔 در حال تحلیل آموزشی...")

    try:
        prompt = f"""
تو یک معلم حرفه‌ای هستی.
سطح کاربر: {level}
وظیفه:
- توضیح شفاف و آموزشی
- مرحله‌به‌مرحله
- فارسی روان
- متناسب با سطح

سابقه گفتگو:
{history}

سوال:
{text}
"""
        response = model.generate_content(prompt)
        answer = response.text.strip()

        bot.edit_message_text(
            answer,
            chat_id=message.chat.id,
            message_id=thinking.message_id
        )

    except Exception as e:
        print("AI Error:", e, flush=True)
        bot.edit_message_text(
            "❌ خطای موقت رخ داد. لطفاً دوباره امتحان کن.",
            chat_id=message.chat.id,
            message_id=thinking.message_id
        )

# --------------------------------------------------
# Stable Polling
# --------------------------------------------------
print("🚀 Full Educational AI Bot is ONLINE", flush=True)
while True:
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
    except Exception as e:
        print("Polling Error:", e, flush=True)
        time.sleep(5)
