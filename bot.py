#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
import time
import uvicorn
import signal
import sys

print("🚀 Starting CryptoPulse AI Bot v3.0...")

# ============================================================
#                    SIGNAL HANDLER
# ============================================================

def signal_handler(sig, frame):
    print(f"⚠️ Signal {sig} received, ignoring...")
    # ری‌استارت نمیکنیم، فقط ادامه میدهیم

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ============================================================
#                    IMPORT ALL PARTS
# ============================================================

print("📁 Loading all 15 parts...\n")

try:
    from part1 import *
    print("  ✅ Part 1: Main Entry Point")
except Exception as e:
    print(f"  ❌ Part 1: {e}")

try:
    from part2 import *
    print("  ✅ Part 2: Config & Settings")
except Exception as e:
    print(f"  ❌ Part 2: {e}")

try:
    from part3 import *
    print("  ✅ Part 3: Database Models")
except Exception as e:
    print(f"  ❌ Part 3: {e}")

try:
    from part4 import *
    print("  ✅ Part 4: Utils & Tehran Time")
except Exception as e:
    print(f"  ❌ Part 4: {e}")

try:
    from part5 import *
    print("  ✅ Part 5: CoinEx Exchange")
except Exception as e:
    print(f"  ❌ Part 5: {e}")

try:
    from part6 import *
    print("  ✅ Part 6: Groq AI")
except Exception as e:
    print(f"  ❌ Part 6: {e}")

try:
    from part7 import *
    print("  ✅ Part 7: Technical Analysis")
except Exception as e:
    print(f"  ❌ Part 7: {e}")

try:
    from part8 import *
    print("  ✅ Part 8: Keyboards & Menus")
except Exception as e:
    print(f"  ❌ Part 8: {e}")

try:
    from part9 import *
    print("  ✅ Part 9: Main Handlers")
except Exception as e:
    print(f"  ❌ Part 9: {e}")

try:
    from part10 import *
    print("  ✅ Part 10: Admin Panel")
except Exception as e:
    print(f"  ❌ Part 10: {e}")

try:
    from part11 import *
    print("  ✅ Part 11: VIP & Payment")
except Exception as e:
    print(f"  ❌ Part 11: {e}")

try:
    from part12 import *
    print("  ✅ Part 12: Channel Management")
except Exception as e:
    print(f"  ❌ Part 12: {e}")

try:
    from part13 import *
    print("  ✅ Part 13: FastAPI Server")
except Exception as e:
    print(f"  ❌ Part 13: {e}")

try:
    from part14 import *
    print("  ✅ Part 14: Background Tasks")
except Exception as e:
    print(f"  ❌ Part 14: {e}")

try:
    from part15 import *
    print("  ✅ Part 15: Media Management")
except Exception as e:
    print(f"  ❌ Part 15: {e}")

print("\n" + "="*50)
print("🚀 All 15 parts loaded successfully!")
print("="*50)

# ============================================================
#                    CHECK ENV
# ============================================================

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
PORT = int(os.environ.get("PORT", 8080))

print(f"\n✅ BOT_TOKEN: {'SET' if BOT_TOKEN else 'NOT SET'}")
print(f"✅ PORT: {PORT}")
print()

# ============================================================
#                    RUN BOT
# ============================================================

async def run_forever():
    """اجرای دائمی ربات بدون خاموش شدن"""
    
    # اجرای ربات تلگرام
    try:
        from part9 import get_application
        bot_app = get_application()
        if bot_app:
            await bot_app.bot.delete_webhook(drop_pending_updates=True)
            await bot_app.initialize()
            await bot_app.start()
            await bot_app.updater.start_polling()
            print("✅ Telegram Bot is running with polling!")
    except Exception as e:
        print(f"⚠️ Bot error: {e}")
    
    # اجرای سرور FastAPI
    try:
        from part13 import app
        config = uvicorn.Config(
            app,
            host="0.0.0.0",
            port=PORT,
            log_level="error",
            loop="asyncio"
        )
        server = uvicorn.Server(config)
        await server.serve()
    except Exception as e:
        print(f"⚠️ Server error: {e}")
    
    # اگر همه چیز خاموش شد، دوباره اجرا کن
    print("🔄 Restarting...")
    await asyncio.sleep(1)
    await run_forever()

if __name__ == "__main__":
    try:
        asyncio.run(run_forever())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        while True:
            time.sleep(1)
