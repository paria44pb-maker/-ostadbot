import sys
from core.logger import Logger
from core.config import Config

class Boot:
    """
    System bootstrapper
    """

    def __init__(self):
        self.log = Logger()

    async def start(self):
        self.log.info("🚀 Booting CryptoPulseAI...")

        try:
            Config.validate()
            self.log.info("✅ Config OK")
        except Exception as e:
            self.log.error(f"❌ Config Error: {e}")
            sys.exit(1)

        self.log.info("🧠 System initialized")
