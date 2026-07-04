import asyncio

from core.logger import Logger
from core.boot import Boot

from system.health import Health

from infra.service_registry import ServiceRegistry

from coinex.engine import CoinExEngine

from engine.live_trader import LiveTrader


class Runtime:
    """
    Main runtime engine of CryptoPulseAI
    """

    def __init__(self):
        self.logger = Logger()
        self.boot = Boot()
        self.running = True

        # =========================
        # 💰 MARKET ENGINE
        # =========================
        self.coinex = CoinExEngine()

        # =========================
        # 🧠 LIVE TRADER ENGINE
        # =========================
        self.trader = LiveTrader(balance=100)

    # =========================
    # 🚀 INITIALIZATION
    # =========================
    async def initialize(self):
        self.logger.info("🚀 Initializing CryptoPulseAI Runtime...")

        await self.boot.start()

        # Register global services
        ServiceRegistry.register("logger", self.logger)
        ServiceRegistry.register("health", Health)
        ServiceRegistry.register("coinex", self.coinex)
        ServiceRegistry.register("trader", self.trader)

        self.logger.info("📦 All services registered")

    # =========================
    # 📊 SYSTEM MONITOR
    # =========================
    async def system_monitor(self):
        while self.running:
            status = Health.status()

            self.logger.info(
                f"📊 CPU:{status['cpu']}% | RAM:{status['ram']}% | Uptime:{status['uptime_sec']}s"
            )

            await asyncio.sleep(5)

    # =========================
    # 💰 MARKET WATCH (CoinEx)
    # =========================
    async def market_monitor(self):
        while self.running:
            try:
                signal = self.coinex.get_price_change_signal("BTCUSDT")
                self.logger.info(f"💰 CoinEx Signal: {signal}")

            except Exception as e:
                self.logger.error(f"⚠️ CoinEx Error: {e}")

            await asyncio.sleep(10)

    # =========================
    # 🧠 LIVE TRADING ENGINE
    # =========================
    async def trading_loop(self):
        """
        Runs AI + TA + Risk + Execution system
        """
        await self.trader.run()

    # =========================
    # 🔁 MAIN RUNNER
    # =========================
    async def run(self):
        await self.initialize()

        self.logger.info("🔥 CryptoPulseAI SYSTEM IS LIVE")

        # =========================
        # PARALLEL TASKS
        # =========================
        system_task = asyncio.create_task(self.system_monitor())
        market_task = asyncio.create_task(self.market_monitor())
        trader_task = asyncio.create_task(self.trading_loop())

        await asyncio.gather(
            system_task,
            market_task,
            trader_task
        )
