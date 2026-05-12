import os
import logging
from telegram.ext import ApplicationBuilder

logging.basicConfig(level=logging.INFO)

def load_token():
    raw = os.getenv("BOT_TOKEN")

    print("RAW TOKEN:", repr(raw))

    if not raw:
        raise RuntimeError("BOT_TOKEN is missing")

    clean = raw.strip().replace("`", "").replace('"', "").replace("'", "")

    print("CLEAN TOKEN:", repr(clean))
    print("TOKEN LENGTH:", len(clean))

    if ":" not in clean:
        raise RuntimeError("Invalid token format")

    return clean

BOT_TOKEN = load_token()

app = ApplicationBuilder().token(BOT_TOKEN).build()

if __name__ == "__main__":
    logging.info("Starting bot polling...")
    app.run_polling()
