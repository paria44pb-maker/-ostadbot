def choose_ai(text):

    coding_words = [
        "کد", "پایتون", "ربات",
        "برنامه", "تحلیل", "اندیکاتور"
    ]

    for word in coding_words:
        if word in text:
            return "deepseek"

    return "groq"
