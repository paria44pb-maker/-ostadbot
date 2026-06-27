from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_market(payload):
    system = """
    You are an institutional trading AI.
    You must:
    - Detect Smart Money concepts
    - Evaluate risk
    - Output structured JSON
    - NEVER guarantee profit
    """

    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": str(payload)}
        ]
    )

    return res.choices[0].message.content
