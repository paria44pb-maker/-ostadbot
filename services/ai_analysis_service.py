import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def analyze(text):

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model":"llama-3.1-8b-instant",
        "messages":[
            {"role":"system","content":"crypto analyst"},
            {"role":"user","content":text}
        ]
    }

    r = requests.post(url,json=payload,headers=headers)

    data = r.json()

    if "choices" not in data:
        return "خطا در تحلیل"

    return data["choices"][0]["message"]["content"]
