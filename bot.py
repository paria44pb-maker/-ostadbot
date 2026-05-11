import os
import telebot
import ast
import operator as op
import time

# -----------------------------
# Load BOT TOKEN from Railway
# -----------------------------
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN variable is missing in Railway!")

bot = telebot.TeleBot(TOKEN)

# -----------------------------
# Safe Math Evaluator (No eval)
# -----------------------------
ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg
}

def eval_expr(expr: str):
    """Evaluate math expression securely"""
    try:
        node = ast.parse(expr, mode="eval").body
        return eval_node(node)
    except Exception:
        return None

def eval_node(node):
    if isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.BinOp):
        return ALLOWED_OPERATORS[type(node.op)](
            eval_node(node.left), eval_node(node.right)
        )
    elif isinstance(node, ast.UnaryOp):
        return ALLOWED_OPERATORS[type(node.op)](eval_node(node.operand))
    else:
        raise TypeError("Invalid expression")

# -----------------------------
# Command Handlers
# -----------------------------
@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(
        message,
        (
            "سلام! 👋 من «OstadBot» هستم.\n"
            "یک ربات دستیار هوشمند برای کمک در درس‌ها، آزمون‌ها و اطلاعات عمومی.\n"
            "می‌تونی از من سوالت رو بپرسی مثل:\n"
            "🔹 سوال ریاضی: 5*(3+2)\n"
            "🔹 سوال درسی: شب امتحان چه بخونم؟\n"
            "🔹 سوال عمومی: چرا آسمان آبیه؟"
        )
    )

# -----------------------------
# Main message handler
# -----------------------------
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.strip().lower()

    # Math evaluation
    if any(c.isdigit() for c in text) and any(opr in text for opr in "+-*/^"):
        result = eval_expr(text)
        if result is not None:
            bot.reply_to(message, f"✅ حاصل عبارت: {result}")
            return

    # General educational responses
    if "امتحان" in text or "درس" in text:
        bot.reply_to(
            message,
            "برای موفقیت در درس‌ها تمرکز، خلاصه‌نویسی و تمرین مکرر مهمه 💪 "
            "می‌خوای راهنمای هر درس رو برات بفرستم؟"
        )
    elif "آزمون" in text:
        bot.reply_to(
            message,
            "قبل از آزمون حتماً نمونه‌سوال‌ تمرین کن و مفاهیم پایه رو مرور کن 📘"
        )
    elif "اطلاعات" in text or "عمومی" in text:
        bot.reply_to(
            message,
            "من می‌تونم برات سوالات عمومی رو پاسخ بدم؛ فقط بپرس 🤖"
        )
    else:
        bot.reply_to(
            message,
            "سوالت رو بپرس! من برای ریاضی، آزمون، اطلاعات عمومی یا هر موضوع درسی آماده‌ام 📚"
        )

# -----------------------------
# Stable polling loop for Railway
# -----------------------------
print("✅ OstadBot is running...", flush=True)
while True:
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
    except Exception as e:
        print(f"❌ Polling error: {e}", flush=True)
        time.sleep(5)
