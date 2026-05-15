import requests
from config import BINANCE

def get_klines(symbol="BTCUSDT", interval="1h", limit=200):

    url = f"{BINANCE}/klines"

    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    r = requests.get(url, params=params)

    data = r.json()

    candles = []

    for c in data:
        candles.append({
            "open": float(c[1]),
            "high": float(c[2]),
            "low": float(c[3]),
            "close": float(c[4]),
            "volume": float(c[5])
        })

    return candles
