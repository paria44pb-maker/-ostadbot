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
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def make_session():
    retry = Retry(
        total=3,
        backoff_factor=1.2,           # 1.2s, 2.4s, 4.8s ...
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET", "POST")
    )
    s = requests.Session()
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.mount("http://", HTTPAdapter(max_retries=retry))
    return s

session = make_session()

def call_ai(url, headers, payload):
    # connect timeout جدا از read timeout
    return session.post(
        url,
        headers=headers,
        json=payload,
        timeout=(10, 120)   # connect=10s, read=120s
    )
