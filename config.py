import os
from dotenv import load_dotenv

# Load .env if running locally
load_dotenv()

# -------------------------
# Telegram BOT Token
# -------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set. Please add it to Railway Variables.")

# -------------------------
# GROQ API Key
# -------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set. Please add it to Railway Variables.")

# -------------------------
# OPTIONAL - Model choice
# -------------------------
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")

# -------------------------
# Debug mode (optional)
# -------------------------
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
