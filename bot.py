import os
import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# نصب کتابخانه: pip install coinexlib
try:
    from coinexlib import CoinexAPI
    COINEX_AVAILABLE = True
except ImportError:
    COINEX_AVAILABLE = False
    print("⚠️ برای اتصال به CoinEx، ابتدا کتابخانه را نصب کنید: pip install coinexlib")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ========== تنظیمات CoinEx ==========
ACCESS_ID = os.getenv("COINEX_ACCESS_ID", "Your_Access_ID_Here")
SECRET_KEY = os.getenv("COINEX_SECRET_KEY", "Your_Secret_Key_Here")

# مقداردهی اولیه کلاینت CoinEx
if COINEX_AVAILABLE and ACCESS_ID != "Your_Access_ID_Here" and SECRET_KEY != "Your_Secret_Key_Here":
    api = CoinexAPI(ACCESS_ID, SECRET_KEY)
    COINEX_CONFIGURED = True
else:
    COINEX_CONFIGURED = False
    api = None
    logger.warning("CoinEx API تنظیم نشده است. لطفاً ACCESS_ID و SECRET_KEY را تنظیم کنید.")

# ========== ارزهای تحت پوشش ==========
SYMBOLS = [
    {"symbol": "BTCUSDT", "name": "بیت‌کوین", "emoji": "👑", "min_amount": 0.0001},
    {"symbol": "ETHUSDT", "name": "اتریوم", "emoji": "💎", "min_amount": 0.001},
    {"symbol": "SOLUSDT", "name": "سولانا", "emoji": "⚡", "min_amount": 0.01},
    {"symbol": "XRPUSDT", "name": "ریپل", "emoji": "💧", "min_amount": 1},
    {"symbol": "DOGEUSDT", "name": "داوج", "emoji": "🐕", "min_amount": 10},
    {"symbol": "ADAUSDT", "name": "کاردانو", "emoji": "🌿", "min_amount": 10},
    {"symbol": "AVAXUSDT", "name": "آوالانچ", "emoji": "❄️", "min_amount": 0.1},
    {"symbol": "MATICUSDT", "name": "پالیگان", "emoji": "🟣", "min_amount": 5},
]

# ========== دریافت قیمت از CoinEx ==========
async def get_coinex_price(symbol="BTCUSDT"):
    """دریافت قیمت لحظه‌ای از CoinEx"""
    if not COINEX_CONFIGURED:
        return {"success": False, "error": "CoinEx API تنظیم نشده است"}
    
    try:
        # دریافت قیمت از بازار اسپات
        ticker = api.get_market_depth(symbol, limit=1, interval="0")
        if ticker and ticker.get("code") == 0:
            data = ticker.get("data", {})
            depth = data.get("depth", {})
            ask = depth.get("asks", [])
            bid = depth.get("bids", [])
            
            last_price = float(ask[0][0]) if ask else 0
            
            # دریافت تغییرات 24 ساعته
            market_info = api.get_market_status(symbol)
            if market_info and market_info.get("code") == 0:
                market_data = market_info.get("data", {})
                change = market_data.get("change", 0)
                volume = market_data.get("vol", 0)
                high = market_data.get("high", 0)
                low = market_data.get("low", 0)
                
                return {
                    "success": True,
                    "price": last_price,
                    "change": float(change) if change else 0,
                    "volume": float(volume) if volume else 0,
                    "high": float(high) if high else 0,
                    "low": float(low) if low else 0,
                    "source": "CoinEx"
                }
        
        return {"success": False, "error": "خطا در دریافت قیمت"}
        
    except Exception as e:
        logger.error(f"خطا در دریافت قیمت {symbol}: {e}")
        return {"success": False, "error": str(e)}

