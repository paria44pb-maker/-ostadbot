def generate_signal(ai, smc_score):
    confidence = 0

    confidence += smc_score
    confidence += ai.get("confidence", 0)

    if confidence > 75:
        return "STRONG BUY"
    elif confidence < 30:
        return "STRONG SELL"
    return "WAIT"
