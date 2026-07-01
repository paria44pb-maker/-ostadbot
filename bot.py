#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
import time
import uvicorn

print("🚀 Starting CryptoPulse AI Bot v3.0...")

# ============================================================
#                    IMPORT ALL PARTS
# ============================================================

try:
    from part1 import *
    print("✅ Part 1 loaded")
except Exception as e:
    print(f"❌ Part 1: {e}")

try:
    from part2 import *
    print("✅ Part 2 loaded")
except Exception as e:
    print(f"❌ Part 2: {e}")

try:
    from part3 import *
    print("✅ Part 3 loaded")
except Exception as e:
    print(f"❌ Part 3: {e}")

try:
    from part4 import *
    print("✅ Part 4 loaded")
except Exception as e:
    print(f"❌ Part 4: {e}")

try:
    from part5 import *
    print("✅ Part 5 loaded")
except Exception as e:
    print(f"❌ Part 5: {e}")

try:
    from part6 import *
    print("✅ Part 6 loaded")
except Exception as e:
    print(f"❌ Part 6: {e}")

try:
    from part7 import *
    print("✅ Part 7 loaded")
except Exception as e:
    print(f"❌ Part 7: {e}")

try:
    from part8 import *
    print("✅ Part 8 loaded")
except Exception as e:
    print(f"❌ Part 8: {e}")

try:
    from part9 import *
    print("✅ Part 9 loaded")
except Exception as e:
    print(f"❌ Part 9: {e}")

try:
    from part10 import *
    print("✅ Part 10 loaded")
except Exception as e:
    print(f"❌ Part 10: {e}")

try:
    from part11 import *
    print("✅ Part 11 loaded")
except Exception as e:
    print(f"❌ Part 11: {e}")

try:
    from part12 import *
    print("✅ Part 12 loaded")
except Exception as e:
    print(f"❌ Part 12: {e}")

try:
    from part13 import *
    print("✅ Part 13 loaded")
except Exception as e:
    print(f"❌ Part 13: {e}")

try:
    from part14 import *
    print("✅ Part 14 loaded")
except Exception as e:
    print(f"❌ Part 14: {e}")

try:
    from part15 import *
    print("✅ Part 15 loaded")
except Exception as e:
    print(f"❌ Part 15: {e}")

print("✅ All 15 parts loaded!")

# ============================================================
#                    SIMPLE FASTAPI SERVER
# ============================================================

from fastapi import FastAPI
app = FastAPI(title="CryptoPulse AI", version="3.0.0")

@app.get("/")
async def root():
    return {"status": "online", "message": "CryptoPulse AI is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# ============================================================
#                    RUN BOT WITH POLLING
# ============================================================

async def run_bot():
    # حذف Webhook
    try:
        from part9 import get_application
        bot_app = get_application()
        if bot_app:
            await bot_app.bot.delete_webhook(drop_pending_updates=True)
            print("✅ Webhook deleted!")
            
            await bot_app.initialize()
            await bot_app.start()
            await bot_app.updater.start_polling()
            print("✅ Telegram Bot is running with polling!")
    except Exception as e:
        print(f"⚠️ Bot error: {e}")
    
    # اجرای سرور
    port = int(os.environ.get("PORT", 8080))
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="error")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        while True:
            time.sleep(1)
