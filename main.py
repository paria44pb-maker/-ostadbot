import os
import requests
import json

def call_groq(prompt: str):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ متغیر محیطی GROQ_API_KEY تنظیم نشده!")
        return

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=25)
        print("🔵 وضعیت پاسخ:", res.status_code)
        print("🔵 پاسخ کامل:", res.text)

        if res.status_code == 200:
            data = res.json()
            answer = data["choices"][0]["message"]["content"]
            print("\n🤖 پاسخ هوش مصنوعی:\n", answer)

    except Exception as e:
        print("❌ خطا در درخواست:", repr(e))


if __name__ == "__main__":
    print("=== شروع تست اتصال به Groq n")
    call_groq("سلام. لطفا ثابت کن که اتصال برقرار است.")
    print("\n=== پایان تست ===")
