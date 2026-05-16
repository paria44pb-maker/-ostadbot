import os
import requests
import tempfile
import time # Import time for delays if needed in bot logic

# --- ADD THIS ---
from nobitex_client import NobitexClient
from config import (
    NOBITEX_API_KEY,
    NOBITEX_SECRET,
    GROQ_API_KEY,
    TELEGRAM_TOKEN,
    DEFAULT_TRADING_PAIR,
    INITIAL_BUY_AMOUNT_BTC,
    INITIAL_BUY_PRICE_RLS,
    API_REQUEST_DELAY,
    MAX_API_RETRIES,
    RETRY_DELAY_MULTIPLIER
)
# --- END ADD ---

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") # REMOVE or COMMENT OUT, now loaded from config
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")     # REMOVE or COMMENT OUT, now loaded from config

conversation_memory = []

# --- INITIALIZE NOBITEX CLIENT ---
# Instantiate the client using credentials from config.py or environment variables
# If you don't have API Key/Secret yet, it will use placeholders and only access public endpoints.
nobitex_client = NobitexClient(api_key=NOBITEX_API_KEY, secret=NOBITEX_SECRET)
# --- END INITIALIZE ---


# ---------------- GROQ CHAT
def groq_chat(messages):
    # Ensure GROQ_API_KEY is loaded correctly from config
    if not GROQ_API_KEY or GROQ_API_KEY == "YOUR_GROQ_API_KEY_HERE":
        return {"error": "GROQ_API_KEY not configured."}

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "temperature": 0.5
    }

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=20) # Added timeout
        r.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        return r.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling Groq API: {e}")
        return {"error": f"Failed to get response from Groq API: {e}"}


# ---------------- TEXT TO SPEECH
def groq_tts(text):
    if not GROQ_API_KEY or GROQ_API_KEY == "YOUR_GROQ_API_KEY_HERE":
        print("GROQ_API_KEY not configured for TTS.")
        return None

    url = "https://api.groq.com/openai/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "bark-small",
        "input": text,
        "voice": "male"
    }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=30) # Added timeout
        if r.status_code == 200:
            temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp.write(r.content)
            temp.close()
            return temp.name
        else:
            print(f"Groq TTS API returned status code {r.status_code}: {r.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error calling Groq TTS API: {e}")
        return None


# ---------------- VOICE TO TEXT
def groq_whisper(audio_bytes):
    if not GROQ_API_KEY or GROQ_API_KEY == "YOUR_GROQ_API_KEY_HERE":
        print("GROQ_API_KEY not configured for Whisper.")
        return None

    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    files = {
        "file": ("voice.ogg", audio_bytes)
    }
    data = {
        "model": "whisper-large-v3-turbo"
    }
    try:
        r = requests.post(url, headers=headers, files=files, data=data, timeout=60) # Added timeout
        r.raise_for_status()
        return r.json().get("text")
    except requests.exceptions.RequestException as e:
        print(f"Error calling Groq Whisper API: {e}")
        return None


# ---------------- PRICE (Uses NobitexClient for Nobitex data)
async def crypto_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # For price, we can still use CoinGecko directly for global prices
    # and NobitexClient for Nobitex-specific prices.
    try:
        # Get prices from Nobitex using our client
        nobitex_btc_price = nobitex_client.get_latest_price("btc-rls")
        nobitex_eth_price = nobitex_client.get_latest_price("eth-rls")
        nobitex_usdt_price = nobitex_client.get_latest_price("usdt-rls")
        nobitex_xrp_price = nobitex_client.get_latest_price("xrp-rls")
        nobitex_ton_price = nobitex_client.get_latest_price("ton-rls")

        # Get global prices from CoinGecko (as before)
        cg_response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,tether,ripple,the-open-network&vs_currencies=usd",
            timeout=10 # Added timeout
        ).json()

        btc_usd = cg_response.get("bitcoin", {}).get("usd", "-")
        eth_usd = cg_response.get("ethereum", {}).get("usd", "-")
        usdt_usd = cg_response.get("tether", {}).get("usd", "-")
        xrp_usd = cg_response.get("ripple", {}).get("usd", "-")
        ton_usd = cg_response.get("the-open-network", {}).get("usd", "-")

        msg = f"""
📊 بازار کریپتو

🇮🇷 نوبیتکس
BTC : {nobitex_btc_price if nobitex_btc_price else '-'}
ETH : {nobitex_eth_price if nobitex_eth_price else '-'}
USDT : {nobitex_usdt_price if nobitex_usdt_price else '-'}
XRP : {nobitex_xrp_price if nobitex_xrp_price else '-'}
TON : {nobitex_ton_price if nobitex_ton_price else '-'}

🌍 بازار جهانی
BTC : {btc_usd} $
ETH : {eth_usd} $
USDT : {usdt_usd} $
XRP : {xrp_usd} $
TON : {ton_usd} $
"""
        await update.message.reply_text(msg)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching market data: {e}")
        await update.message.reply_text("خطا در دریافت قیمت بازار.")
    except Exception as e:
        print(f"An unexpected error occurred in crypto_price: {e}")
        await update.message.reply_text("خطای غیرمنتظره در دریافت قیمت بازار.")


