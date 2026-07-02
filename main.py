import os
import sys
import asyncio
import logging
import importlib
from pathlib import Path
from datetime import datetime
from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("CryptoPulse")

app = FastAPI(
    title="CryptoPulse AI Bot v3.5",
    version="3.5.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# Module Manager FIXED
# ============================================================

class ModuleManager:
    def __init__(self):
        self.modules: Dict[str, str] = {}
        self.task = None
        self.bot_task = None
        self.running = False
        self.start_time = datetime.utcnow()

        self.parts = {
            1: ("part1", "Database & Models"),
            2: ("part2", "Config & Settings"),
            3: ("part3", "i18n & Languages"),
            4: ("part4", "Utils & Helpers"),
            5: ("part5", "Exchange & Market"),
            6: ("part6", "AI & ML"),
            7: ("part7", "Technical Analysis"),
            8: ("part8", "Signals"),
            9: ("part9", "Risk Management"),
            10: ("part10", "Trading Engine"),
            11: ("part11", "Payments"),
            12: ("part12", "Media"),
            13: ("part13", "Notifications"),
            14: ("part14", "Telegram Bot"),
            15: ("part15", "Monitor"),
        }

    async def start_all(self):
        if self.running:
            logger.warning("Already running")
            return

        self.running = True
        logger.info("🚀 Starting CryptoPulse modules...")

        # Load parts
        for i in range(1, 16):
            await self.load_part(i)

        # Load bot ONLY ONCE
        await self.load_bot()

        logger.info("✅ All modules loaded")

    async def load_part(self, i: int):
        name, desc = self.parts[i]
        try:
            module = importlib.import_module(name)

            if hasattr(module, "start"):
                res = module.start()
                if asyncio.iscoroutine(res):
                    await res

            elif hasattr(module, "init"):
                res = module.init()
                if asyncio.iscoroutine(res):
                    await res

            self.modules[name] = f"✅ {desc}"
            logger.info(f"[OK] {name}")

        except ModuleNotFoundError:
            self.modules[name] = f"⚠️ missing"
            logger.warning(f"[MISS] {name}")

        except Exception as e:
            self.modules[name] = f"❌ error: {str(e)[:50]}"
            logger.error(f"[ERR] {name} -> {e}")

        await asyncio.sleep(0.03)

    async def load_bot(self):
        try:
            bot = importlib.import_module("bot")

            # prevent double run
            if self.bot_task and not self.bot_task.done():
                return

            if hasattr(bot, "main"):
                self.bot_task = asyncio.create_task(bot.main())
            elif hasattr(bot, "start"):
                self.bot_task = asyncio.create_task(bot.start())
            elif hasattr(bot, "run"):
                self.bot_task = asyncio.create_task(bot.run())

            self.modules["bot"] = "✅ running"

        except Exception as e:
            self.modules["bot"] = f"❌ {str(e)[:50]}"
            logger.error(f"BOT ERROR: {e}")

    def status(self):
        return {
            "uptime": (datetime.utcnow() - self.start_time).total_seconds(),
            "modules": self.modules,
            "running": self.running
        }

manager = ModuleManager()

# ============================================================
# FASTAPI EVENTS (FIXED)
# ============================================================

@app.on_event("startup")
async def startup():
    if manager.task is None:
        manager.task = asyncio.create_task(manager.start_all())

# ============================================================
# ROUTES
# ============================================================

@app.get("/")
async def root():
    return {
        "bot": "CryptoPulse v3.5",
        "status": "online",
        "uptime": manager.status()["uptime"]
    }

@app.get("/health")
async def health():
    ok = sum("✅" in v for v in manager.modules.values())

    return {
        "status": "healthy" if ok > 12 else "degraded",
        "loaded": ok,
        "total": 16
    }

@app.get("/status")
async def status():
    return manager.status()

@app.get("/restart")
async def restart():
    manager.running = False
    manager.modules.clear()
    manager.task = asyncio.create_task(manager.start_all())
    return {"status": "restarting"}

# ============================================================
# RUN (Railway compatible)
# ============================================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8080))

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
