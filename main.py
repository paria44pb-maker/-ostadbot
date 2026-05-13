import os
import requests

def test_groq():
    url = "https://api.groq.com/openai/v1/models"
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("GROQ_API_KEY is NOT set")
        return

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        r = requests.get(url, headers=headers, timeout=20)
        print("Groq status:", r.status_code)
        print("Groq response (first 300 chars):", r.text[:300])
    except Exception as e:
        print("Groq request error:", repr(e))

def test_deepseek():
    # اگر DeepSeek را با OpenAI-compatible API صدا می‌زنی
    # آدرس دقیق ممکن است بسته به اکانت/پراوایدر متفاوت باشد.
    # برای تست، از فرم رایج استفاده می‌کنیم:
    url = "https://api.deepseek.com/chat/completions"

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("DEEPSEEK_API_KEY is NOT set")
        return

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "Say hello in Persian."}],
        "max_tokens": 20,
        "temperature": 0.2
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=25)
        print("DeepSeek status:", r.status_code)
        print("DeepSeek response (first 300 chars):", r.text[:300])
    except Exception as e:
        print("DeepSeek request error:", repr(e))

if __name__ == "__main__":
    test_groq()
    test_deepseek()
