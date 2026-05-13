import os
import requests


GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

MODEL_NAME = "llama-3.1-8b-instant"


def ask_groq(user_message: str):
    if not GROQ_API_KEY:
        return "❌ خطا: متغیر GROQ_API_KEY تنظیم نشده است."

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}",
    }

    payload = {
        "model": MODEL_NAME,
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

        if "choices" not in data:
            # نمایش کل پاسخ برای debug
            return f"❌ خطای Groq API: پاسخ نامناسب:\n{data}"

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"❌ خطا در اتصال به Groq: {e}"
