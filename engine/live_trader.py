import asyncio

from coinex.engine import CoinExEngine
from risk.risk_manager import RiskManager
from ai.fusion_engine import FusionEngine


class LiveTrader:
    """
    Full automated trading orchestrator
    """

    def __init__(self):
        self.coinex = CoinExEngine()
        self.risk = RiskManager(balance=100)
        self.fusion = FusionEngine()

        self.running = True

    # =========================
    # 📊 FAKE PRICE FEED (placeholder)
    # =========================
    def get_market_data(self):
        """
        Replace with real OHLCV later
        """
        import random

        base = 100
        return [base + random.randint(-5, 5) for _ in range(50)]

    # =========================
    # 💰 EXECUTE TRADE
    # =========================
    def execute_trade(self, signal, price):
        if not self.risk.is_safe_trade(signal["signal"]):
            return {"status": "blocked_by_risk"}

        size = self.risk.position_size(price)

        sl = self.risk.stop_loss(price)
        tp = self.risk.take_profit(price)

        return {
            "action": signal["signal"],
            "size": size,
            "entry": price,
            "stop_loss": sl,
            "take_profit": tp
        }

    # =========================
    # 🔁 MAIN LOOP
    # =========================
    async def run(self):
        while self.running:

            # 📊 market data
            prices = self.get_market_data()

            # 🧠 AI + TECH ANALYSIS
            analysis = self.fusion.analyze_market(prices)

            tech_signal = analysis["technical"]

            # 💰 last price
            price = prices[-1]

            # ⚙️ execute decision
            trade = self.execute_trade(tech_signal, price)

            print("🧠 AI:", analysis["ai"])
            print("📊 TECH:", tech_signal)
            print("💰 TRADE:", trade)

            print("-" * 50)

            await asyncio.sleep(5)
