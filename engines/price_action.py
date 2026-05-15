def market_structure(df):

    last = df.iloc[-1]

    ema20 = last["ema20"]
    ema50 = last["ema50"]

    if ema20 > ema50:
        trend = "bullish"
    else:
        trend = "bearish"

    rsi = last["rsi"]

    if rsi > 70:
        momentum = "overbought"
    elif rsi < 30:
        momentum = "oversold"
    else:
        momentum = "neutral"

    return {
        "trend": trend,
        "momentum": momentum,
        "rsi": round(rsi,2)
    }
