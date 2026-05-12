import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

def generate_answer(question, history=None):
    try:
        response = model.generate_content(question)
        return response.text
    except Exception as e:
        print("AI ERROR:", e)
        return "❌ خطا در ارتباط با هوش مصنوعی."
