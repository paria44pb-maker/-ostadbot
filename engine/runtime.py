import asyncio

from core.logger import Logger
from core.boot import Boot

from system.health import Health
from system.security import Security

from infra.service_registry import ServiceRegistry

# 🔌 NEW MODULES (CONNECTED)
from telegram.bot_handler import TelegramBot
from ai.groq_engine import GroqAI
from signals.signal_engine import SignalEngine


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
        self.telegram = TelegramBot()
        self.ai = GroqAI()
        self.signal = SignalEngine()

    async def initialize(self):
        """
        Initialize full system
        """
        self.logger.info("🚀 Initializing CryptoPulseAI Runtime...")

        await self.boot.start()

        # Register services globally
        ServiceRegistry.register("logger", self.logger)
        ServiceRegistry.register("health", Health)
        ServiceRegistry.register("ai", self.ai)
        ServiceRegistry.register("signal", self.signal)

        self.logger.info("📦 Services registered successfully")

    async def system_monitor(self):
        """
        Background monitoring loop
        """
        while self.running:
            status = Health.status()

            self.logger.info(
                f"📊 CPU:{status['cpu']}% | RAM:{status['ram']}% | Uptime:{status['uptime_sec']}s"
            )

            await asyncio.sleep(5)

    async def start_telegram(self):
        """
        Run telegram bot (blocking → run in thread)
        """
        self.logger.info("📡 Starting Telegram Bot...")

        loop = asyncio.get_event_loop()

        await loop.run_in_executor(None, self.telegram.run)

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
        telegram_task = asyncio.create_task(self.start_telegram())

        await asyncio.gather(monitor_task, telegram_task)
