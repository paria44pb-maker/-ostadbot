from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM = """
You are a professional crypto trading analyst.
You generate signals ONLY with reasoning:
- trend
- volume
- risk
- entry/exit
Never guarantee profit.
Return structured JSON.
"""

async def analyze_market(data):
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": str(data)}
        ]
    )
    return res.choices[0].message.content
