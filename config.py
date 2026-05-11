import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN variable is missing in Railway!")

if " " in BOT_TOKEN:
    raise ValueError("BOT_TOKEN must not contain spaces!")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY variable is missing in Railway!")
