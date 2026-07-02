#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot - Safe 15 Parts Loader
Production-safe dynamic module loader with Webhook support
"""

import os
import sys
import importlib
import traceback
import asyncio
import uvicorn
import threading
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# ============================================================
#                    FIX ENV (Railway)
# ============================================================

if "Telegram _bot_token" in os.environ:
    os.environ["BOT_TOKEN"] = os.environ["Telegram _bot_token"]
    print("🔧 Mapped Telegram _bot_token → BOT_TOKEN")

# ============================================================
#                    FASTAPI APP
# ============================================================

api_app = FastAPI(title="CryptoPulse Webhook")

api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store bot application
telegram_app = None

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
        print("❌ BOT_TOKEN not set in environment!")
        print("💡 Set it in Railway: Variables > BOT_TOKEN")
    else:
        print(f"✅ BOT_TOKEN found: {token[:8]}...")

    print("\n🚀 Loading 15 Parts...\n")

    for part in PARTS:
        load_part(part)

    print("\n" + "=" * 50)
    print(f"✅ Loaded modules: {len(loaded_modules)}/{len(PARTS)}")
    print("=" * 50 + "\n")


# ============================================================
#                    TELEGRAM BOT (WEBHOOK MODE)
# ============================================================

async def start_bot():
    global telegram_app

    try:
        part9 = loaded_modules.get("part9")

        if part9 and hasattr(part9, "get_application"):
            app = part9.get_application()

            if app:
                # Get Railway URL
                railway_url = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")
                port = int(os.environ.get("PORT", "8080"))

                if not railway_url:
                    # Try to construct from Railway env
                    railway_url = os.environ.get("RAILWAY_STATIC_URL", "")

                if railway_url:
                    webhook_url = f"https://{railway_url}/webhook"
                    print(f"🔗 Setting webhook: {webhook_url}")

                    await app.initialize()
                    await app.start()

                    # Set webhook
                    await app.bot.set_webhook(url=webhook_url)

                    # Store for FastAPI
                    telegram_app = app

                    print(f"🤖 Bot started with webhook on port {port}!")
                else:
                    print("⚠️ No Railway URL found, falling back to polling...")
                    await app.initialize()
                    await app.start()
                    await app.updater.start_polling()
                    print("🤖 Bot started with polling!")
                return

        print("⚠️ Bot not found in part9 fallback mode")
        print("💡 Check BOT_TOKEN in Railway Variables")

    except Exception as e:
        print(f"❌ Bot Error: {e}")
        traceback.print_exc()


# ============================================================
#                    FASTAPI ROUTES
# ============================================================

@api_app.get("/")
async def root():
    return {
        "bot": "CryptoPulse v3.5",
        "status": "online",
        "mode": "webhook" if telegram_app else "offline",
        "uptime": str(datetime.now())
    }

@api_app.get("/health")
async def health():
    ok = len(loaded_modules)
    return {
        "status": "healthy" if ok >= 9 else "degraded",
        "loaded": ok,
        "total": len(PARTS)
    }

@api_app.post("/webhook")
async def webhook(request: Request):
    """Receive Telegram updates via webhook"""
    global telegram_app

    if telegram_app:
        try:
            data = await request.json()
            await telegram_app.update_queue.put(data)
            return {"status": "ok"}
        except Exception as e:
            print(f"❌ Webhook error: {e}")
            return {"status": "error", "message": str(e)}

    return {"status": "error", "message": "Bot not initialized"}


# ============================================================
#                    MAIN
# ============================================================

async def main():
    print("🚀 CryptoPulse AI Bot Starting...")
    print(f"⏰ {datetime.now()}\n")

    # 1. Load all modules
    load_all_parts()

    # 2. Start bot
    await start_bot()

    # 3. Keep alive
    await asyncio.Event().wait()


def run_fastapi():
    port = int(os.environ.get("PORT", "8080"))
    print(f"🌐 Starting FastAPI on port {port}...")
    uvicorn.run(api_app, host="0.0.0.0", port=port, log_level="info")


# ============================================================
#                    RUN
# ============================================================

if __name__ == "__main__":
    # Start FastAPI in a thread
    api_thread = threading.Thread(target=run_fastapi, daemon=True)
    api_thread.start()

    # Start bot in async
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Stopped manually")
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
        traceback.print_exc()
