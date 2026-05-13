def ask_groq(user_message):
    if not GROQ_API_KEY:
        return "❌ خطا: متغیر GROQ_API_KEY تنظیم نشده است."

    if not isinstance(user_message, str):
        # اگر رشته نیست، به رشته تبدیلش کن
        user_message = str(user_message)

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
        response = requests.post(GROQ_URL, json=payload, headers=headers, timeout=20)
        data = response.json()

        if "choices" not in data:
            return f"❌ خطای Groq API: پاسخ نامناسب:\n{data}"

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"❌ خطا در اتصال به Groq: {e}"
