#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot - Safe 15 Parts Loader
Production-safe dynamic module loader with Creator Page
"""

import os
import sys
import importlib
import traceback
import asyncio
import uvicorn
import threading
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ============================================================
#                    CREATOR INFO
# ============================================================

CREATOR_NAME = "Farhad Behmard"
CREATOR_TELEGRAM = "@Amir92aa"
CREATOR_GITHUB = "github.com/farhadbehmard"

# ============================================================
#                    FIX ENV (Railway)
# ============================================================

if "Telegram _bot_token" in os.environ:
    os.environ["BOT_TOKEN"] = os.environ["Telegram _bot_token"]
    print("🔧 Mapped Telegram _bot_token → BOT_TOKEN")

# ============================================================
#                    CREATOR PAGE API
# ============================================================

app = FastAPI(title="CryptoPulse AI Bot v3.5")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "bot": "CryptoPulse AI v3.5",
        "creator": CREATOR_NAME,
        "status": "online",
        "message": "🚀 Bot is running successfully!",
        "telegram": CREATOR_TELEGRAM,
        "github": CREATOR_GITHUB,
        "uptime": str(datetime.now())
    }

@app.get("/health")
async def health():
    ok = len(loaded_modules)
    return {
        "status": "healthy" if ok >= 9 else "degraded",
        "loaded": ok,
        "total": 15
    }

@app.get("/status")
async def status():
    return {
        "modules": {name: "✅" for name in loaded_modules},
        "bot_token": "✅" if BOT_TOKEN else "❌",
        "running": True
    }

# ============================================================
#                    لیست پارت‌ها
# ============================================================

PARTS = [
    "part1", "part2", "part3", "part4", "part5",
    "part6", "part7", "part8", "part9", "part10",
    "part11", "part12", "part13", "part14", "part15"
]

loaded_modules = {}
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

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
        print(f"❌ Failed: {module_name} - {str(e)[:80]}")
        return None


def load_all_parts():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not set in environment!")
        print("💡 Set it in Railway: Variables > BOT_TOKEN")
    else:
        print(f"✅ BOT_TOKEN found: {BOT_TOKEN[:8]}...")

    print(f"\n🚀 Loading 15 Parts...\n")

    for part in PARTS:
        load_part(part)
        import time
        time.sleep(0.05)

    print("\n" + "=" * 50)
    print(f"✅ Loaded modules: {len(loaded_modules)}/{len(PARTS)}")
    print("=" * 50 + "\n")


# ============================================================
#                    TELEGRAM BOT (part9)
# ============================================================

async def start_bot():
    try:
        part9 = loaded_modules.get("part9")

        if not part9:
            print("❌ part9 not loaded")
            return False

        if not hasattr(part9, "get_application"):
            print("❌ get_application() not found in part9")
            return False

        app_bot = part9.get_application()

        if not app_bot:
            print("⚠️ Bot not found in part9 fallback mode")
            print("💡 Check: BOT_TOKEN, bot2-bot8 imports")
            return False

        print("🔄 Initializing bot...")
        await app_bot.initialize()
        
        print("▶️  Starting bot...")
        await app_bot.start()
        
        print("📡 Starting polling...")
        await app_bot.updater.start_polling(drop_pending_updates=True)
        
        print("🤖 Telegram bot started successfully!")
        return True

    except Exception as e:
        print(f"❌ Bot Error: {e}")
        traceback.print_exc()
        return False


# ============================================================
#                    MAIN
# ============================================================

def run_server():
    """Run FastAPI server (blocking)"""
    port = int(os.environ.get("PORT", "8080"))
    print(f"\n🌐 Creator Page: http://0.0.0.0:{port}")
    print(f"📊 Health Check: http://0.0.0.0:{port}/health")
    print(f"📈 Status: http://0.0.0.0:{port}/status\n")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


async def main():
    print("""
╔══════════════════════════════════════════════════╗
║                                                  ║
║   🚀 CryptoPulse AI Bot v3.5                    ║
║   👑 Creator: Farhad Behmard                    ║
║   📱 Telegram: @Amir92aa                        ║
║                                                  ║
╚══════════════════════════════════════════════════╝
""")
    print(f"⏰ Start Time: {datetime.now()}\n")

    # 1. Load all parts first
    load_all_parts()

    # 2. Start FastAPI server in thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    await asyncio.sleep(2)

    # 3. Start bot polling
    success = await start_bot()

    if success:
        print("\n" + "=" * 50)
        print("✅ ALL SYSTEMS OPERATIONAL")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("⚠️  Bot failed to start, API still running")
        print("=" * 50)

    # 4. Keep alive forever
    print("\n💡 Bot is running. Press Ctrl+C to stop.\n")
    while True:
        await asyncio.sleep(3600)


# ============================================================
#                    RUN
# ============================================================

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
        traceback.print_exc()