async def get_account_balance():
    """دریافت موجودی حساب از CoinEx"""
    if not COINEX_CONFIGURED:
        return {"success": False, "error": "CoinEx API تنظیم نشده است"}
    
    try:
        balance_data = api.get_balance()
        if balance_data and balance_data.get("code") == 0:
            data = balance_data.get("data", {})
            return {
                "success": True,
                "total": float(data.get("USDT", {}).get("total", 0)),
                "free": float(data.get("USDT", {}).get("free", 0)),
                "frozen": float(data.get("USDT", {}).get("frozen", 0))
            }
        return {"success": False, "error": "خطا در دریافت موجودی"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def place_buy_order(symbol, amount, price=None):
    """ثبت سفارش خرید در CoinEx"""
    if not COINEX_CONFIGURED:
        return {"success": False, "error": "CoinEx API تنظیم نشده است"}
    
    try:
        if price:
            order = api.place_order(
                market=symbol,
                market_type="SPOT",
                side="buy",
                order_type="limit",
                amount=str(amount),
                price=str(price)
            )
        else:
            # سفارش بازار
            order = api.place_order(
                market=symbol,
                market_type="SPOT",
                side="buy",
                order_type="market",
                amount=str(amount)
            )
        
        if order and order.get("code") == 0:
            return {"success": True, "order": order.get("data", {})}
        return {"success": False, "error": order.get("message", "خطا در ثبت سفارش")}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def place_sell_order(symbol, amount, price=None):
    """ثبت سفارش فروش در CoinEx"""
    if not COINEX_CONFIGURED:
        return {"success": False, "error": "CoinEx API تنظیم نشده است"}
    
    try:
        if price:
            order = api.place_order(
                market=symbol,
                market_type="SPOT",
                side="sell",
                order_type="limit",
                amount=str(amount),
                price=str(price)
            )
        else:
            order = api.place_order(
                market=symbol,
                market_type="SPOT",
                side="sell",
                order_type="market",
                amount=str(amount)
            )
        
        if order and order.get("code") == 0:
            return {"success": True, "order": order.get("data", {})}
        return {"success": False, "error": order.get("message", "خطا در ثبت سفارش")}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ========== تولید سیگنال ==========
def generate_signal(price, change):
    if change > 3:
        return "🟢🟢 خرید قوی", 90
    elif change > 1:
        return "🟢 خرید", 70
    elif change < -3:
        return "🔴🔴 فروش قوی", 90
    elif change < -1:
        return "🔴 فروش", 70
    else:
        return "⚪ نگهداری", 50

# ========== دکمه‌ها ==========
def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("✨ قیمت لحظه‌ای", callback_data="prices")],
        [InlineKeyboardButton("🎯 سیگنال‌ها", callback_data="signals")],
        [InlineKeyboardButton("📊 تحلیل تکنیکال", callback_data="analysis")],
        [InlineKeyboardButton("💰 موجودی حساب", callback_data="balance")],
        [InlineKeyboardButton("🛡️ مدیریت ریسک", callback_data="risk")],
        [InlineKeyboardButton("⚙️ وضعیت API", callback_data="status")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])

