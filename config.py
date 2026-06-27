import os
from dataclasses import dataclass


def get_env(key: str, default=None, required=False):
    value = os.getenv(key, default)

    if required and (value is None or value == ""):
        raise RuntimeError(f"❌ Missing required environment variable: {key}")

    return value


@dataclass
class Config:

    # ======================
    # TELEGRAM
    # ======================
    BOT_TOKEN: str = get_env("BOT_TOKEN", required=True)
    BOT_USERNAME: str = get_env("BOT_USERNAME", default="CryptoPulseBot")

    # ======================
    # AI SERVICES
    # ======================
    GROQ_API_KEY: str = get_env("GROQ_API_KEY", required=True)

    # (اختیاری)
    OPENAI_API_KEY: str = get_env("OPENAI_API_KEY")
    GEMINI_API_KEY: str = get_env("GEMINI_API_KEY")

    # ======================
    # EXCHANGE
    # ======================
    COINEX_KEY: str = get_env("COINEX_KEY")
    COINEX_SECRET: str = get_env("COINEX_SECRET")

    # ======================
    # DATABASE
    # ======================
    DATABASE_URL: str = get_env("DATABASE_URL", default="sqlite:///bot.db")

    # ======================
    # REDIS (اگر داشتی)
    # ======================
    REDIS_URL: str = get_env("REDIS_URL")

    # ======================
    # ADMIN
    # ======================
    ADMIN_IDS: list = [
        int(x) for x in get_env("ADMIN_IDS", default="").split(",") if x.strip().isdigit()
    ]

    # ======================
    # APP SETTINGS
    # ======================
    ENV: str = get_env("ENV", default="production")
    DEBUG: bool = get_env("DEBUG", default="False").lower() == "true"

    # ======================
    # RATE LIMITS
    # ======================
    FREE_DAILY_AI_LIMIT: int = int(get_env("FREE_DAILY_AI_LIMIT", default="5"))
    RATE_LIMIT_SECONDS: int = int(get_env("RATE_LIMIT_SECONDS", default="2"))

    # ======================
    # WEBHOOK
    # ======================
    WEBHOOK_URL: str = get_env("WEBHOOK_URL")
    WEBHOOK_SECRET: str = get_env("WEBHOOK_SECRET", default="change_me")

    # ======================
    # SUBSCRIPTION PLANS
    # ======================
    VIP_PRICE: int = int(get_env("VIP_PRICE", default="10"))
    PRO_PRICE: int = int(get_env("PRO_PRICE", default="25"))
    ELITE_PRICE: int = int(get_env("ELITE_PRICE", default="50"))
