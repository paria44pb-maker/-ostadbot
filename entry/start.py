import asyncio

from engine.runtime import Runtime
from engine.event_bus import EventBus
from infra.plugin_loader import PluginLoader
from infra.folder_manager import FolderManager
from infra.dependency_checker import DependencyChecker
from infra.service_registry import ServiceRegistry

from core.logger import Logger


class SystemStarter:
    """
    Boots entire CryptoPulseAI system
    """

    def __init__(self):
        self.logger = Logger()
        self.runtime = Runtime()
        self.event_bus = EventBus()
        self.loader = PluginLoader(self.logger)

    async def bootstrap(self):
        self.logger.info("🚀 Starting CryptoPulseAI System...")

        # 1. Create folders
        FolderManager.create()
        self.logger.info("📁 Folders ready")

        # 2. Check dependencies
        DependencyChecker.check()
        self.logger.info("📦 Dependencies OK")

        # 3. Register core services
        ServiceRegistry.register("logger", self.logger)
        ServiceRegistry.register("event_bus", self.event_bus)
        ServiceRegistry.register("runtime", self.runtime)

        self.logger.info("🧠 Services registered")

        # 4. Load all plugins (Part2 → Part20)
        self.loader.load_all()

        self.logger.info("🧩 Plugins loaded")

    async def run(self):
        await self.bootstrap()

        self.logger.info("🔥 System is now LIVE")

        # Start main runtime loop
        await self.runtime.run()


# Global entry function
async def start():
    starter = SystemStarter()
    await starter.run()


# If run directly
if __name__ == "__main__":
    asyncio.run(start())
