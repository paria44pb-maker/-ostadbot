import os
from dataclasses import dataclass, field
from typing import List


def get_env(key: str, default=None, required=False):
    value = os.getenv(key, default)

    if required and (value is None or value == ""):
        raise RuntimeError(f"Missing env: {key}")

    return value


# =========================
# CONFIG CLASS
# =========================
@dataclass
class Config:

    # 🔴 BOT
    BOT_TOKEN: str = get_env("BOT_TOKEN", required=True)
    BOT_USERNAME: str = get_env("BOT_USERNAME", default="CryptoPulseBot")

    # 🔴 AI
    GROQ_API_KEY: str = get_env("GROQ_API_KEY", required=True)

    # 🔴 EXCHANGE
    COINEX_KEY: str = get_env("COINEX_KEY", default="")
    COINEX_SECRET: str = get_env("COINEX_SECRET", default="")

    # 🔴 DATABASE
    DATABASE_URL: str = get_env("DATABASE_URL", default="sqlite:///bot.db")

    # 🔴 ADMIN IDS (FIXED SAFE VERSION)
    ADMIN_IDS: List[int] = field(
        default_factory=lambda: [
            int(x) for x in get_env("ADMIN_IDS", default="").split(",") if x.strip().isdigit()
        ]
    )

    # 🔴 SYSTEM
    ENV: str = get_env("ENV", default="production")
    DEBUG: bool = get_env("DEBUG", default="false").lower() == "true"

    # 🔴 LIMITS
    FREE_DAILY_AI_LIMIT: int = int(get_env("FREE_DAILY_AI_LIMIT", default="5"))
    RATE_LIMIT_SECONDS: int = int(get_env("RATE_LIMIT_SECONDS", default="2"))

    # 🔴 WEBHOOK
    WEBHOOK_URL: str = get_env("WEBHOOK_URL", default="")
    WEBHOOK_SECRET: str = get_env("WEBHOOK_SECRET", default="change_me")

    # 🔴 PRICING
    VIP_PRICE: int = int(get_env("VIP_PRICE", default="10"))
    PRO_PRICE: int = int(get_env("PRO_PRICE", default="25"))
    ELITE_PRICE: int = int(get_env("ELITE_PRICE", default="50"))
