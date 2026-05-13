# price_action.py
# تشخیص ساختار بازار و پرایس اکشن

def detect_trend(prices):
    """
    تشخیص روند ساده بر اساس HH/HL
    """

    if len(prices) < 3:
        return "side"

    if prices[-1] > prices[-2] > prices[-3]:
        return "up"

    if prices[-1] < prices[-2] < prices[-3]:
        return "down"

    return "side"


def detect_liquidity_sweep(prices):
    """
    تشخیص ساده لیکوییدیتی سوئیپ
    """

    if len(prices) < 5:
        return False

    last_high = max(prices[-5:-1])

    if prices[-1] > last_high:
        return True

    return False


def detect_break_of_structure(prices):
    """
    تشخیص شکست ساختار
    """

    if len(prices) < 10:
        return False

    recent_high = max(prices[-10:-1])

    if prices[-1] > recent_high:
        return "bullish_bos"

    recent_low = min(prices[-10:-1])

    if prices[-1] < recent_low:
        return "bearish_bos"

    return None
