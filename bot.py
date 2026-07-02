#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI v3.0
Main Starter
"""

import os
import sys
import asyncio
import importlib
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", "8080"))

PARTS = [
    "part1","part2","part3","part4","part5","part6",
    "part7","part8","part9","part10","part11","part12",
    "part13","part14","part15","part16","part17","part18"
]

loaded = {}


async def load_modules():

    print("══════════════════════════════")
    print(" CryptoPulse AI Boot")
    print("══════════════════════════════")

    for name in PARTS:

        try:
            module = importlib.import_module(name)

            loaded[name] = module

            print(f"✅ {name}")

            startup = getattr(module, "startup", None)

            if startup:

                if asyncio.iscoroutinefunction(startup):
                    await startup()
                else:
                    startup()

        except Exception as e:

            print(f"❌ {name} -> {e}")

    print("══════════════════════════════")


async def start_bot():

    module = loaded.get("part9")

    if not module:
        return

    fn = getattr(module, "start_bot", None)

    if fn:

        print("🤖 Telegram Bot Starting...")

        if asyncio.iscoroutinefunction(fn):
            asyncio.create_task(fn(BOT_TOKEN))
        else:
            fn(BOT_TOKEN)


async def start_server():

    module = loaded.get("part13")

    if not module:
        return

    fn = getattr(module, "start_server", None)

    if fn:

        print("🌐 FastAPI Starting...")

        if asyncio.iscoroutinefunction(fn):
            asyncio.create_task(fn(PORT))
        else:
            fn(PORT)


async def keep_alive():

    while True:
        await asyncio.sleep(60)


async def main():

    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not found")
        return

    await load_modules()

    await start_bot()

    await start_server()

    print()
    print("══════════════════════════════")
    print(" 🚀 CryptoPulse AI Online")
    print("══════════════════════════════")
    print()

    await keep_alive()


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("🛑 Stopped")

    except Exception as e:
        print(e)
        sys.exit(1)
