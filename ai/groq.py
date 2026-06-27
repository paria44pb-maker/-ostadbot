from groq import Groq
from config import Config

client = Groq(api_key=Config.GROQ_API_KEY)

async def ask_ai(prompt):
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content
