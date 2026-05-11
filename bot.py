import os
import re
import ast
import operator as op
import telebot

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

# --- Safe math evaluator (no eval) ---
_ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}

def _safe_eval_math(expr: str) -> float:
    """
    Evaluate a math expression safely using AST.
    Supports: +, -, *, /, //, %, **, parentheses, unary +/-.
    """
    node = ast.parse(expr, mode="eval").body

    def _eval(n):
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.Num):  # older python ast
            return n.n
        if isinstance(n, ast.BinOp) and type(n.op) in _ALLOWED_OPERATORS:
            return _ALLOWED_OPERATORS[type(n.op)](_eval(n.left), _eval(n.right))
        if isinstance(n, ast.UnaryOp) and type(n.op) in _ALLOWED_OPERATORS:
            return _ALLOWED_OPERATORS[type(n.op)](_eval(n.operand))
        raise ValueError("Unsupported expression")

    return _eval(node)

def normalize_math_text(text: str) -> str:
    t = text.strip().lower()
    # Persian/Arabic digits to English digits
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    arabic_digits   = "٠١٢٣٤٥٦٧٨٩"
    for i, d in enumerate(persian_digits):
        t = t.replace(d, str(i))
    for i, d in enumerate(arabic_digits):
        t = t.replace(d, str(i))

    # common Persian operators/words
    t = t.replace("×", "*").replace("x", "*").replace("÷", "/")
    t = t.replace("ضرب", "*")
    t = t.replace("تقسیم", "/")
    t = t.replace("منهای", "-")
    t = t.replace("بعلاوه", "+").replace("به‌علاوه", "+").replace("به علاوه", "+")

    # remove spaces
    t = re.sub(r"\s+", "", t)
    return t

def looks_like_math(expr: str) -> bool:
    # allow digits, operators and parentheses only
    return bool(re.fullmatch(r"[0-9\.\+\-\*\/\%\(\)]{3,}", expr)) or "**" in expr or "//" in expr

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "سلام! من OstadBot هستم.\n"
        "یک عبارت ریاضی بفرست مثل:\n"
        "6*5\n"
        "6 ضرب 5\n"
        "12/3\n"
        "یا سوال درسی بپرس."
    )

@bot.message_handler(func=lambda m: True, content_types=["text"])
def handle_text(message):
    text = message.text or ""
    normalized = normalize_math_text(text)

    # Try math
    if looks_like_math(normalized):
        try:
            result = _safe_eval_math(normalized)
            # nice formatting: show int if exact
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            bot.reply_to(message, f"✅ نتیجه: {result}")
            return
        except Exception:
            pass

    # Fallback (echo / placeholder)
    bot.reply_to(message, f"✅ پیام شما دریافت شد.\nمتن: {text}")

if __name__ == "__main__":
    # Long-polling (works well on Railway)
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
