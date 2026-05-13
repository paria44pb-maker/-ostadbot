import os
import requests


GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# مدل‌های قابل تنظیم
FAST_MODEL = "llama-3.1-8b-instant"
STRONG_MODEL = "llama-3.1-70b-versatile"


def ask_groq(user_message: str, strong: bool = False):
    """
    strong = True  →  مدل 70B برای پاسخ‌های قوی و طولانی
    strong = False →  مدل سریع 8B
    """

    if not GROQ_API_KEY:
        return "❌ خطا: متغیر GROQ_API_KEY تنظیم نشده است."

    model_to_use = STRONG_MODEL if strong else FAST_MODEL

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}",
    }

    payload = {
        "model": model_to_use,
        "messages": [
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(
            GROQ_URL,
            json=payload,
            headers=headers,
            timeout=20
        )

        data = response.json()

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"❌ خطا در اتصال به Groq: {e}"
