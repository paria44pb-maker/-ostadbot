import httpx
import logging
from config.settings import GROQ_API_KEY

logger = logging.getLogger(__name__)

class GroqClient:
    def __init__(self):
        self.api_key = GROQ_API_KEY
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"

    async def generate(self, prompt, max_tokens=1000):
        if not self.api_key:
            logger.error("GROQ_API_KEY not set")
            return None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(self.base_url, json=payload, headers=headers)
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
                else:
                    logger.error(f"Groq API error: {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Groq request failed: {e}")
            return None
