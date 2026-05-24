import ccxt
import logging
from config.settings import COINEX_API_KEY, COINEX_SECRET_KEY, COINEX_PASSPHRASE, COINEX_DEMO

logger = logging.getLogger(__name__)

class CoinExExchange:
    def __init__(self):
        self.exchange = ccxt.coinex({
            'apiKey': COINEX_API_KEY,
            'secret': COINEX_SECRET_KEY,
            'password': COINEX_PASSPHRASE,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        if COINEX_DEMO:
            self.exchange.set_sandbox_mode(True)
        self.balance = None

    async def fetch_ohlcv(self, symbol, timeframe='1h', limit=200):
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return ohlcv
        except Exception as e:
            logger.error(f"Error fetching ohlcv: {e}")
            return None

    async def fetch_ticker(self, symbol):
        try:
            return self.exchange.fetch_ticker(symbol)
        except Exception as e:
            logger.error(f"Error fetching ticker: {e}")
            return None

    async def fetch_balance(self):
        try:
            self.balance = self.exchange.fetch_balance()
            return self.balance
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return None

    async def create_order(self, symbol, side, amount, price=None, order_type='market'):
        try:
            order = self.exchange.create_order(symbol, order_type, side, amount, price)
            return order
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return None
