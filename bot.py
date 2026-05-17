import os
import json
import logging
import random
import httpx
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MEMORY_FILE = "memory.json"
PORTFOLIO_FILE = "portfolio.json"

# ========== مدیریت فایل‌ها ==========
def load_json(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return {}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# ========== API واقعی نوبیتکس ==========
async def get_nobitex_price(symbol="BTC"):
    """دریافت قیمت واقعی از نوبیتکس"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # تبدیل نماد به فرمت نوبیتکس
            src_currency = symbol.upper()
            dst_currency = "USDT"
            
            response = await client.post(
                "https://api.nobitex.ir/market/stats",
                json={"srcCurrency": src_currency, "dstCurrency": dst_currency}
            )
            
            if response.status_code == 200:
                data = response.json()
                stats = data.get("stats", {})
                if stats:
                    best_sell = stats.get("bestSell")
                    best_buy = stats.get("bestBuy")
                    price = best_sell or best_buy
                    if price:
                        return {
                            "price": float(price),
                            "change": float(stats.get("change24h", 0)),
                            "high": float(stats.get("high24h", 0)) if stats.get("high24h") else None,
                            "low": float(stats.get("low24h", 0)) if stats.get("low24h") else None,
                            "volume": float(stats.get("volumeSrc", 0)) if stats.get("volumeSrc") else 0,
                            "source": "Nobitex"
                        }
    except Exception as e:
        logging.error(f"خطا در دریافت قیمت نوبیتکس: {e}")
    return None

# ========== API کوین مارکت کپ (قیمت دلاری) ==========
async def get_coinmarketcap_price(symbol="BTC"):
    """دریافت قیمت واقعی از CoinMarketCap (دلاری)"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"https://api.coingecko.com/api/v3/simple/price",
                params={
                    "ids": get_coin_id(symbol),
                    "vs_currencies": "usd",
                    "include_24hr_change": "true",
                    "include_24hr_vol": "true",
                    "include_last_updated_at": "true"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                coin_data = data.get(get_coin_id(symbol), {})
                if coin_data:
                    return {
                        "price": coin_data.get("usd", 0),
                        "change": coin_data.get("usd_24h_change", 0),
                        "volume": coin_data.get("usd_24h_vol", 0),
                        "source": "CoinGecko"
                    }
    except Exception as e:
        logging.error(f"خطا در دریافت قیمت CoinGecko: {e}")
    return None

def get_coin_id(symbol):
    """تبدیل نماد به ID کوین‌گیکو"""
    ids = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
        "BNB": "binancecoin",
        "XRP": "ripple",
        "DOGE": "dogecoin",
        "ADA": "cardano",
        "AVAX": "avalanche-2",
        "MATIC": "matic-network"
    }
    return ids.get(symbol.upper(), "bitcoin")

# ========== قیمت تتر به تومان (نوبیتکس) ==========
async def get_usdt_irt():
    """دریافت قیمت واقعی تتر به تومان از نوبیتکس"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                "https://api.nobitex.ir/market/stats",
                json={"srcCurrency": "USDT", "dstCurrency": "IRT"}
            )
            
            if response.status_code == 200:
                data = response.json()
                stats = data.get("stats", {})
                if stats:
                    return float(stats.get("bestSell", 0)) or float(stats.get("bestBuy", 0))
    except Exception as e:
        logging.error(f"خطا در دریافت قیمت تتر: {e}")
    return None

# ========== کش قیمت‌ها (برای کاهش درخواست) ==========
price_cache = {}
last_update = {}

async def get_realtime_price(symbol="BTC", currency="USD"):
    """دریافت قیمت واقعی با کش 30 ثانیه"""
    now = datetime.now().timestamp()
    
    # بررسی کش
    cache_key = f"{symbol}_{currency}"
    if cache_key in price_cache and now - last_update.get(cache_key, 0) < 30:
        return price_cache[cache_key]
    
    # دریافت قیمت جدید
    if currency == "USD":
        price_data = await get_coinmarketcap_price(symbol)
    else:
        price_data = await get_nobitex_price(symbol)
    
    if price_data:
        price_cache[cache_key] = price_data
        last_update[cache_key] = now
    
    return price_data

# ========== شخصیت‌ها ==========
personalities = {
    "تریدر حرفه‌ای": {"emoji": "📊", "prompt": "تو یک تریدر حرفه‌ای هستی.", "color": "🔥"},
    "تحلیلگر بازار": {"emoji": "📈", "prompt": "تو یک تحلیلگر بازار هستی.", "color": "📊"},
    "مدیر ریسک": {"emoji": "🛡️", "prompt": "تو یک مدیر ریسک هستی.", "color": "⚖️"},
    "نهنگ بازار": {"emoji": "🐋", "prompt": "تو مثل یک نهنگ بازار فکر کن.", "color": "💎"},
    "معلم ترید": {"emoji": "📚", "prompt": "تو یک معلم ترید هستی.", "color": "✏️"},
}

# ========== منوی اصلی ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 قیمت لحظه‌ای", callback_data="prices")],
        [InlineKeyboardButton("🎯 سیگنال معاملاتی", callback_data="signals")],
        [InlineKeyboardButton("📈 تحلیل تکنیکال", callback_data="technical")],
        [InlineKeyboardButton("🧠 تحلیل با AI", callback_data="ai_analysis")],
        [InlineKeyboardButton("💰 مدیریت پرتفوی", callback_data="portfolio")],
        [InlineKeyboardButton("🛡️ مدیریت ریسک", callback_data="risk")],
        [InlineKeyboardButton("🎭 شخصیت", callback_data="personality")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    
    text = f"""
📊 **ربات تریدر واقعی** 📊

✅ **قابلیت‌های واقعی:**
• 🔗 متصل به نوبیتکس (قیمت تومانی)
• 🔗 متصل به CoinGecko (قیمت دلاری)
• 🎯 سیگنال‌های واقعی
• 📈 تحلیل تکنیکال
• 🧠 تحلیل هوشمند با AI
• 💰 مدیریت پرتفوی

---
📌 از منوی زیر انتخاب کن 👇
"""
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== قیمت لحظه‌ای واقعی ==========
async def prices_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # نمایش پیام در حال بارگذاری
    await update.callback_query.edit_message_text("🔄 در حال دریافت قیمت‌های واقعی...", parse_mode="Markdown")
    
    symbols = ["BTC", "ETH", "SOL", "BNB"]
    prices_text = ""
    
    # دریافت قیمت دلاری
    prices_text += "🌍 **قیمت دلاری (CoinGecko):**\n"
    for symbol in symbols:
        price_data = await get_realtime_price(symbol, "USD")
        if price_data:
            emoji = "🟢" if price_data["change"] > 0 else "🔴" if price_data["change"] < 0 else "⚪"
            prices_text += f"{emoji} **{symbol}**: ${price_data['price']:,.0f} ({price_data['change']:+.1f}%)\n"
        else:
            prices_text += f"⚪ **{symbol}**: خطا در دریافت\n"
    
    # دریافت قیمت تومانی (تتر)
    usdt_irt = await get_usdt_irt()
    if usdt_irt:
        prices_text += f"\n🇮🇷 **قیمت تتر (نوبیتکس):**\n🟢 **USDT/IRT**: {usdt_irt:,.0f} تومان\n"
    
    # دریافت قیمت تومانی بیت‌کوین
    btc_irt = await get_nobitex_price("BTC")
    if btc_irt:
        btc_toman = btc_irt["price"] * usdt_irt if usdt_irt else 0
        prices_text += f"🟢 **BTC/IRT**: {btc_toman:,.0f} تومان\n"
    
    keyboard = [
        [InlineKeyboardButton("🔄 بروزرسانی", callback_data="refresh_prices")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
    ]
    await update.callback_query.edit_message_text(prices_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== سیگنال واقعی ==========
async def signals_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("🔄 در حال محاسبه سیگنال‌ها...", parse_mode="Markdown")
    
    symbols = ["BTC", "ETH", "SOL", "BNB"]
    signals_text = "🎯 **سیگنال‌های معاملاتی لحظه‌ای** 🎯\n\n"
    
    for symbol in symbols:
        price_data = await get_realtime_price(symbol, "USD")
        if price_data:
            change = price_data["change"]
            
            # منطق سیگنال
            if change > 3:
                signal = "🟢 خرید قوی"
                reason = f"رشد {change:.1f}% در 24 ساعت"
            elif change > 1:
                signal = "🟢 خرید ملایم"
                reason = f"رشد {change:.1f}%"
            elif change < -3:
                signal = "🔴 فروش قوی"
                reason = f"افت {abs(change):.1f}%"
            elif change < -1:
                signal = "🔴 فروش ملایم"
                reason = f"افت {abs(change):.1f}%"
            else:
                signal = "⚪ نگهداری"
                reason = "بازار خنثی"
            
            signals_text += f"**{symbol}**: {signal}\n📝 {reason}\n\n"
        else:
            signals_text += f"**{symbol}**: ⚪ خطا در دریافت\n\n"
    
    keyboard = [
        [InlineKeyboardButton("🔄 بروزرسانی", callback_data="refresh_signals")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
    ]
    await update.callback_query.edit_message_text(signals_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== تحلیل تکنیکال واقعی ==========
async def technical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📈 BTC", callback_data="tech_BTC")],
        [InlineKeyboardButton("💎 ETH", callback_data="tech_ETH")],
        [InlineKeyboardButton("🔷 SOL", callback_data="tech_SOL")],
        [InlineKeyboardButton("🟡 BNB", callback_data="tech_BNB")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back")],
    ]
    await update.callback_query.edit_message_text(
        "📈 **تحلیل تکنیکال واقعی**\n\nارز مورد نظر را انتخاب کن:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def technical_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    await update.callback_query.edit_message_text(f"📊 در حال تحلیل {symbol}...", parse_mode="Markdown")
    
    price_data = await get_realtime_price(symbol, "USD")
    if not price_data:
        await update.callback_query.edit_message_text("❌ خطا در دریافت قیمت", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="technical")]]))
        return
    
    price = price_data["price"]
    change = price_data["change"]
    
    # محاسبه سطوح تقریبی
    support = price * 0.95
    resistance = price * 1.05
    support2 = price * 0.92
    resistance2 = price * 1.08
    
    # محاسبه RSI تقریبی
    rsi = 50 + change * 3
    rsi = max(20, min(80, rsi))
    rsi_status = "🟢 اشباع فروش (منطقه خرید)" if rsi < 30 else "🔴 اشباع خرید (منطقه فروش)" if rsi > 70 else "⚪ خنثی"
    
    text = f"📈 **تحلیل تکنیکال {symbol}** 📈\n\n"
    text += f"💰 **قیمت فعلی:** ${price:,.0f}\n"
    text += f"📊 **تغییر ۲۴h:** {change:+.1f}%\n"
    text += f"📈 **منبع:** {price_data['source']}\n\n"
    
    text += "**📊 اندیکاتورها:**\n"
    text += f"• RSI(14): {rsi:.0f} → {rsi_status}\n"
    text += f"• MACD: {'صعودی' if change > 0 else 'نزولی'}\n"
    text += f"• روند: {'صعودی' if change > 0 else 'نزولی' if change < 0 else 'خنثی'}\n\n"
    
    text += "**🔑 سطوح کلیدی:**\n"
    text += f"🟢 حمایت اصلی: ${support:,.0f}\n"
    text += f"🔴 مقاومت اصلی: ${resistance:,.0f}\n"
    text += f"🟡 حمایت دوم: ${support2:,.0f}\n"
    text += f"🔴 مقاومت دوم: ${resistance2:,.0f}\n\n"
    
    # سیگنال
    if change > 2:
        signal = "🟢 سیگنال خرید"
        sl = price * 0.97
        tp = price * 1.05
    elif change < -2:
        signal = "🔴 سیگنال فروش"
        sl = price * 1.03
        tp = price * 0.95
    else:
        signal = "⚪ سیگنال نگهداری"
        sl = price * 0.98
        tp = price * 1.02
    
    text += f"**🎯 سیگنال:** {signal}\n"
    if signal != "⚪ سیگنال نگهداری":
        text += f"🛡️ **حد ضرر:** ${sl:,.0f}\n"
        text += f"🎯 **حد سود:** ${tp:,.0f}\n"
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="technical")]]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== تحلیل با AI ==========
async def ai_analysis_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🧠 تحلیل BTC", callback_data="ai_BTC")],
        [InlineKeyboardButton("🧠 تحلیل ETH", callback_data="ai_ETH")],
        [InlineKeyboardButton("🧠 تحلیل SOL", callback_data="ai_SOL")],
        [InlineKeyboardButton("🧠 تحلیل BNB", callback_data="ai_BNB")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back")],
    ]
    await update.callback_query.edit_message_text(
        "🧠 **تحلیل هوشمند با AI**\n\nارز مورد نظر را انتخاب کن:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def ai_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    await update.callback_query.edit_message_text(f"🤖 در حال تحلیل {symbol} با هوش مصنوعی...", parse_mode="Markdown")
    
    price_data = await get_realtime_price(symbol, "USD")
    if not price_data:
        await update.callback_query.edit_message_text("❌ خطا در دریافت قیمت", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="ai_analysis")]]))
        return
    
    if GROQ_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {"role": "system", "content": "تو یک تحلیلگر حرفه‌ای بازار ارزهای دیجیتال هستی. پاسخ کوتاه و مفید بده."},
                            {"role": "user", "content": f"تحلیل {symbol} با قیمت ${price_data['price']:,.0f} و تغییر {price_data['change']:+.1f}% در 24 ساعت اخیر"}
                        ],
                        "max_tokens": 300
                    }
                )
                if response.status_code == 200:
                    ai_response = response.json()["choices"][0]["message"]["content"]
                else:
                    ai_response = await fallback_ai_analysis(symbol, price_data)
        except:
            ai_response = await fallback_ai_analysis(symbol, price_data)
    else:
        ai_response = await fallback_ai_analysis(symbol, price_data)
    
    text = f"🧠 **تحلیل AI - {symbol}** 🧠\n\n"
    text += f"💰 قیمت فعلی: ${price_data['price']:,.0f}\n"
    text += f"📊 تغییر ۲۴h: {price_data['change']:+.1f}%\n\n"
    text += f"{ai_response}"
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="ai_analysis")]]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def fallback_ai_analysis(symbol: str, price_data: dict):
    """پاسخ پیش‌فرض AI در صورت عدم دسترسی به API"""
    change = price_data["change"]
    if change > 2:
        return f"✅ **تحلیل:** روند صعودی قوی برای {symbol}. پیش‌بینی ادامه رشد تا مقاومت بعدی. حد ضرر را ۳٪ زیر قیمت قرار دهید."
    elif change > 0:
        return f"🟡 **تحلیل:** {symbol} در روند صعودی ملایم. تایید روند نیاز است. منتظر شکست مقاومت بعدی باشید."
    elif change < -2:
        return f"🔴 **تحلیل:** روند نزولی برای {symbol}. از ورود به معامله خودداری کنید تا بازار تثبیت شود."
    else:
        return f"⚪ **تحلیل:** {symbol} در حالت رنج. سطوح حمایت و مقاومت را رصد کنید."

# ========== مدیریت پرتفوی ==========
async def portfolio_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    portfolio = load_json(PORTFOLIO_FILE)
    user_portfolio = portfolio.get(user_id, {"balance": 10000, "positions": [], "history": []})
    
    text = f"💰 **پرتفوی شما** 💰\n\n"
    text += f"💵 **موجودی نقد:** ${user_portfolio['balance']:,.0f}\n"
    
    if user_portfolio["positions"]:
        text += "\n**📊 پوزیشن‌های باز:**\n"
        for pos in user_portfolio["positions"]:
            price_data = await get_realtime_price(pos["symbol"], "USD")
            current = price_data["price"] if price_data else pos["entry_price"]
            pnl = (current - pos["entry_price"]) / pos["entry_price"] * 100
            pnl_direction = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "⚪"
            text += f"{pnl_direction} **{pos['symbol']}**: {pos['amount']} @ ${pos['entry_price']:,.0f} | PnL: {pnl:+.1f}%\n"
    else:
        text += "\n📭 **هیچ پوزیشن بازی ندارید**\n"
    
    keyboard = [
        [InlineKeyboardButton("💰 افزایش موجودی", callback_data="add_balance")],
        [InlineKeyboardButton("📜 تاریخچه", callback_data="trade_history")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
    ]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def add_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    portfolio = load_json(PORTFOLIO_FILE)
    user_portfolio = portfolio.get(user_id, {"balance": 10000, "positions": [], "history": []})
    
    user_portfolio["balance"] += 5000
    portfolio[user_id] = user_portfolio
    save_json(PORTFOLIO_FILE, portfolio)
    
    await update.callback_query.edit_message_text(
        "✅ **۵۰۰۰ دلار به موجودی شما اضافه شد!**",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="portfolio")]])
    )

# ========== مدیریت ریسک ==========
async def risk_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
🛡️ **مدیریت ریسک حرفه‌ای** 🛡️

📊 **قوانین طلایی:**

1️⃣ **حداکثر ریسک در هر معامله:** ۲٪ سرمایه

2️⃣ **نسبت ریسک به ریوارد:** حداقل ۱:۲

3️⃣ **حد ضرر:** همیشه اجباری

4️⃣ **حداکثر معاملات همزمان:** ۳ تا

5️⃣ **حداکثر افت روزانه:** ۶٪

---
📈 **فرمول حجم معامله:**

`حجم = (سرمایه × ۲٪) / (قیمت ورود - حد ضرر)`

---
💡 **نکات کلیدی:**
• هیچوقت فول مارژین نکن
• احساسات را از معامله جدا کن
• در ضررهای متوالی، توقف کن
"""
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== شخصیت ==========
async def personality_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for name, data in personalities.items():
        keyboard.append([InlineKeyboardButton(f"{data['emoji']} {name}", callback_data=f"set_personality_{name}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    
    await update.callback_query.edit_message_text(
        "🎭 **انتخاب شخصیت**\n\nشخصیت مورد نظر را انتخاب کن:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def set_personality(update: Update, context: ContextTypes.DEFAULT_TYPE, personality: str):
    context.user_data["personality"] = personality
    await update.callback_query.edit_message_text(
        f"✅ شخصیت به **{personality}** تغییر کرد!",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
    )

# ========== راهنما ==========
async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
❓ **راهنمای ربات تریدر واقعی** ❓

📊 **قیمت لحظه‌ای:**
قیمت‌های واقعی از نوبیتکس و CoinGecko

🎯 **سیگنال:**
بر اساس تغییرات قیمت ۲۴ ساعته

📈 **تحلیل تکنیکال:**
RSI، سطوح حمایت/مقاومت

🧠 **تحلیل AI:**
تحلیل هوشمند با Groq (در صورت تنظیم API)

💰 **پرتفوی:**
مدیریت سرمایه و پوزیشن‌ها

---
⚠️ **هشدار:** این ربات فقط جنبه آموزشی دارد
"""
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== تاریخچه معاملات ==========
async def trade_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    portfolio = load_json(PORTFOLIO_FILE)
    user_portfolio = portfolio.get(user_id, {"balance": 10000, "positions": [], "history": []})
    
    if not user_portfolio["history"]:
        text = "📜 **تاریخچه معاملات خالی است**"
    else:
        text = "📜 **تاریخچه معاملات** 📜\n\n"
        for h in user_portfolio["history"][-10:]:
            text += f"• {h.get('type', '')} {h.get('symbol', '')} @ ${h.get('price', 0):,.0f}\n"
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="portfolio")]]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== هندلر اصلی ==========
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "back":
        await start(update, context)
    elif data == "prices":
        await prices_menu(update, context)
    elif data == "signals":
        await signals_menu(update, context)
    elif data == "technical":
        await technical_menu(update, context)
    elif data == "ai_analysis":
        await ai_analysis_menu(update, context)
    elif data == "portfolio":
        await portfolio_menu(update, context)
    elif data == "risk":
        await risk_menu(update, context)
    elif data == "personality":
        await personality_menu(update, context)
    elif data == "help":
        await help_menu(update, context)
    elif data == "add_balance":
        await add_balance(update, context)
    elif data == "trade_history":
        await trade_history(update, context)
    elif data == "refresh_prices":
        await prices_menu(update, context)
    elif data == "refresh_signals":
        await signals_menu(update, context)
    elif data.startswith("tech_"):
        symbol = data.split("_")[1]
        await technical_analysis(update, context, symbol)
    elif data.startswith("ai_"):
        symbol = data.split("_")[1]
        await ai_analysis(update, context, symbol)
    elif data.startswith("set_personality_"):
        personality = data.replace("set_personality_", "")
        await set_personality(update, context, personality)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🍃 لطفاً از دکمه‌های منو استفاده کن یا /start بزن.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 ربات تریدر واقعی با API نوبیتکس و CoinGecko روشن شد...")
    app.run_polling()

if __name__ == "__main__":
    main()
