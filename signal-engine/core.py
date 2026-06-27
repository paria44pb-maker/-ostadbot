def generate_signal(ai, smc, market):
    score = 0

    score += ai.get("confidence", 0)
    score += smc.get("score", 0)

    if market["trend"] == "bullish":
        score += 20
    if market["volatility"] > 2:
        score -= 10

    if score > 80:
        return {"signal": "STRONG BUY", "score": score}
    elif score < 30:
        return {"signal": "STRONG SELL", "score": score}

    return {"signal": "HOLD", "score": score}
