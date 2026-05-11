def detect_level(text: str) -> str:
    t = text.lower()

    if any(word in t for word in ["ابتدایی", "کودک", "بچه", "خیلی ساده", "کلاس اول", "کلاس دوم"]):
        return "ابتدایی"

    if any(word in t for word in ["متوسطه", "راهنمایی", "هفتم", "هشتم", "نهم"]):
        return "متوسطه"

    if any(word in t for word in ["دبیرستان", "کنکور", "دهم", "یازدهم", "دوازدهم", "تستی"]):
        return "دبیرستان"

    if any(word in t for word in ["دانشگاه", "مهندسی", "تحقیق", "پروژه", "مقاله", "دانشگاهی"]):
        return "دانشگاهی"

    return "عمومی"


def detect_request_type(text: str) -> str:
    t = text.lower()

    if any(word in t for word in ["حل کن", "محاسبه", "جواب", "مرحله به مرحله", "حل"]):
        return "حل مسئله"

    if any(word in t for word in ["توضیح", "یعنی چی", "مفهوم", "شرح", "آموزش"]):
        return "توضیح مفهومی"

    if any(word in t for word in ["تست", "سوال تستی", "چهارگزینه‌ای", "آزمون"]):
        return "تست"

    if any(word in t for word in ["خلاصه", "جمع‌بندی", "جمع بندی", "خلاصه کن"]):
        return "خلاصه‌سازی"

    if any(word in t for word in ["پروژه", "تحقیق", "مقاله"]):
        return "پروژه"

    if any(word in t for word in ["کد", "برنامه نویسی", "برنامه‌نویسی", "python", "java", "c++", "جاوا", "پایتون"]):
        return "برنامه‌نویسی"

    return "عمومی"
