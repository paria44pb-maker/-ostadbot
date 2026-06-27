import random

def generate_signal(price, rsi, volume):
    score = 0

    if rsi < 30:
        score += 40
    if rsi > 70:
        score -= 40
    if volume > 1000000:
        score += 20

    if score > 50:
        return {
            "signal": "BUY",
            "confidence": min(95, score)
        }

    elif score < -30:
        return {
            "signal": "SELL",
            "confidence": min(95, abs(score))
        }

    return {
        "signal": "HOLD",
        "confidence": 40
    }
