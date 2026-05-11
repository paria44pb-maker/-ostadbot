import os
import re
import ast
import operator as op
import telebot

# ---------------------------------------------------
# Load BOT TOKEN
# ---------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in Railway Variables")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")


# ---------------------------------------------------
# Safe Math Evaluator (No eval – fully secure)
# ---------------------------------------------------
_ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
}

def _eval_ast(node):
    if isinstance(node, ast.Num):
        return node.n

    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_eval_ast(node.operand)

    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
        left = _eval_ast(node.left)
        right = _eval_ast(node.right)
        return _ALLOWED_OPERATORS[type(node.op)](left, right)

    raise ValueError("Unsupported expression")

def evaluate_expression(expr: str):
    try:
        tree = ast.parse(expr, mode="eval")
        return _eval_ast(tree.body)
    except Exception:
        return None


# ---------------------------------------------------
# Smart AI-style answer (simple NLP)
# ---------------------------------------------------
def ai_answer(text: str) -> str:
    normalized = text.lower().strip()

    # Greetings
    if any(word in normalized for word in ["hi", "hello", "سلام", "درود"]):
        return "سلام فرهاد عزیز! چه کمکی ازم برمیاد؟ 😊"

    # Who are you?
    if "کی هستی" in normali or "who are you" in normalized:
        return "من OstadBot هستم! دستیار باهوش و همیشه آنلاین فرهاد 🤖🔥"

    # Study Help
  if "درس" in normalized or "مشقی" in normalized:
        return "اگه سوال درسی داری، بفرست فرهاد! با بهترین توضیح جواب می‌دم 📘✨"

    # Math phrases
    if any(word i normalized for word in ["محاسبه", "چند میشه", "جواب"]):
        ex = extract_expression(text)
        if ex:
            value = evaluate_expression(ex)
            if value is not None:
                return f"نتیجه محاسبه: <b>{value}</b>"
        return "ا
