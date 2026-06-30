#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - Main Entry Point
ربات هوشمند تحلیل و سیگنال ارزهای دیجیتال
اجرای تمام ۱۵ بخش - نسخه نهایی
"""

import os
import sys
import asyncio
import time
import uvicorn

print("🚀 Starting CryptoPulse AI Bot v3.0...")

# ============================================================
#                    IMPORT ALL 15 PARTS
# ============================================================

try:
    print("📁 Loading all 15 parts...")
    
    from part1 import *
    print("  ✅ Part 1: Main Entry Point")
    
    from part2 import *
    print("  ✅ Part 2: Config & Settings")
    
    from part3 import *
    print("  ✅ Part 3: Database Models")
    
    from part4 import *
    print("  ✅ Part 4: Utils & Tehran Time")
    
    from part5 import *
    print("  ✅ Part 5: CoinEx Exchange")
    
    from part6 import *
    print("  ✅ Part 6: Groq AI")
    
    from part7 import *
    print("  ✅ Part 7: Technical Analysis")
    
    from part8 import *
    print("  ✅ Part 8: Keyboards & Menus")
    
    from part9 import *
    print("  ✅ Part 9: Main Handlers")
    
    from part10 import *
    print("  ✅ Part 10: Admin Panel")
    
    from part11 import *
    print("  ✅ Part 11: VIP & Payment")
    
    from part12 import *
    print("  ✅ Part 12: Channel Management")
    
    from part13 import *
    print("  ✅ Part 13: FastAPI Server")
    
    from part14 import *
    print("  ✅ Part 14: Background Tasks")
    
    from part15 import *
    print("  ✅ Part 15: Media Management")
    
    print("📁 All 15 parts imported successfully!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# ============================================================
#                    GET APPLICATION
# ============================================================

try:
    from bot9 import get_application
    application = get_application()
    print("✅ Bot application created!")
except Exception as e:
    print(f"⚠️ Error getting application: {e}")
    application = None

# ============================================================
#                    RUN SERVER
# ============================================================

async def run_bot():
    """اجرای ربات و سرور"""
    
    # اجرای ربات تلگرام
    if application:
        try:
            await application.initialize()
            await application.start()
            await application.updater.start_polling()
            print("✅ Telegram Bot is running!")
        except Exception as e:
            print(f"⚠️ Bot error: {e}")
    
    # اجرای سرور FastAPI
    try:
        from bot13 import app
        port = int(os.environ.get("PORT", 8080))
        print(f"🌐 Server running on port {port}")
        
        config = uvicorn.Config(
            "bot13:app",
            host="0.0.0.0",
            port=port,
            log_level="error",
            loop="asyncio"
        )
        server = uvicorn.Server(config)
        await server.serve()
        
    except Exception as e:
        print(f"⚠️ Server error: {e}")
        while True:
            await asyncio.sleep(1)

# ============================================================
#                    MAIN
# ============================================================

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
