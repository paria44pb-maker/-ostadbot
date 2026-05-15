def detect_structure(df):

    last_high = df["high"].rolling(20).max().iloc[-1]

    last_low = df["low"].rolling(20).min().iloc[-1]

    current = df["close"].iloc[-1]

    if current > last_high:
        return "BOS_BULLISH"

    if current < last_low:
        return "BOS_BEARISH"

    return "RANGE"
