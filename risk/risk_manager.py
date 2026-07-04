class RiskManager:
    """
    Controls trading risk and capital safety
    """

    def __init__(self, balance: float = 100):
        self.balance = balance
        self.max_risk_per_trade = 0.02  # 2%

    # =========================
    # 💰 POSITION SIZE
    # =========================
    def position_size(self, price: float):
        risk_amount = self.balance * self.max_risk_per_trade
        size = risk_amount / price
        return round(size, 6)

    # =========================
    # 🛑 STOP LOSS
    # =========================
    def stop_loss(self, entry_price: float, percent: float = 2):
        return entry_price * (1 - percent / 100)

    # =========================
    # 🎯 TAKE PROFIT
    # =========================
    def take_profit(self, entry_price: float, percent: float = 4):
        return entry_price * (1 + percent / 100)

    # =========================
    # ⚠️ RISK CHECK
    # =========================
    def is_safe_trade(self, signal: str):
        """
        Simple safety filter
        """
        if signal not in ["BUY", "SELL"]:
            return False

        if self.balance <= 0:
            return False

        return True
