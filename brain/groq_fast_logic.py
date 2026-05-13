# groq_fast_logic.py
# تحلیل سریع ثانیه‌ای

def fast_signal(price, indicators):
    # مثال: تایم‌فریم 1s برای اسکالپ
    if indicators["rsi"] < 30 and indicators["trend"] == "up":
        return "buy"
    if indicators["rsi"] > 70 and indicators["trend"] == "down":
        return "sell"
    return "hold"
