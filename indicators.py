import pandas as pd

# --------------------
# RSI
# --------------------

def calculate_rsi(series, period=14):

    delta = series.diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()

    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi

# --------------------
# EMA
# --------------------

def calculate_ema(series, period):

    return series.ewm(span=period, adjust=False).mean()

# --------------------
# MACD
# --------------------

def calculate_macd(series):

    ema12 = calculate_ema(series, 12)

    ema26 = calculate_ema(series, 26)

    macd = ema12 - ema26

    signal = macd.ewm(span=9, adjust=False).mean()

    return macd, signal

# --------------------
# APPLY
# --------------------

def apply_indicators(df):

    df["rsi"] = calculate_rsi(df["close"])

    macd, signal = calculate_macd(df["close"])

    df["macd"] = macd

    df["macd_signal"] = signal

    df["ema50"] = calculate_ema(df["close"], 50)

    df["ema200"] = calculate_ema(df["close"], 200)

    return df
