import hashlib
from datetime import datetime
from ai.groq_client import GroqClient
from db.models import Session, AIMessage

class ContentGenerator:
    def __init__(self):
        self.groq = GroqClient()
        self.topics = [
            "تحلیل تکنیکال بیت‌کوین در تایم‌فریم روزانه",
            "تأثیر اخبار اقتصادی بر قیمت اتریوم",
            "تشخیص تله‌های گاوی و خرسی در بازار کریپتو",
            "آموزش الگوهای کندل استیک معروف",
            "مدیریت ریسک و حد ضرر پویا با ATR",
            "واگرایی RSI و سیگنال‌های برگشتی",
            "نقش وال‌ها و نهنگ‌ها در حرکت بازار",
            "استراتژی سوئینگ تریدینگ با EMA و MACD"
        ]
        self.last_hashes = set()

    async def generate_unique_content(self):
        """تولید محتوای غیرتکراری با Groq"""
        # انتخاب موضوع تصادفی
        import random
        topic = random.choice(self.topics)
        
        prompt = f"""
        یک تحلیل حرفه‌ای و کامل درباره "{topic}" بنویس.
        طول متن حدود ۵۰۰ تا ۱۰۰۰ کاراکتر باشد.
        شامل نکات آموزشی، تحلیل بازار و توصیه معاملاتی.
        از ایموجی‌های مرتبط استفاده کن.
        """
        
        content = await self.groq.generate(prompt, max_tokens=800)
        if not content:
            return None
        
        # بررسی یکتایی محتوا با هش
        content_hash = hashlib.md5(content.encode()).hexdigest()
        if content_hash in self.last_hashes:
            return None  # تکراری
        
        self.last_hashes.add(content_hash)
        if len(self.last_hashes) > 50:
            self.last_hashes.clear()
        
        # ذخیره در دیتابیس
        session = Session()
        ai_msg = AIMessage(content=content, content_hash=content_hash, created_at=datetime.utcnow())
        session.add(ai_msg)
        session.commit()
        session.close()
        
        return content