# ---------------- TOP 10
async def top_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1",
            timeout=10 # Added timeout
        ).json()

        msg = "🔥 10 ارز برتر بازار (بر اساس ارزش بازار جهانی)\n\n"
        for coin in data:
            name = coin["name"]
            price = coin["current_price"]
            msg += f"{name} : {price:,.2f} $\n" # Formatted price

        await update.message.reply_text(msg)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching top crypto data: {e}")
        await update.message.reply_text("خطا در دریافت لیست 10 ارز برتر.")
    except Exception as e:
        print(f"An unexpected error occurred in top_crypto: {e}")
        await update.message.reply_text("خطای غیرمنتظره در دریافت لیست 10 ارز برتر.")


# ---------------- MARKET ANALYSIS
async def market_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = requests.get(
            "https://api.coingecko.com/api/v3/global",
            timeout=10 # Added timeout
        ).json()

        total_market_cap = data["data"]["total_market_cap"]["usd"]
        btc_dominance = data["data"]["market_cap_percentage"]["btc"]

        msg = f"""
🧠 تحلیل سریع بازار جهانی

ارزش کل بازار:
{total_market_cap:,.0f} $

Dominance BTC:
{btc_dominance:.2f} %

(دامیننس بالا یعنی سهم بیشتری از پول بازار در بیت‌کوین است.)
"""
        await update.message.reply_text(msg)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching market analysis data: {e}")
        await update.message.reply_text("خطا در دریافت تحلیل بازار.")
    except Exception as e:
        print(f"An unexpected error occurred in market_analysis: {e}")
        await update.message.reply_text("خطای غیرمنتظره در دریافت تحلیل بازار.")


# ---------------- START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 قیمت بازار", callback_data="price")],
        [InlineKeyboardButton("🔥 10 ارز برتر", callback_data="top")],
        [InlineKeyboardButton("🧠 تحلیل بازار", callback_data="analysis")],
        [InlineKeyboardButton("🎧 ارسال ویس", callback_data="voice")],
        [InlineKeyboardButton("💬 چت هوشمند", callback_data="chat")],
        # --- ADDED BUTTON FOR NOBITEX SPECIFIC ACTIONS ---
        [InlineKeyboardButton("💰 موجودی نوبیتکس", callback_data="nobitex_balance")],
        [InlineKeyboardButton("📈 خرید BTC", callback_data="nobitex_buy")],
        # --- END ADDED ---
    ]

    await update.message.reply_text(
        "سلام فرهاد 👋\nربات کریپتو فعال شد",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ---------------- CHAT (Groq API)
async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if not user_text:
        return

    # Limit conversation memory to avoid excessive token usage
    conversation_memory.append({"role": "user", "content": user_text})
    if len(conversation_memory) > 5: # Keep last 5 turns (user + assistant)
        conversation_memory.pop(0)

    messages = [
        {"role": "system", "content": "You are a helpful Persian crypto assistant. Focus on providing clear, concise, and technically accurate information. If asked about trading actions, remind the user to use specific commands and verify details."},
        *conversation_memory
    ]

    answer = groq_chat(messages)

    if "error" in answer:
        await update.message.reply_text(f"خطا در ارتباط با هوش مصنوعی: {answer['error']}")
        return

    if "choices" not in answer or not answer["choices"]:
        await update.message.reply_text("خطا در دریافت پاسخ از هوش مصنوعی.")
        return

    text = answer["choices"][0]["message"]["content"]
    conversation_memory.append({"role": "assistant", "content": text}) # Store assistant response
    if len(conversation_memory) > 5: # Ensure memory doesn't exceed limit after adding response
        conversation_memory.pop(0)

    await update.message.reply_text(text)

    # Attempt to convert text to speech
    audio = groq_tts(text)
    if audio:
        try:
            await update.message.reply_voice(open(audio, "rb"))
        except Exception as e:
            print(f"Error sending voice message: {e}")
        finally:
            # Clean up the temporary audio file
            if os.path.exists(audio):
                os.remove(audio)


# ---------------- VOICE (Groq API Whisper)
async def ai_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.voice:
        await update.message.reply_text("لطفا یک فایل صوتی ارسال کنید.")
        return

    try:
        file = await update.message.voice.get_file()
        voice_bytes = await file.download_as_bytearray()
        text = groq_whisper(voice_bytes)

        if not text:
            await update.message.reply_text("خطا در تبدیل ویس به متن. لطفا دوباره تلاش کنید.")
            return

        # Process the transcribed text as if it was typed by the user
        update.message.text = text
        await ai_chat(update, context) # Reuse ai_chat to handle the text response and TTS

    except Exception as e:
        print(f"Error processing voice message: {e}")
        await update.message.reply_text("خطایی در پردازش پیام صوتی رخ داد.")


# --- NEW HANDLERS FOR NOBITEX CLIENT ---

async def nobitex_balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler to display user's balance from Nobitex."""
    if not NOBITEX_API_KEY or NOBITEX_API_KEY == "YOUR_API_KEY_HERE":
        await update.message.reply_text("کلید API نوبیتکس تنظیم نشده است. لطفا `config.py` را بررسی کنید یا متغیر محیطی `NOBITEX_API_KEY` را تنظیم کنید.")
        return

    try:
        # Assuming Nobitex API has a '/panel/balance' endpoint for balance
        # NOTE: You MUST uncomment and adapt the get_balance method in nobitex_client.py
        # if this endpoint is correct and requires specific POST/GET parameters.
        # For now, we'll assume it exists and is a POST request as an example.
        # If it's a GET request, change _make_request("POST", ...) to _make_request("GET", ...)
        # and remove the 'data' parameter if it's not needed.
        balance_data = nobitex_client.session.post(f"{nobitex_client.BASE_URL}/panel/balance", headers=nobitex_client.session.headers, timeout=15).json() # Direct call example

        # Parse the balance data - adjust based on actual API response structure
        # Example structure: {"balance": [{"asset": "BTC", "free": "0.001", "locked": "0.0001"}, ...]}
        if balance_data and "balance" in balance_data:
            msg = "💰 موجودی حساب نوبیتکس:\n\n"
            total_value_usd = 0
            for item in balance_data["balance"]:
                asset = item.get("asset", "N/A")
                free = item.get("free", "0")
                locked = item.get("locked", "0")
                # Attempt to get USD value if available or by looking up current price
                # For simplicity, we'll just display asset, free, locked amounts.
                # To get total value, you'd need to fetch prices again and convert.
                msg += f"- {asset}: Free: {free}, Locked: {locked}\n"

            await update.message.reply_text(msg)
        else:
            await update.message.reply_text("خطا در دریافت اطلاعات موجودی از نوبیتکس. پاسخ API نامعتبر بود.")
            print(f"Nobitex balance API response: {balance_data}")

    except requests.exceptions.HTTPError as e:
        await update.message.reply_text(f"خطا در ارتباط با نوبیتکس (HTTP Error): {e}")
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"خطا در ارتباط با نوبیتکس: {e}")
    except ValueError as e:
        await update.message.reply_text(f"خطا در پردازش پاسخ نوبیتکس: {e}")
    except Exception as e:
        print(f"Unexpected error in nobitex_balance_handler: {e}")
        await update.message.reply_text("یک خطای غیرمنتظره رخ داد.")


