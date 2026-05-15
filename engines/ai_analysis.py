import requests
from config import GROQ_API_KEY

def ai_summary(data):

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
    Analyze this crypto data:

    Trend: {data['trend']}
    RSI: {data['rsi']}
    Momentum: {data['momentum']}

    Provide a short crypto trading analysis.
    """

    payload = {
        "model":"llama-3.1-8b-instant",
        "messages":[{"role":"user","content":prompt}]
    }

    r = requests.post(url, json=payload, headers=headers)

    return r.json()["choices"][0]["message"]["content"]
