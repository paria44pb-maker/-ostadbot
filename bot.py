
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
import uvicorn

print("🚀 Starting CryptoPulse AI Bot v3.0...")

from part1 import *
from part2 import *
from part3 import *
from part4 import *
from part5 import *
from part6 import *
from part7 import *
from part8 import *
from part9 import *
from part10 import *
from part11 import *
from part12 import *
from part13 import *
from part14 import *
from part15 import *

print("✅ All 15 parts loaded!")

async def main():
    # اجرای ربات تلگرام
    try:
        from part9 import get_application
        bot_app = get_application()
        if bot_app:
            await bot_app.bot.delete_webhook(drop_pending_updates=True)
            await bot_app.initialize()
            await bot_app.start()
            await bot_app.updater.start_polling()
            print("✅ Telegram Bot is running!")
    except Exception as e:
        print(f"⚠️ Bot error: {e}")
    
    # اجرای سرور
    from part13 import app
    port = int(os.environ.get("PORT", 8080))
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="error")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
