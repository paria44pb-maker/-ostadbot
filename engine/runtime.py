import asyncio

from core.logger import Logger
from core.boot import Boot
from core.config import Config

from system.health import Health
from system.security import Security

from infra.service_registry import ServiceRegistry


class Runtime:
    """
    Main runtime engine of CryptoPulseAI
    """

    def __init__(self):
        self.logger = Logger()
        self.boot = Boot()
        self.running = True

    async def initialize(self):
        """
        Initialize full system
        """
        self.logger.info("🚀 Initializing Runtime Engine...")

        await self.boot.start()

        # register core services
        ServiceRegistry.register("logger", self.logger)
        ServiceRegistry.register("health", Health)

        self.logger.info("📦 Services registered")

    async def main_loop(self):
        """
        Main system loop (always running)
        """
        self.logger.info("🔁 System loop started")

        while self.running:
            try:
                status = Health.status()

                self.logger.info(
                    f"📊 CPU:{status['cpu']}% | RAM:{status['ram']}% | Uptime:{status['uptime_sec']}s"
                )

                await asyncio.sleep(5)

            except Exception as e:
                self.logger.error(f"⚠️ Runtime error: {e}")

    async def shutdown(self):
        """
        Graceful shutdown
        """
        self.logger.warning("🛑 Shutting down system...")
        self.running = False

    async def run(self):
        """
        Entry point for full system
        """
        await self.initialize()
        await self.main_loop()
