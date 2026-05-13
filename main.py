import os
import requests

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    print("❌ GROQ_API_KEY تنظیم نشده")
    exit()

url = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "llama-3.1-8b-instant",
    "messages": [
        {"role": "user", "content": "سلام، فقط بگو وصل شدی"}
    ]
}

try:
    r = requests.post(url, headers=headers, json=data, timeout=20)
    print("Status:", r.status_code)
    print(r.text)
except Exception as e:
    print("Error:", e)
