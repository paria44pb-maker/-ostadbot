# groq_fast_logic.py
# تحلیل سریع ثانیه‌ای مخصوص Groq

def fast_signal(price, indicators):
    """
    price: آخرین قیمت لحظه‌ای
    indicators: دیکشنری شامل RSI، روند و ...
    """

    # مثال ساده برای نسخه اولیه:
    # اگر RSI پایین باشد و روند صعودی باشد → خرید
    if indicators.get("rsi", 50) < 30 and indicators.get("trend") == "up":
        return "buy"

    # اگر RSI بالا باشد و روند نزولی باشد → فروش
    if indicators.get("rsi", 50) > 70 and indicators.get("trend") == "down":
        return "sell"

    # در بقیه موارد → نگه‌دار
    return "hold"
