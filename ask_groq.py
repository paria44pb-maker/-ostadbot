import os
from groq import Groq

# ================================
# Load API Key
# ================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY یافت نشد! لطفاً آن را در Railway تنظیم کن.")

# ================================
# Initialize Client
# ================================
client = Groq(api_key=GROQ_API_KEY)

# ================================
# Ask Groq Function
# ================================
def ask_groq(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # مدل جدید و فعال
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=4096
        )

        # متن خروجی
        return response.choices[0].message["content"]

    except Exception as e:
        # خطای کامل برای لاگ Railway
        print("🔥 خطای Groq:", e)
        return "❌ خطا در ارتباط با سرویس Groq. لطفاً بعداً دوباره امتحان کنید."
      
