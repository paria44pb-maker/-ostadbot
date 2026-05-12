import os
import requests
from config import (
    GROQ_API_KEY,
    DEEPSEEK_API_KEY,
    GROQ_BASE_URL,
    DEEPSEEK_BASE_URL
)


class AIEngine:
    def __init__(self):
        self.models = {
            "groq": {
                "url": f"{GROQ_BASE_URL}/chat/completions",
                "key": GROQ_API_KEY,
                "default_model": "llama-3.1-70b-versatile"
            },
            "deepseek": {
                "url": f"{DEEPSEEK_BASE_URL}/chat/completions",
                "key": DEEPSEEK_API_KEY,
                "default_model": "deepseek-chat"
            }
        }

    def _request(self, provider, prompt, model=None, max_tokens=4000):
        if provider not in self.models:
            raise ValueError(f"Model provider '{provider}' not found.")

        url = self.models[provider]["url"]
        api_key = self.models[provider]["key"]
        model = model or self.models[provider]["default_model"]

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

        except requests.exceptions.Timeout:
            return "Request timeout. Please try again."

        except requests.exceptions.HTTPError as e:
            return f"HTTP error from {provider}: {str(e)}"

        except Exception as e:
            return f"Unexpected error in {provider}: {str(e)}"

    def ask_groq(self, prompt, model=None):
        return self._request("groq", prompt, model)

    def ask_deepseek(self, prompt, model=None):
        return self._request("deepseek", prompt, model)

    def smart_ask(self, prompt):
        prompt_lower = prompt.lower()

        math_keywords = ["math", "solve", "calculate", "equation", "محاسبه", "حل", "ریاضی"]
        if any(k in prompt_lower for k in math_keywords):
            return self.ask_groq(prompt)

        long_analysis = ["analyze", "تحلیل", "بررسی", "explain deeply"]
        if any(k in prompt_lower for k in long_analysis):
            return self.ask_deepseek(prompt)

        return self.ask_deepseek(prompt)
