def score(signal, volatility, volume):
    base = signal["confidence"]

    if volatility > 2:
        base -= 10
    if volume > 1000000:
        base += 15

    return max(0, min(100, base))
