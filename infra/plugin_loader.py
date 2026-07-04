import importlib
import logging


class PluginLoader:
    """
    Loads all system parts dynamically
    """

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger("CryptoPulseAI")
        self.plugins = {}

    def load(self, module_name: str):
        try:
            module = importlib.import_module(module_name)
            self.plugins[module_name] = module
            self.logger.info(f"✅ Loaded {module_name}")
            return module

        except Exception as e:
            self.logger.error(f"❌ Failed to load {module_name}: {e}")
            return None

    def load_all(self, start=2, end=21):
        """
        Load part2 to part20 automatically
        """
        for i in range(start, end):
            self.load(f"part{i}")
