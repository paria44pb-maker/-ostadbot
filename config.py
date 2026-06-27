import os

class Config:
 #   BOT_TOKEN = os.getenv("BOT_TOKEN")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot.db")
    REDIS_URL = os.getenv("REDIS_URL")

    COINEX_KEY = os.getenv("COINEX_KEY")
    COINEX_SECRET = os.getenv("COINEX_SECRET")

    WEBHOOK_URL = os.getenv("WEBHOOK_URL")

    TIMEZONE = "Asia/Tehran"
