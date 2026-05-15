def generate_signal(structure):

    trend = structure["trend"]
    momentum = structure["momentum"]

    if trend == "bullish" and momentum != "overbought":
        signal = "BUY"

    elif trend == "bearish" and momentum != "oversold":
        signal = "SELL"

    else:
        signal = "NEUTRAL"

    return signal
