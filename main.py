#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - Main Entry Point (for Railway)
این فایل فقط برای Railway است و bot.py را اجرا می‌کند
"""

import os
import sys
import asyncio

# اجرای فایل bot.py
if __name__ == "__main__":
    # اجرای bot.py به عنوان ماژول اصلی
    import bot
    
    # اگر bot.py تابع main دارد
    if hasattr(bot, 'main'):
        bot.main()
    else:
        # اجرای مستقیم
        import runpy
        runpy.run_path("bot.py")
