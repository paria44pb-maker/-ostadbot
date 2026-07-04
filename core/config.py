import os

class Config:
    """
    Central configuration system
    """

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    ADMIN_IDS = os.getenv("ADMIN_IDS", "")

    COINEX_API_KEY = os.getenv("COINEX_API_KEY")
    COINEX_SECRET_KEY = os.getenv("COINEX_SECRET_KEY")

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    @staticmethod
    def validate():
        required = [
            Config.TELEGRAM_BOT_TOKEN,
            Config.COINEX_API_KEY,
            Config.COINEX_SECRET_KEY
        ]

        missing = [x for x in required if not x]

        if missing:
            raise Exception(f"Missing env keys: {len(missing)}")

        return True
