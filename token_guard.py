import os

def get_safe_token():
    token = os.getenv("BOT_TOKEN")

    if not token:
        raise RuntimeError("❌ BOT_TOKEN not found")

    # basic sanity check
    if ":" not in token:
        raise RuntimeError("❌ BOT_TOKEN format is invalid")

    return token
