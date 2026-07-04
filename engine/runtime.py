import asyncio

from core.logger import Logger
from core.boot import Boot

from system.health import Health
from system.security import Security

from infra.service_registry import ServiceRegistry

from coinex.engine import CoinExEngine  # ✅ اضافه شد


class Runtime:
    """
    Main runtime engine of CryptoPulseAI
    """

    def __init__(self):
        self.logger = Logger()
        self.boot = Boot()
        self.running = True

        # =========================
        # 🔌 CORE MODULES
        # =========================
        self.telegram = None  # فعلاً بعداً وصل میشه
        self.ai = None        # فعلاً بعداً وصل میشه
        self.signal = None    # فعلاً بعداً وصل میشه

        # =========================
        # 💰 COINEX ENGINE
        # =========================
        self.coinex = CoinExEngine()

    async def initialize(self):
        """
        Initialize full system
        """
        self.logger.info("🚀 Initializing CryptoPulseAI Runtime...")

        await self.boot.start()

        # Register services globally
        ServiceRegistry.register("logger", self.logger)
        ServiceRegistry.register("health", Health)
        ServiceRegistry.register("coinex", self.coinex)

        self.logger.info("📦 Services registered successfully")

    async def system_monitor(self):
        """
        Main monitoring loop
        """
        while self.running:
            status = Health.status()

            self.logger.info(
                f"📊 CPU:{status['cpu']}% | RAM:{status['ram']}% | Uptime:{status['uptime_sec']}s"
            )

            await asyncio.sleep(5)

    async def market_monitor(self):
        """
        💰 CoinEx live market signal loop
        """
        while self.running:
            try:
                signal = self.coinex.get_price_change_signal("BTCUSDT")

                self.logger.info(f"💰 Market Signal: {signal}")

            except Exception as e:
                self.logger.error(f"⚠️ CoinEx error: {e}")

            await asyncio.sleep(10)

    async def run(self):
        """
        Main runtime entry point
        """
        await self.initialize()

        self.logger.info("🔥 System LIVE")

        # =========================
        # 🔁 PARALLEL TASKS
        # =========================
        monitor_task = asyncio.create_task(self.system_monitor())
        market_task = asyncio.create_task(self.market_monitor())

        await asyncio.gather(monitor_task, market_task)
