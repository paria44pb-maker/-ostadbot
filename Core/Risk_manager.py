import logging
from config.settings import RISK_PER_TRADE, ATR_MULTIPLIER_SL, RR_RATIO, MAX_POSITIONS

logger = logging.getLogger(__name__)

class RiskManager:
    def __init__(self):
        self.consecutive_losses = 0
        self.open_positions = 0

    def can_trade(self):
        if self.open_positions >= MAX_POSITIONS:
            return False
        if self.consecutive_losses >= 3:
            return False
        return True

    def calculate_position_size(self, symbol, current_price, atr, balance):
        """محاسبه حجم معامله بر اساس ریسک ثابت"""
        risk_amount = balance * RISK_PER_TRADE
        stop_distance = atr * ATR_MULTIPLIER_SL
        if stop_distance == 0:
            return 0
        position_size = risk_amount / stop_distance
        return round(position_size, 6)

    def calculate_stop_loss(self, entry_price, action, atr):
        if action == 'BUY':
            return entry_price - (atr * ATR_MULTIPLIER_SL)
        else:
            return entry_price + (atr * ATR_MULTIPLIER_SL)

    def calculate_take_profit(self, entry_price, action, stop_loss):
        distance = abs(entry_price - stop_loss)
        if action == 'BUY':
            return entry_price + (distance * RR_RATIO)
        else:
            return entry_price - (distance * RR_RATIO)

    def update_trade_result(self, is_win):
        if is_win:
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1
