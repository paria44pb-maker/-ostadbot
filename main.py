import os
import requests

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    print("GROQ_API_KEY تنظیم نشده")
    exit()

url = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "llama3-8b-8192",
    "messages": [
        {
            "role": "user",
            "content": "سلام"
        }
    ]
}

try:
    response = requests.post(url, headers=headers, json=data)

    print("Status:", response.status_code)
    print(response.text)

except Exception as e:
    print("Error:", e)
