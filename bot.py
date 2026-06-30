#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - Main Entry Point
ربات هوشمند تحلیل و سیگنال ارزهای دیجیتال
فقط بارگذاری و اجرای تمام ۱۵ بخش
"""

import os
import sys
import asyncio
import time

print("🚀 Starting CryptoPulse AI Bot v3.0...")
print("📁 Loading all 15 parts...\n")

# ============================================================
#                    LOAD ALL 15 PARTS
# ============================================================

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

# ============================================================
#                    RUN
# ============================================================

print("\n" + "="*50)
print("🚀 All 15 parts loaded successfully!")
print("="*50)

if __name__ == "__main__":
    try:
        # اجرای اپلیکیشن از part9
        from part9 import get_application
        app = get_application()
        if app:
            print("✅ Bot application created!")
            asyncio.run(app.run_polling())
        else:
            print("⚠️ No application found. Running idle...")
            while True:
                time.sleep(1)
    except ImportError:
        print("⚠️ part9 not found. Running idle...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        while True:
            time.sleep(1)