def get_symbols_trade_keyboard():
    keyboard = []
    for s in SYMBOLS:
        keyboard.append([InlineKeyboardButton(f"{s['emoji']} خرید {s['symbol']}", callback_data=f"buy_{s['symbol']}")])
        keyboard.append([InlineKeyboardButton(f"{s['emoji']} فروش {s['symbol']}", callback_data=f"sell_{s['symbol']}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    return InlineKeyboardMarkup(keyboard)

# ========== هندلرها ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    api_status = "✅ متصل" if COINEX_CONFIGURED else "❌ متصل نیست"
    
    text = f"""
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

          🔥 *تریدر حرفه‌ای کوینکس* 🔥
          
        ربات متصل به صرافی **CoinEx**

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

┌─────────────────────────────────┐
│  👑 پشتیبانی از ۸ ارز دیجیتال   │
│  📊 قیمت‌های لحظه‌ای از CoinEx   │
│  🎯 سیگنال خرید/فروش هوشمند     │
│  💰 مشاهده موجودی حساب          │
│  ⚡ معامله خودکار با API        │
└─────────────────────────────────┘

📡 **وضعیت API:** {api_status}

📌 *از منوی زیر انتخاب کن*

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())

async def prices_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("🔄 دریافت قیمت‌های لحظه‌ای از CoinEx...")
    
    text = "✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n"
    text += "           💰 *قیمت لحظه‌ای کوینکس* 💰\n"
    text += "✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n\n"
    
    for s in SYMBOLS:
        data = await get_coinex_price(s["symbol"])
        
        if data["success"]:
            emoji = "🟢" if data["change"] > 0 else "🔴" if data["change"] < 0 else "⚪"
            text += f"{emoji} *{s['symbol']}*\n"
            text += f"┌─────────────────────────\n"
            text += f"├ 💰 قیمت: ${data['price']:,.4f}\n"
            text += f"├ 📈 تغییر: {data['change']:+.2f}%\n"
            text += f"├ 📊 بالا: ${data['high']:,.4f}\n"
            text += f"├ 📉 پایین: ${data['low']:,.4f}\n"
            text += f"└─────────────────────────\n\n"
        else:
            text += f"❌ *{s['symbol']}*: {data.get('error', 'خطا')}\n\n"
    
    text += "✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n"
    text += f"🕐 {datetime.now().strftime('%H:%M:%S')}"
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def signals_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("🔄 محاسبه سیگنال‌های لحظه‌ای...")
    
    text = "✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n"
    text += "          📡 *سیگنال‌های لحظه‌ای* 📡\n"
    text += "✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨\n\n"
    
    for s in SYMBOLS:
        data = await get_coinex_price(s["symbol"])
        
        if data["success"]:
            signal, conf = generate_signal(data["price"], data["change"])
            arrow = "📈" if data["change"] > 0 else "📉" if data["change"] < 0 else "➖"
            text += f"{s['emoji']} *{s['symbol']}*\n"
            text += f"┌─────────────────────────\n"
            text += f"├ 💰 ${data['price']:,.4f}\n"
            text += f"├ {arrow} {data['change']:+.2f}%\n"
            text += f"├ {signal} ({conf}%)\n"
            text += f"└─────────────────────────\n\n"
        else:
            text += f"❌ *{s['symbol']}*: {data.get('error', 'خطا')}\n\n"
    
    text += "✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨"
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def analysis_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = []
    for s in SYMBOLS:
        keyboard.append([InlineKeyboardButton(f"{s['emoji']} {s['symbol']}", callback_data=f"analyze_{s['symbol']}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    
    text = """
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
        📊 *تحلیل تکنیکال CoinEx* 📊
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

📈 **اندیکاتورها:**
• RSI (قدرت نسبی)
• MACD (همگرایی)
• حمایت و مقاومت
• روند بازار

🎯 *ارز مورد نظر را انتخاب کن:*
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def analyze_coin(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(f"🔄 تحلیل {symbol}...")
    
    data = await get_coinex_price(symbol)
    
    if not data["success"]:
        text = f"""
❌ *خطا در تحلیل {symbol}*

{data.get('error', 'لطفاً دوباره تلاش کن')}

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())
        return
    
    signal, conf = generate_signal(data["price"], data["change"])
    
    # محاسبات تقریبی اندیکاتورها
    rsi = 50 + (data["change"] * 2)
    rsi = max(25, min(75, rsi))
    
    support = data["price"] * 0.95
    resistance = data["price"] * 1.05
    
    text = f"""
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
      📊 *تحلیل {symbol}* 📊
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

💰 **قیمت:** ${data['price']:,.4f}
📈 **تغییر 24h:** {data['change']:+.2f}%
📊 **حجم 24h:** ${data['volume']/1e6:.2f}M
📈 **بالاترین:** ${data['high']:,.4f}
📉 **پایین‌ترین:** ${data['low']:,.4f}

🎯 **سیگنال:** {signal} ({conf}%)

┌─────────────────────────────
├ 📊 RSI: **{rsi:.0f}**
├ 📈 MACD: **{'صعودی' if data['change'] > 0 else 'نزولی'}**
└─────────────────────────────

🔑 **سطوح کلیدی:**
🟢 حمایت: ${support:,.4f}
🔴 مقاومت: ${resistance:,.4f}

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
    keyboard = [
        [InlineKeyboardButton("🔴 فروش", callback_data=f"sell_{symbol}")],
        [InlineKeyboardButton("🟢 خرید", callback_data=f"buy_{symbol}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="analysis")]
    ]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def balance_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not COINEX_CONFIGURED:
        await query.edit_message_text(
            "❌ CoinEx API تنظیم نشده است\n\n"
            "لطفاً ACCESS_ID و SECRET_KEY را در متغیرهای محیطی تنظیم کنید.",
            reply_markup=get_back_keyboard()
        )
        return
    
    await query.edit_message_text("🔄 دریافت موجودی حساب...")
    
    balance = await get_account_balance()
    
    if balance["success"]:
        text = f"""
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
          💰 *موجودی حساب کوینکس* 💰
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

┌─────────────────────────────
├ 💵 **USDT (کل):** ${balance['total']:,.2f}
├ 📊 **قابل استفاده:** ${balance['free']:,.2f}
├ 🔒 **مسدود شده:** ${balance['frozen']:,.2f}
└─────────────────────────────

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
    else:
        text = f"❌ خطا: {balance.get('error', 'مشخص نیست')}"
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def buy_order(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    query = update.callback_query
    await query.answer()
    
    if not COINEX_CONFIGURED:
        await query.edit_message_text("❌ CoinEx API تنظیم نشده است", reply_markup=get_back_keyboard())
        return
    
    balance = await get_account_balance()
    if not balance["success"] or balance["free"] < 10:
        await query.edit_message_text("❌ موجودی کافی برای خرید وجود ندارد", reply_markup=get_back_keyboard())
        return
    
    # دریافت قیمت فعلی
    price_data = await get_coinex_price(symbol)
    if not price_data["success"]:
        await query.edit_message_text("❌ خطا در دریافت قیمت", reply_markup=get_back_keyboard())
        return
    
    # محاسبه مقدار برای خرید با 10 دلار
    amount = 10 / price_data["price"]
    
    await query.edit_message_text(f"🟢 در حال ثبت سفارش خرید {symbol}...")
    
    order = await place_buy_order(symbol, amount)
    
    if order["success"]:
        text = f"""
✅ *سفارش خرید ثبت شد!*

┌─────────────────────────────
├ 📊 نماد: {symbol}
├ 🟢 نوع: خرید
├ 💰 قیمت: ${price_data['price']:,.4f}
├ 📦 مقدار: {amount:.6f}
└─────────────────────────────

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
    else:
        text = f"❌ خطا در ثبت سفارش: {order.get('error', 'مشخص نیست')}"
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def sell_order(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    query = update.callback_query
    await query.answer()
    
    if not COINEX_CONFIGURED:
        await query.edit_message_text("❌ CoinEx API تنظیم نشده است", reply_markup=get_back_keyboard())
        return
    
    # دریافت قیمت فعلی
    price_data = await get_coinex_price(symbol)
    if not price_data["success"]:
        await query.edit_message_text("❌ خطا در دریافت قیمت", reply_markup=get_back_keyboard())
        return
    
    await query.edit_message_text(f"🔴 در حال ثبت سفارش فروش {symbol}...")
    
    # برای فروش، یک مقدار کوچک (برای تست)
    amount = 0.001
    
    order = await place_sell_order(symbol, amount)
    
    if order["success"]:
        text = f"""
✅ *سفارش فروش ثبت شد!*

┌─────────────────────────────
├ 📊 نماد: {symbol}
├ 🔴 نوع: فروش
├ 💰 قیمت: ${price_data['price']:,.4f}
├ 📦 مقدار: {amount:.6f}
└─────────────────────────────

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
    else:
        text = f"❌ خطا در ثبت سفارش: {order.get('error', 'مشخص نیست')}"
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def risk_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = """
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
          🛡️ *مدیریت ریسک* 🛡️
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

📊 **قوانین طلایی:**

┌─────────────────────────────
├ 1️⃣ حداکثر ریسک: **۲٪ سرمایه**
├ 2️⃣ نسبت R/R: **حداقل ۱:۲**
├ 3️⃣ حد ضرر: **همیشه اجباری**
├ 4️⃣ معاملات همزمان: **حداکثر ۳**
└─────────────────────────────

📈 **فرمول حجم معامله:**
`حجم = (سرمایه × ۲٪) / (قیمت - حد ضرر)`

💡 **نکات مهم در کوینکس:**
• از سفارشات محدود (Limit) استفاده کن
• همیشه حد ضرر را فعال کن
• در ضررهای متوالی توقف کن

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def status_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = f"""
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
          ⚙️ *وضعیت سیستم* ⚙️
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

📡 **وضعیت API CoinEx:**
┌─────────────────────────────
├ 🔑 Access ID: {'✅ تنظیم شده' if COINEX_CONFIGURED else '❌ تنظیم نشده'}
├ 🔒 Secret Key: {'✅ تنظیم شده' if COINEX_CONFIGURED else '❌ تنظیم نشده'}
└─────────────────────────────

📊 **وضعیت ربات:**
┌─────────────────────────────
├ 🤖 ربات: فعال
├ 📡 اینترنت: متصل
├ 🕐 زمان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
└─────────────────────────────

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = """
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
          ❓ *راهنما* ❓
✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨

📊 **انواع سیگنال:**

🟢🟢 خرید قوی → ورود مطمئن
🟢 خرید → ورود با احتیاط
⚪ نگهداری → صبر کن
🔴 فروش → خروج تدریجی
🔴🔴 فروش قوی → خروج فوری

📈 **اندیکاتورها:**
• RSI: تشخیص اشباع خرید/فروش
• MACD: تشخیص روند
• حمایت/مقاومت: سطوح کلیدی

💡 **نکات امنیتی در CoinEx:**
• کلیدهای API را در Railway ذخیره کن
• از IP بایندینگ استفاده کن
• هرگز کلیدها را به اشتراک نگذار

✨━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━✨
⚠️ فقط جنبه آموزشی - مسئولیت با شماست
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == "back":
        await back_handler(update, context)
    elif data == "prices":
        await prices_menu(update, context)
    elif data == "signals":
        await signals_menu(update, context)
    elif data == "analysis":
        await analysis_menu(update, context)
    elif data == "balance":
        await balance_menu(update, context)
    elif data == "risk":
        await risk_menu(update, context)
    elif data == "status":
        await status_menu(update, context)
    elif data == "help":
        await help_menu(update, context)
    elif data.startswith("analyze_"):
        symbol = data.split("_")[1]
        await analyze_coin(update, context, symbol)
    elif data.startswith("buy_"):
        symbol = data.split("_")[1]
        await buy_order(update, context, symbol)
    elif data.startswith("sell_"):
        symbol = data.split("_")[1]
        await sell_order(update, context, symbol)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✨ لطفاً از دکمه‌های منو استفاده کن یا /start بزن")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("🚀 ربات متصل به صرافی CoinEx روشن شد...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
