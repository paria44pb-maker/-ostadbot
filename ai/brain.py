if "کد" in text or "برنامه" in text:
    model = "deepseek"

elif "تحلیل" in text or "ارز" in text:
    model = "deepseek"

else:
    model = "groq"
