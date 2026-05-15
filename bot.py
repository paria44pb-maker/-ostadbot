def smart_reply(user_msg: str) -> str:
    if not DEEPSEEK_API_KEY:
        return "کلید DeepSeek تنظیم نشده."

    try:
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "پاسخ کوتاه، مودب و دوستانه بده."},
                {"role": "user", "content": user_msg}
            ]
        }

        res = requests.post(url, json=payload, headers=headers, timeout=20)
        data = res.json()

        # ============================
        #      SAFE CHECKS
        # ============================

        if "error" in data:
            return f"⚠️ خطا از DeepSeek: {data['error']}"

        if "choices" not in data:
            return f"⚠️ پاسخ غیرمنتظره از DeepSeek: {data}"

        if not data["choices"]:
            return "⚠️ DeepSeek پاسخی برنگردوند!"

        # پاسخ نرمال
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"⚠️ خطای داخلی: {e}"
