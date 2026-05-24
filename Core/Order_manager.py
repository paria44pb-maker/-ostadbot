
import logging
from core.exchange_coinex import CoinExExchange
from core.risk_manager import RiskManager
from config.settings import AUTO_TRADE_ENABLED, REAL_TRADE_ENABLED

logger = logging.getLogger(__name__)

class OrderManager:
    def __init__(self, exchange: CoinExExchange, risk_manager: RiskManager):
        self.exchange = exchange
        self.risk_manager = risk_manager

    async def execute_trade(self, signal):
        if not AUTO_TRADE_ENABLED:
            logger.info(f"Auto trade disabled – signal: {signal['action']}")
            return

        if not self.risk_manager.can_trade():
            logger.warning("Cannot trade – max positions or consecutive losses reached")
            return

        symbol = signal['symbol']
        action = signal['action']
        amount = signal.get('amount', 0)
        price = signal.get('price', 0)

        if amount <= 0:
            logger.error(f"Invalid amount for {symbol}")
            return

        try:
            if REAL_TRADE_ENABLED:
                order = await self.exchange.create_order(symbol, action.lower(), amount, price)
                logger.info(f"Real order placed: {order}")
            else:
                # حالت دمو (فقط لاگ)
                logger.info(f"DEMO trade: {action} {amount} {symbol} @ {price}")
        except Exception as e:
            logger.error(f"Order execution failed: {e}")
