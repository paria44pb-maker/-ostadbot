import requests
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def analyze_market(btc_price, btc_usd):

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
You are a professional crypto market analyst.

Bitcoin price in IRR: {btc_price}
Bitcoin price in USD: {btc_usd}

Give:
1) Short technical insight
2) Market sentiment
3) Simple signal (BUY / SELL / HOLD)
Keep it short and professional.
Answer in Persian.
"""

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You are a crypto expert."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    r = requests.post(url, json=payload, headers=headers)

    if "choices" not in r.json():
        return "خطا در تحلیل بازار"

    return r.json()["choices"][0]["message"]["content"]
