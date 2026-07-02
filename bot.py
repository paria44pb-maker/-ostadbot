#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot - Safe 15 Parts Loader
Production-safe with Webhook + Creator Page
"""

import os
import sys
import importlib
import traceback
import asyncio
import uvicorn
import threading
from datetime import datetime
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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
#                    STATUS FLAG
# ============================================================

bot_ready = False
startup_complete = False

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

# Store bot application globally
telegram_bot_app = None

@app.get("/")
async def root():
    return {
        "bot": "CryptoPulse AI v3.5",
        "creator": CREATOR_NAME,
        "status": "online" if bot_ready else "starting",
        "message": "🚀 Bot is running!" if bot_ready else "⏳ Starting up...",
        "telegram": CREATOR_TELEGRAM,
        "github": CREATOR_GITHUB,
        "uptime": str(datetime.now()),
        "mode": "webhook"
    }

@app.get("/health")
async def health():
    ok = len(loaded_modules)
    return {
        "status": "healthy" if ok >= 9 and bot_ready else "starting",
        "loaded": ok,
        "total": 15,
        "bot_ready": bot_ready
    }

@app.get("/status")
async def status():
    return {
        "modules": {name: "✅" for name in loaded_modules},
        "bot_token": "✅" if BOT_TOKEN else "❌",
        "bot_ready": bot_ready,
        "startup_complete": startup_complete
    }

@app.post("/webhook")
async def webhook(request: Request):
    """Receive Telegram updates"""
    global telegram_bot_app, bot_ready
    
    if not bot_ready or not telegram_bot_app:
        print(f"⏳ Webhook call but bot not ready yet")
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "message": "Bot still starting"}
        )
    
    try:
        data = await request.json()
        await telegram_bot_app.update_queue.put(data)
        return {"status": "ok"}
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

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
    else:
        print(f"✅ BOT_TOKEN found: {BOT_TOKEN[:8]}...")

    print(f"\n🚀 Loading 15 Parts...\n")

    for part in PARTS:
        load_part(part)
        import time
        time.sleep(0.05)

    print("\n" + "=" * 50)
    print(f"✅ Loaded: {len(loaded_modules)}/{len(PARTS)}")
    print("=" * 50 + "\n")


# ============================================================
#                    TELEGRAM BOT (WEBHOOK)
# ============================================================

async def start_bot():
    global telegram_bot_app, bot_ready, startup_complete

    try:
        part9 = loaded_modules.get("part9")

        if not part9:
            print("❌ part9 not loaded")
            return False

        if not hasattr(part9, "get_application"):
            print("❌ get_application() not found")
            return False

        telegram_bot_app = part9.get_application()

        if not telegram_bot_app:
            print("⚠️ Bot not found in fallback mode")
            return False

        print("🔄 Initializing bot...")
        await telegram_bot_app.initialize()
        
        print("▶️  Starting bot...")
        await telegram_bot_app.start()

        # Get webhook URL
        railway_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")
        if not railway_domain:
            railway_domain = os.environ.get("RAILWAY_STATIC_URL", "").replace("https://", "")

        if not railway_domain:
            print("❌ No Railway domain found")
            print("💡 Enable Public URL in Railway Settings > Networking")
            return False

        webhook_url = f"https://{railway_domain}/webhook"
        print(f"🔗 Setting webhook: {webhook_url}")
        
        # Delete old webhook
        await telegram_bot_app.bot.delete_webhook(drop_pending_updates=True)
        await asyncio.sleep(1)
        
        # Set new webhook
        result = await telegram_bot_app.bot.set_webhook(
            url=webhook_url,
            max_connections=5,
            drop_pending_updates=True
        )
        
        if result:
            bot_ready = True
            startup_complete = True
            print(f"✅ Webhook set successfully!")
            print(f"🤖 Bot is ready!")
            print(f"📡 Webhook URL: {webhook_url}")
            
            # Verify webhook
            info = await telegram_bot_app.bot.get_webhook_info()
            print(f"🔍 Webhook info: {info.url}")
            print(f"📊 Pending updates: {info.pending_update_count}")
            
            return True
        else:
            print("❌ Failed to set webhook")
            return False

    except Exception as e:
        print(f"❌ Bot Error: {e}")
        traceback.print_exc()
        return False


# ============================================================
#                    MAIN
# ============================================================

def run_server():
    """Run FastAPI server"""
    port = int(os.environ.get("PORT", "8080"))
    print(f"\n🌐 Server starting on port {port}...")
    print(f"   Creator Page: /")
    print(f"   Health: /health")
    print(f"   Status: /status")
    print(f"   Webhook: /webhook\n")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")


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
    print(f"⏰ {datetime.now()}\n")

    # 1. Start FastAPI server FIRST
    print("🌐 Starting web server...")
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    await asyncio.sleep(3)
    print("✅ Web server ready\n")

    # 2. Load all parts
    load_all_parts()

    # 3. Start bot with webhook
    print("🤖 Setting up Telegram bot...")
    success = await start_bot()

    if success:
        print("\n" + "=" * 50)
        print("✅ ALL SYSTEMS OPERATIONAL")
        print("=" * 50)
        print("\n💡 Bot is running 24/7. Press Ctrl+C to stop.\n")
    else:
        print("\n" + "=" * 50)
        print("⚠️  Bot webhook failed")
        print("💡 Check: Railway Public URL, BOT_TOKEN")
        print("=" * 50)

    # 4. Keep alive
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