async def nobitex_buy_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler to attempt a buy order on Nobitex."""
    if not NOBITEX_API_KEY or NOBITEX_API_KEY == "YOUR_API_KEY_HERE":
        await update.message.reply_text("کلید API نوبیتکس تنظیم نشده است. لطفا `config.py` را بررسی کنید یا متغیر محیطی `NOBITEX_API_KEY` را تنظیم کنید.")
        return

    # Get parameters from config or user message if provided
    pair = DEFAULT_TRADING_PAIR
    amount = INITIAL_BUY_AMOUNT_BTC
    price = INITIAL_BUY_PRICE_RLS

    # --- Basic example: User can specify amount and price ---
    # e.g., /buy_btc 0.0001 50000000
    # You might want to parse this from the message text if the command is used differently.
    # For simplicity, we use defaults from config.py for now.

    if not pair or amount is None or price is None:
        await update.message.reply_text("اطلاعات لازم برای خرید (جفت ارز، مقدار، قیمت) در config.py تنظیم نشده است.")
        return

    confirmation_msg = (
        f"آیا مطمئنید که می‌خواهید:\n"
        f"مقدار `{amount}` از ارز `{pair.split('-')[0].upper()}`\n"
        f"را در قیمت `{price:,}` ریال در نوبیتکس خریداری کنید؟\n\n"
        f"*(این یک دستور آزمایشی است و ممکن است نیاز به تأیید نهایی داشته باشد)*"
    )
    keyboard = [
        [
            InlineKeyboardButton("✅ بله، خرید انجام شود", callback_data=f"confirm_buy_{pair}_{amount}_{price}"),
            InlineKeyboardButton("❌ خیر، لغو شود", callback_data="cancel_action")
        ]
    ]
    await update.message.reply_text(confirmation_msg, reply_markup=InlineKeyboardMarkup(keyboard))


async def handle_confirm_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the confirmation for a buy order."""
    query = update.callback_query
    await query.answer()

    data = query.data.split('_')
    if len(data) < 4 or data[0] != "confirm" o
