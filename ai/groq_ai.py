import os
from groq import Groq

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL_NAME = "llama-3.1-8b-instant"


def ask_groq(messages):
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7,
            max_tokens=1024
        )

        return completion.choices[0].message.content.strip()

    except Exception as e:
        print(f"❌ GROQ ERROR: {e}")
        return "❌ در ارتباط با مدل هوش مصنوعی خطایی رخ داد."
