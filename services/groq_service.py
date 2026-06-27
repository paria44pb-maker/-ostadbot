import asyncio
from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

async def ask_groq(prompt: str, profile: str = ""):
    if not client:
        return "سرویس AI در دسترس نیست."
    loop = asyncio.get_running_loop()
    def _call():
        return client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a concise Persian crypto assistant. Never promise guaranteed profit."},
                {"role": "user", "content": f"Profile: {profile}

{prompt}"}
            ],
            temperature=0.3,
        )
    res = await loop.run_in_executor(None, _call)
    return res.choices[0].message.content.strip()
