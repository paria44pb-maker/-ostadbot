import logging
from config.settings import RR_RATIO

logger = logging.getLogger(__name__)

class StrategyManager:
    def decide(self, score_4h, score_1h, score_15m):
        """تصمیم‌گیری نهایی بر اساس چند بازه زمانی"""
        if score_4h >= 40 and score_1h >= 20 and score_15m >= 10:
            return {
                'action': 'BUY',
                'confidence': min(95, 50 + score_4h // 2),
                'strength': score_4h + score_1h + score_15m,
                'timeframes': {'4h': score_4h, '1h': score_1h, '15m': score_15m}
            }
        elif score_4h <= -40 and score_1h <= -20 and score_15m <= -10:
            return {
                'action': 'SELL',
                'confidence': min(95, 50 - score_4h // 2),
                'strength': abs(score_4h + score_1h + score_15m),
                'timeframes': {'4h': score_4h, '1h': score_1h, '15m': score_15m}
            }
        else:
            return {'action': 'HOLD', 'confidence': 0, 'strength': 0, 'timeframes': {}}

    def calculate_entry_price(self, symbol, action, current_price):
        """محاسبه قیمت ورود بر اساس سیگنال"""
        if action == 'BUY':
            return current_price * 0.995  # 0.5% بالاتر برای اطمینان از اجرا
        elif action == 'SELL':
            return current_price * 1.005
        return current_price
