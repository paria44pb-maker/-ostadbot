import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

def generate_answer(user_text, history):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash-latest")

        prompt = ""
        for msg in history[-10:]:
            prompt += f"{msg}\n"
        prompt += f"User: {user_text}\nAssistant:"

        response = model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": 300,
                "temperature": 0.7,
            }
        )

        return response.text

    except Exception as e:
        return f"❗ خطا در پردازش پیام: {e}"
