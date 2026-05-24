import asyncio
import logging
from core.exchange_coinex import CoinExExchange
from core.data_fetcher import DataFetcher
from core.technical_engine import TechnicalEngine
from core.strategy_manager import StrategyManager
from core.risk_manager import RiskManager
from core.order_manager import OrderManager
from ai.content_generator import ContentGenerator
from telegram_bot.bot import TelegramBot
from telegram_bot.notifier import TelegramNotifier
from db.db_session import init_db
from config.settings import SYMBOLS, AUTO_TRADE_ENABLED

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self):
        self.exchange = CoinExExchange()
        self.data_fetcher = DataFetcher(self.exchange)
        self.strategy = StrategyManager()
        self.risk_manager = RiskManager()
        self.order_manager = OrderManager(self.exchange, self.risk_manager)
        self.content_gen = ContentGenerator()
        self.notifier = TelegramNotifier()
        self.telegram_bot = TelegramBot()

    async def trading_cycle(self):
        while True:
            for symbol in SYMBOLS:
                try:
                    # دریافت داده‌های چند بازه
                    df_4h = await self.data_fetcher.fetch_ohlcv(symbol, '4h', 200)
                    df_1h = await self.data_fetcher.fetch_ohlcv(symbol, '1h', 200)
                    df_15m = await self.data_fetcher.fetch_ohlcv(symbol, '15m', 200)
                    
                    if df_4h is None or df_1h is None or df_15m is None:
                        continue
                    
                    # تحلیل تکنیکال
                    tech_4h = TechnicalEngine(df_4h)
                    tech_4h.calculate_all_indicators()
                    score_4h, _, _ = tech_4h.score_indicators()
                    
                    tech_1h = TechnicalEngine(df_1h)
                    tech_1h.calculate_all_indicators()
                    score_1h, _, signals_1h = tech_1h.score_indicators()
                    
                    tech_15m = TechnicalEngine(df_15m)
                    tech_15m.calculate_all_indicators()
                    score_15m, _, signals_15m = tech_15m.score_indicators()
                    
                    # تصمیم‌گیری
                    signal = self.strategy.decide(score_4h, score_1h, score_15m)
                    if signal['action'] != 'HOLD':
                        current_price = await self.data_fetcher.fetch_current_price(symbol)
                        signal['symbol'] = symbol
                        signal['price'] = current_price
                        signal['stop_loss'] = current_price * 0.97 if signal['action'] == 'BUY' else current_price * 1.03
                        signal['take_profit'] = current_price * 1.04 if signal['action'] == 'BUY' else current_price * 0.96
                        
                        # ارسال سیگنال به کانال
                        await self.notifier.send_signal(signal, signals_1h, signals_15m)
                        
                        # معامله خودکار
                        if AUTO_TRADE_ENABLED:
                            await self.order_manager.execute_trade(signal)
                    
                except Exception as e:
                    logger.error(f"Error in cycle for {symbol}: {e}")
            
            await asyncio.sleep(300)  # 5 دقیقه

    async def ai_content_cycle(self):
        while True:
            try:
                content = await self.content_gen.generate_unique_content()
                if content:
                    await self.notifier.send_ai_content(content)
                await asyncio.sleep(7200)  # 2 ساعت
            except Exception as e:
                logger.error(f"AI content error: {e}")
                await asyncio.sleep(3600)

    async def run(self):
        await init_db()
        await self.telegram_bot.run()
        
        # اجرای حلقه‌های اصلی
        await asyncio.gather(
            self.trading_cycle(),
            self.ai_content_cycle()
        )

if __name__ == "__main__":
    bot = TradingBot()
    asyncio.run(bot.run())
