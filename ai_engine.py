import google.generativeai as genai
from config import GEMINI_API_KEY
from utils import detect_level, detect_request_type

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash-latest")

SYSTEM_PROMPT = """
تو یک استاد هوش مصنوعی آموزشی بسیار حرفه‌ای هستی.
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

پیام کاربر:
{user_text}

حالا یک پاسخ حرفه‌ای، آموزشی، دقیق و کاملاً فارسی تولید کن.
"""

    try:
        response = model.generate_content(prompt)

        if response and hasattr(response, "text"):
            return response.text.strip()

        return "پاسخی تولید نشد."

    except Exception as e:
        print("GEMINI ERROR:", e)

        return (
            "⚠️ سرور هوش مصنوعی موقتاً پاسخ نمی‌دهد.\n"
            "لطفاً چند لحظه دیگر دوباره امتحان کنید."
        )
