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
            "می‌تونی از من هر سوالی بپرسی!"
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

    # Educational replies
    if "امتحان" in text or "درس" in text:
        bot.reply_to(message, "برای درس خوندن، تمرکز و تمرین مهمه. چه درسی داری؟")
    elif "آزمون" in text:
        bot.reply_to(message, "نمونه‌سوال‌ها بهترین ابزار آمادگی برای آزمون هستن.")
    else:
    

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
