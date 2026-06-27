def score_signal(signal, market):
    base = signal["confidence"]

    volatility = market.get("volatility", 1)

    if volatility > 2:
        base -= 10

    return max(0, min(100, base))
