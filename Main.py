import asyncio
import logging
import schedule
import time
from datetime import datetime
from config.settings import SYMBOLS, AUTO_TRADE_ENABLED, CHANNEL_ID
from core.exchange_coinex import CoinExExchange
from core.data_fetcher import DataFetcher
from core.technical_engine import TechnicalEngine
from core.strategy_manager import StrategyManager
from core.risk_manager import RiskManager
from core.order_manager import OrderManager
from ai.content_generator import ContentGenerator
from telegram_bot.notifier import TelegramNotifier
from db.db_session import init_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self):
        self.exchange = CoinExExchange()
        self.data_fetcher = DataFetcher(self.exchange)
        self.risk_manager = RiskManager()
        self.order_manager = OrderManager(self.exchange, self.risk_manager)
        self.notifier = TelegramNotifier()
        self.content_gen = ContentGenerator()
        self.strategy = StrategyManager()

    async def trading_cycle(self):
        for symbol in SYMBOLS:
            try:
                # دریافت داده‌های چند بازه زمانی
                data_4h = await self.data_fetcher.fetch_ohlcv(symbol, '4h', 200)
                data_1h = await self.data_fetcher.fetch_ohlcv(symbol, '1h', 200)
                data_15m = await self.data_fetcher.fetch_ohlcv(symbol, '15m', 200)
                
                if not data_4h or not data_1h or not data_15m:
                    continue
                
                # تحلیل تکنیکال
                tech_4h = TechnicalEngine(data_4h)
                tech_4h.calculate_all_indicators()
                score_4h, _, _ = tech_4h.score_indicators()
                
                tech_1h = TechnicalEngine(data_1h)
                tech_1h.calculate_all_indicators()
                score_1h, _, signals_1h = tech_1h.score_indicators()
                
                tech_15m = TechnicalEngine(data_15m)
                tech_15m.calculate_all_indicators()
                score_15m, _, signals_15m = tech_15h.score_indicators()
                
                # تصمیم نهایی بر اساس چند بازه زمانی
                final_signal = self.strategy.decide(score_4h, score_1h, score_15m)
                
                if final_signal['action'] != 'HOLD':
                    # محاسبه حجم و حد ضرر/سود
                    amount, sl, tp = self.risk_manager.calculate_position_size(
                        symbol, final_signal['price'], final_signal['action']
                    )
                    final_signal['amount'] = amount
                    final_signal['stop_loss'] = sl
                    final_signal['take_profit'] = tp
                    
                    # ارسال سیگنال به تلگرام
                    await self.notifier.send_signal(final_signal, signals_1h, signals_15m)
                    
                    # معامله خودکار (اگر فعال باشد)
                    if AUTO_TRADE_ENABLED:
                        await self.order_manager.execute_trade(final_signal)
                
                # ذخیره سیگنال در دیتابیس
                await self.save_signal(symbol, final_signal)
                
            except Exception as e:
                logger.error(f"Error in trading cycle for {symbol}: {e}")
        
        await asyncio.sleep(300)  # هر ۵ دقیقه

    async def ai_content_cycle(self):
        # تولید محتوا هر ۲ ساعت
        while True:
            try:
                content = await self.content_gen.generate_unique_content()
                if content:
                    await self.notifier.send_ai_content(content)
                await asyncio.sleep(7200)  # ۲ ساعت
            except Exception as e:
                logger.error(f"AI content error: {e}")
                await asyncio.sleep(3600)

    async def main_loop(self):
        await init_db()
        await self.notifier.send_message(CHANNEL_ID, "✅ ربات هوشمند کریپتو راه‌اندازی شد!")
        
        # اجرای همزمان دو حلقه
        await asyncio.gather(
            self.trading_cycle(),
            self.ai_content_cycle(),
            self.news_fetch_cycle()
        )

if __name__ == "__main__":
    bot = TradingBot()
    asyncio.run(bot.main_loop())
