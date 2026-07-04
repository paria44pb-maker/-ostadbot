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
        # 🧠 TRADER (IMPORTANT FIX)
        # =========================
        self.trader = LiveTrader(balance=100)

    # =========================
    # 🚀 INIT
    # =========================
    async def initialize(self):
        self.logger.info("🚀 Initializing CryptoPulseAI Runtime...")

        await self.boot.start()

        ServiceRegistry.register("logger", self.logger)
        ServiceRegistry.register("health", Health)
        ServiceRegistry.register("coinex", self.coinex)
        ServiceRegistry.register("trader", self.trader)

        self.logger.info("📦 Services registered")

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
    # 💰 MARKET MONITOR
    # =========================
    async def market_monitor(self):
        while self.running:
            signal = self.coinex.get_price_change_signal("BTCUSDT")
            self.logger.info(f"💰 CoinEx Signal: {signal}")

            await asyncio.sleep(10)

    # =========================
    # 🧠 TRADING LOOP WRAPPER
    # =========================
    async def trader_runner(self):
        """
        Wrapper for LiveTrader.run()
        """
        await self.trader.run()

    # =========================
    # 🔁 MAIN RUN
    # =========================
    async def run(self):
        await self.initialize()

        self.logger.info("🔥 SYSTEM IS LIVE")

        # ✅ درست و استاندارد (اینجا fix اصلیه)
        monitor_task = asyncio.create_task(self.system_monitor())
        market_task = asyncio.create_task(self.market_monitor())
        trader_task = asyncio.create_task(self.trader_runner())

        await asyncio.gather(
            monitor_task,
            market_task,
            trader_task
        )
