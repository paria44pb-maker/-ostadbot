#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot - Safe 15 Parts Loader
Production-safe dynamic module loader
"""

import importlib
import traceback
import asyncio
import uvicorn
from datetime import datetime

# ============================================================
#                    لیست پارت‌ها
# ============================================================

PARTS = [
    "part1",
    "part2",
    "part3",
    "part4",
    "part5",
    "part6",
    "part7",
    "part8",
    "part9",
    "part10",
    "part11",
    "part12",
    "part13",
    "part14",
    "part15"
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
    print("\n🚀 Loading 15 Parts...\n")

    for part in PARTS:
        load_part(part)

    print("\n" + "=" * 50)
    print(f"✅ Loaded modules: {len(loaded_modules)}/{len(PARTS)}")
    print("=" * 50 + "\n")

# ============================================================
#                    FASTAPI (optional part13)
# ============================================================

def start_api():
    try:
        part13 = loaded_modules.get("part13")

        if part13 and hasattr(part13, "app"):
            print("🌐 Starting FastAPI from part13...")
            uvicorn.run(part13.app, host="0.0.0.0", port=8080)
        else:
            print("⚠️ FastAPI app not found in part13")

    except Exception as e:
        print(f"❌ API Error: {e}")

# ============================================================
#                    TELEGRAM BOT (part9)
# ============================================================

async def start_bot():
    try:
        part9 = loaded_modules.get("part9")

        if part9 and hasattr(part9, "get_application"):
            app = part9.get_application()

            if app:
                await app.initialize()
                await app.start()
                await app.updater.start_polling()
                print("🤖 Telegram bot started successfully!")
                return

        print("⚠️ Bot not found in part9 fallback mode")

    except Exception as e:
        print(f"❌ Bot Error: {e}")
        traceback.print_exc()

# ============================================================
#                    MAIN
# ============================================================

async def main():
    print("🚀 CryptoPulse AI Bot Starting...")
    print(f"⏰ {datetime.now()}\n")

    # 1. Load all modules
    load_all_parts()

    # 2. Start bot + API together
    bot_task = asyncio.create_task(start_bot())

    # API in background thread (safe)
    import threading
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()

    # 3. Keep alive
    await bot_task
    await asyncio.Event().wait()


# ============================================================
#                    RUN
# ============================================================

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Stopped manually")
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
        traceback.print_exc()
