import pandas as pd
import pandas_ta as ta

def indicators(candles):

    df = pd.DataFrame(candles)

    df["rsi"] = ta.rsi(df["close"], length=14)

    df["ema20"] = ta.ema(df["close"], length=20)

    df["ema50"] = ta.ema(df["close"], length=50)

    df["macd"] = ta.macd(df["close"])["MACD_12_26_9"]

    return df
