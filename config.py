import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
COINEX_KEY = os.getenv("COINEX_KEY", "")
COINEX_SECRET = os.getenv("COINEX_SECRET", "")
DATABASE_URL = os.getenv("DATABASE_URL", "bot.db")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@CryptoPulse606")
FREE_DAILY_AI_LIMIT = int(os.getenv("FREE_DAILY_AI_LIMIT", "5"))
RATE_LIMIT_SECONDS = int(os.getenv("RATE_LIMIT_SECONDS", "2"))
VIP_PRICE_TOMAN = 199000
OWNER_NAME = os.getenv("OWNER_NAME", "فرهاد بهمرد")
OWNER_CARD = os.getenv("OWNER_CARD", "6063731196254479")
ADMIN_IDS = set(int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit())
