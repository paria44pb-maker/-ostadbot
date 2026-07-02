#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot - Safe 15 Parts Loader
Production-safe dynamic module loader with custom API server
"""

import os
import sys
import importlib
import traceback
import asyncio
import uvicorn
import threading
from datetime import datetime

# ============================================================
#                    FIX ENV (Railway)
# ============================================================

if "Telegram _bot_token" in os.environ:
    os.environ["BOT_TOKEN"] = os.environ["Telegram _bot_token"]
    print("🔧 Mapped Telegram _bot_token → BOT_TOKEN")

# Also set custom API server if needed
if "TELEGRAM_API_SERVER" not in os.environ:
    # Use local API server or proxy
    # os.environ["TELEGRAM_API_SERVER"] = "https://api.telegram.org"  # default
    pass

# ============================================================
#                    لیست پارت‌ها
# ============================================================

PARTS = [
    "part1", "part2", "part3", "part4", "part5",
    "part6", "part7", "part8", "part9", "part10",
    "part11", "part12", "part13", "part14", "part15"
]

loaded_modules = {}

# ============================================================
#                    SAFE LOADER
# ============================================================

def load_part(module_name: str):
    try:
        module = importlib.import_module(module_name)
        loaded_modules[module_name] = module
        print(f"✅ Loaded: {module_name}")
        return module
    except Exception as e:
        print(f"❌ Failed: {module_name}")
        print(traceback.format_exc())
        return None


def load_all_parts():
    token = os.environ.get("BOT_TOKEN", "")
    if not token:
        print("❌ BOT_TOKEN not set!")
    else:
        print(f"✅ BOT_TOKEN found: {token[:8]}...")

    print("\n🚀 Loading 15 Parts...\n")

    for part in PARTS:
        load_part(part)

    print("\n" + "=" * 50)
    print(f"✅ Loaded: {len(loaded_modules)}/{len(PARTS)}")
    print("=" * 50 + "\n")


# ============================================================
#                    TELEGRAM BOT
# ============================================================

async def start_bot():
    try:
        part9 = loaded_modules.get("part9")

        if not part9:
            print("❌ part9 not loaded")
            return

        if not hasattr(part9, "get_application"):
            print("❌ get_application not found in part9")
            return

        app = part9.get_application()

        if not app:
            print("⚠️ Bot not found in part9 fallback mode")
            return

        print("🔄 Initializing bot...")
        await app.initialize()
        print("▶️ Starting bot...")
        await app.start()
        print("📡 Starting polling...")
        await app.updater.start_polling(drop_pending_updates=True)
        print("🤖 Telegram bot started successfully!")
        print("💡 Bot is now polling for messages...")

    except Exception as e:
        print(f"❌ Bot Error: {e}")
        traceback.print_exc()


# ============================================================
#                    HEALTH SERVER (Keep Railway alive)
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

health_app = FastAPI()

health_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@health_app.get("/")
async def root():
    return {"status": "alive", "bot": "CryptoPulse"}

@health_app.get("/health")
async def health():
    return {"status": "ok"}

def run_health_server():
    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run(health_app, host="0.0.0.0", port=port, log_level="warning")


# ============================================================
#                    MAIN
# ============================================================

async def main():
    print("=" * 50)
    print("🚀 CryptoPulse AI Bot v3.5")
    print(f"⏰ {datetime.now()}")
    print("=" * 50 + "\n")

    # 1. Load all modules
    load_all_parts()

    # 2. Start health server in thread
    server_thread = threading.Thread(target=run_health_server, daemon=True)
    server_thread.start()
    print("🏥 Health server started")

    # 3. Start bot
    await start_bot()

    # 4. Keep alive
    print("\n✅ Bot is running. Press Ctrl+C to stop.")
    await asyncio.Event().wait()


# ============================================================
#                    RUN
# ============================================================

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Stopped")
    except Exception as e:
        print(f"❌ Fatal: {e}")
        traceback.print_exc()
