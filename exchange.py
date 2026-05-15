import ccxt
from config import BINANCE_API_KEY, BINANCE_SECRET

exchange = ccxt.binance({
    "apiKey": BINANCE_API_KEY,
    "secret": BINANCE_SECRET,
    "enableRateLimit": True
})

def get_ohlcv(symbol="BTC/USDT", timeframe="1h", limit=300):

    data = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

    return data
