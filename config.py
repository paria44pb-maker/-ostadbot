import os

# ================================
# TELEGRAM TOKEN
# ================================
# پشتیبانی از هر دو نام متداول برای متغیر محیطی
TELEGRAM_TOKEN = (
    os.getenv("TELEGRAM_TOKEN") or
    os.getenv("TELEGRAM_BOT_TOKEN")
)

if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN یافت نشد! لطفاً آن را در Railway → Variables تنظیم کن.")


# ================================
# GROQ API KEY (اختیاری)
# ================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# اگر استفاده نمی‌کنی نیاز نیست خطا بدهد
# ولی اگر خواستی اجباری باشد، این بخش را فعال کن:
# if not GROQ_API_KEY:
#     raise ValueError("❌ GROQ_API_KEY یافت نشد!")


# ================================
# نوبیتکس (اختیاری)
# ================================
NOBITEX_TOKEN = os.getenv("NOBITEX_TOKEN")
