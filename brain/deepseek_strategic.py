# deepseek_strategic.py
# تحلیل استراتژیک عمیق مخصوص DeepSeek

def long_term_trend(candles, news_sentiment):
    """
    candles: لیست کندل‌ها
    news_sentiment: عدد مثبت یا منفی براساس تحلیل اخبار
    """

    score = 0

    # اگر اخبار مثبت باشد → امتیاز +۱
    if news_sentiment > 0:
        score += 1

    # اگر روند ۵۰ کندل گذشته رو به بالا باشد → +۱
    if len(candles) > 50 and candles[-1]["close"] > candles[-50]["close"]:
        score += 1

    # نتیجه‌گیری:
    if score >= 2:
        return "up"
    elif score <= 0:
        return "down"
    return "side"
