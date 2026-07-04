# =========================================================
# 🧠 CryptoPulse AI - Part 1
# 🚀 Boot & Core System Foundation
# =========================================================

import os
import sys
import asyncio
import platform
import logging
from datetime import datetime

# =========================================================
# SECTION 1 - GLOBAL CONSTANTS
# =========================================================

PROJECT_NAME = "CryptoPulseAI"
VERSION = "1.0.0"
AUTHOR = "CryptoPulse Team"

START_TIME = datetime.utcnow()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =========================================================
# SECTION 2 - ENVIRONMENT LOADER
# =========================================================

def load_env():
    """
    Load environment variables safely
    """
    env_path = os.path.join(BASE_DIR, ".env")

    if not os.path.exists(env_path):
        print("⚠️ .env file not found!")
        return

    with open(env_path, "r", encoding="utf-8") as f:
        for line in f.readlines():
            if "=" in line and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key] = value

load_env()

# =========================================================
# SECTION 3 - CONFIG MANAGER
# =========================================================

class Config:
    """
    Central configuration manager
    """

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    ADMIN_IDS = os.getenv("ADMIN_IDS")
    CHANNEL_ID = os.getenv("CHANNEL_ID")

    COINEX_API_KEY = os.getenv("COINEX_API_KEY")
    COINEX_SECRET_KEY = os.getenv("COINEX_SECRET_KEY")

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    @staticmethod
    def validate():
        """
        Validate required configs
        """
        required = [
            Config.TELEGRAM_BOT_TOKEN,
            Config.COINEX_API_KEY,
            Config.COINEX_SECRET_KEY
        ]

        missing = [r for r in required if not r]

        if missing:
            raise Exception(f"Missing config values: {len(missing)}")

        return True
