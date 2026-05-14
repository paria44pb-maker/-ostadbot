import os

# ================================
# TELEGRAM TOKEN
# ================================
TELEGRAM_TOKEN = (
    os.getenv("TELEGRAM_TOKEN") or
    os.getenv("TELEGRAM_BOT_TOKEN")
)

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN not found")


# ================================
# GROQ API KEY
# ================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# ================================
# NOBITEX API
# ================================
NOBITEX_API_KEY = os.getenv("NOBITEX_API_KEY")

if not NOBITEX_API_KEY:
    print("WARNING: NOBITEX_API_KEY not found")
