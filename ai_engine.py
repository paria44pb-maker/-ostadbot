import google.generativeai as genai
from config import GEMINI_API_KEY
from utils import detect_level, detect_request_type

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

SYSTEM_PROMPT = """
تو یک استاد هوش مصنوعی آموزشی بسیار حرفه‌ای هستی.

قوانین پاسخ‌دهی:
- پاسخ‌ها باید دقیق، علمی، فارسی و ساختاریافته باشند.
- متناسب با سطح کاربر توضیح بده: ابتدایی، متوسطه، دبیرستان، دانشگاهی.
- اگر سوال مفهومی بود، ساده و روشن توضیح بده.
- اگر سوال حل مسئله بود، مرحله‌به‌مرحله حل کن.
- اگر سوال برنامه‌نویسی بود، کد تمیز، استاندارد و قابل اجرا بده.
- اگر لازم بود مثال بزن.
- اگر لازم بود نکات مهم را بولت‌وار بیان کن.
- از پاسخ‌های مبهم، کوتاهِ بی‌فایده یا نامرتب خودداری کن.
"""

def generate_answer(user_text: str, history: list[str]) -> str:
    level = detect_level(user_text)
    req_type = detect_request_type(user_text)
    history_text = "\n".join(history[-6:]) if history else "ندارد"

    prompt = f"""
{SYSTEM_PROMPT}

سطح کاربر: {level}
نوع درخواست: {req_type}

سابقه مکالمه:
{history_text}

پیام کاربر:
{user_text}

حالا یک پاسخ حرفه‌ای، آموزشی، دقیق و کاملاً فارسی تولید کن.
"""
    response = model.generate_content(prompt)

    if hasattr(response, "text") and response.text:
        return response.text.strip()

    return "در حال حاضر پاسخ مناسبی پیدا نشد."
