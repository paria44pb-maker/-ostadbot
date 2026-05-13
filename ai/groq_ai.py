from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)


def ask_groq(messages):

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages
    )

    return completion.choices[0].message.content
