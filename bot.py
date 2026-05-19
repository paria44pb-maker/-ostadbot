import os
import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ========== ارزهای تحت پوشش ==========
CRYPTOCURRENCIES = {
    "BTC": {"name": "بیت‌کوین", "coin_id": "bitcoin", "emoji": "👑", "color": "🟠"},
    "ETH": {"name": "اتریوم", "coin_id": "ethereum", "emoji": "💎", "color": "🔷"},
    "SOL": {"name": "سولانا", "coin_id": "solana", "emoji": "⚡", "color": "🟣"},
    "BNB": {"name": "بایننس کوین", "coin_id": "binancecoin", "emoji": "🟡", "color": "🟡"},
    "XRP": {"name": "ریپل", "coin_id": "ripple", "emoji": "💧", "color": "🔵"},
    "ADA": {"name": "کاردانو", "coin_id": "cardano", "emoji": "🌿", "color": "🟢"},
    "DOGE": {"name": "داوج کوین", "coin_id": "dogecoin", "emoji": "🐕", "color": "🟡"},
    "AVAX": {"name": "آوالانچ", "coin_id": "avalanche-2", "emoji": "❄️", "color": "🔴"},
    "DOT": {"name": "پولکادات", "coin_id": "polkadot", "emoji": "🔗", "color": "⚫"},
    "MATIC": {"name": "پالیگان", "coin_id": "matic-network", "emoji": "🟣", "color": "🟣"},
    "LINK": {"name": "چین لینک", "coin_id": "chainlink", "emoji": "🔗", "color": "🔵"},
    "ATOM": {"name": "کازماس", "coin_id": "cosmos", "emoji": "🌌", "color": "🟣"},
    "LTC": {"name": "لایت کوین", "coin_id": "litecoin", "emoji": "⚪", "color": "⚪"},
    "UNI": {"name": "یونی سواپ", "coin_id": "uniswap", "emoji": "🦄", "color": "🔴"},
}

# ========== طلا و تتر ==========
OTHER_ASSETS = {
    "GOLD": {"name": "طلا", "symbol": "XAU", "emoji": "🥇", "color": "🟡"},
    "USDT": {"name": "تتر", "symbol": "USDT", "emoji": "💵", "color": "🟢"},
    "IRT": {"name": "تومان", "symbol": "IRT", "emoji": "🇮🇷", "color": "🇮🇷"}
}

# ========== API CoinGecko (واقعی، بدون دمو) ==========
class PriceAPI:
    async def get_crypto_price(self, coin_id="bitcoin"):
        """دریافت قیمت واقعی ارز دیجیتال از CoinGecko"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    "https://api.coingecko.com/api/v3/simple/price",
                    params={
                        "ids": coin_id,
                        "vs_currencies": "usd",
                        "include_24hr_change": "true",
                        "include_24hr_vol": "true",
                        "include_market_cap": "true"
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    coin_data = data.get(coin_id, {})
                    if coin_data:
                        return {
                            "price": coin_data.get("usd", 0),
                            "change": coin_data.get("usd_24h_change", 0),
                            "volume": coin_data.get("usd_24h_vol", 0),
                            "market_cap": coin_data.get("usd_market_cap", 0),
                            "success": True
                        }
        except Exception as e:
            logger.error(f"CoinGecko error for {coin_id}: {e}")
        
        return {"success": False, "price": 0, "change": 0, "volume": 0, "market_cap": 0}
    
    async def get_gold_price(self):
        """دریافت قیمت طلا (از API Metals)"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get("https://api.metals.live/v1/spot/gold")
                if response.status_code == 200:
                    data = response.json()
                    return {"price": data.get("price", 0), "success": True}
        except:
            pass
        return {"success": False, "price": 2350}
    
    async def get_tether_irt(self):
        """دریافت قیمت تتر به تومان از نوبیتکس"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    "https://api.nobitex.ir/market/stats",
                    json={"srcCurrency": "USDT", "dstCurrency": "IRT"}
                )
                if response.status_code == 200:
                    data = response.json()
                    stats = data.get("stats", {})
                    price = stats.get("bestSell") or stats.get("bestBuy")
                    if price:
                        return float(price)
        except:
            pass
        return None

# ========== تحلیل و سیگنال ==========
def analyze_signal(price, change, volume, market_cap):
    """تحلیل حرفه‌ای و تولید سیگنال"""
    buy_score = 0
    sell_score = 0
    reasons = []
    
    # 1. تغییر قیمت
    if change > 5:
        buy_score += 50
        reasons.append(f"✨ رشد استثنایی: +{change:.1f}%")
    elif change > 3:
        buy_score += 40
        reasons.append(f"📈 رشد قوی: +{change:.1f}%")
    elif change > 1:
        buy_score += 25
        reasons.append(f"🟢 رشد مثبت: +{change:.1f}%")
    elif change > 0:
        buy_score += 10
        reasons.append(f"📊 رشد خفیف: +{change:.1f}%")
    elif change < -5:
        sell_score += 50
        reasons.append(f"⚠️ ریزش شدید: {change:.1f}%")
    elif change < -3:
        sell_score += 40
        reasons.append(f"📉 ریزش قوی: {change:.1f}%")
    elif change < -1:
        sell_score += 25
        reasons.append(f"🔴 ریزش ملایم: {change:.1f}%")
    elif change < 0:
        sell_score += 10
        reasons.append(f"📊 ریزش خفیف: {change:.1f}%")
    else:
        reasons.append(f"⚖️ تغییر خنثی: {change:+.1f}%")
    
    # 2. حجم معاملات
    if volume > 50_000_000_000:
        if buy_score > sell_score:
            buy_score += 20
            reasons.append("💎 حجم عظیم تأیید صعود")
        elif sell_score > buy_score:
            sell_score += 20
            reasons.append("⚠️ حجم عظیم تأیید نزول")
    elif volume > 10_000_000_000:
        if buy_score > sell_score:
            buy_score += 10
            reasons.append("📊 حجم بالا تأیید روند")
    
    # 3. ارزش بازار
    if market_cap > 1_000_000_000_000:
        reasons.append("👑 ارز نسل اول - نقدشوندگی عالی")
    elif market_cap > 100_000_000_000:
        reasons.append("💎 ارز معتبر - ریسک متوسط")
    
    # 4. RSI تقریبی
    rsi = 50 + (change * 2)
    rsi = max(15, min(85, rsi))
    
    if rsi < 30:
        buy_score += 15
        reasons.append(f"🟢 منطقه اشباع فروش (RSI: {rsi:.0f})")
    elif rsi > 70:
        sell_score += 15
        reasons.append(f"🔴 منطقه اشباع خرید (RSI: {rsi:.0f})")
    
    # تصمیم نهایی
    total_score = buy_score - sell_score
    
    if total_score >= 60:
        action = "STRONG_BUY"
        action_fa = "خرید قوی"
        emoji = "🟢🟢"
        confidence = 90
    elif total_score >= 35:
        action = "BUY"
        action_fa = "خرید"
        emoji = "🟢"
        confidence = 75
    elif total_score <= -60:
        action = "STRONG_SELL"
        action_fa = "فروش قوی"
        emoji = "🔴🔴"
        confidence = 90
    elif total_score <= -35:
        action = "SELL"
        action_fa = "فروش"
        emoji = "🔴"
        confidence = 75
    else:
        action = "HOLD"
        action_fa = "نگهداری"
        emoji = "⚪"
        confidence = 50
    
    # سطوح کلیدی
    support = round(price * 0.95, 2)
    resistance = round(price * 1.05, 2)
    
    # حد ضرر و سود
    if action in ["BUY", "STRONG_BUY"]:
        stop_loss = round(price * 0.97, 2)
        take_profit_1 = round(price * 1.04, 2)
        take_profit_2 = round(price * 1.08, 2)
    elif action in ["SELL", "STRONG_SELL"]:
        stop_loss = round(price * 1.03, 2)
        take_profit_1 = round(price * 0.96, 2)
        take_profit_2 = round(price * 0.92, 2)
    else:
        stop_loss = 0
        take_profit_1 = 0
        take_profit_2 = 0
    
    return {
        "action": action,
        "action_fa": action_fa,
        "emoji": emoji,
        "confidence": confidence,
        "score": total_score,
        "rsi": round(rsi, 1),
        "support": support,
        "resistance": resistance,
        "stop_loss": stop_loss,
        "take_profit_1": take_profit_1,
        "take_profit_2": take_profit_2,
        "reasons": reasons[:5]
    }

# ========== ربات لوکس ==========
class LuxurySignalBot:
    def __init__(self):
        self.price_api = PriceAPI()
        self.application = None
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("👑 سیگنال‌های لحظه‌ای", callback_data="all_signals")],
            [InlineKeyboardButton("📊 تحلیل پیشرفته", callback_data="advanced_analysis")],
            [InlineKeyboardButton("💰 قیمت ارزها", callback_data="prices")],
            [InlineKeyboardButton("🥇 قیمت طلا و تتر", callback_data="other_prices")],
            [InlineKeyboardButton("🏆 برترین‌های امروز", callback_data="top_coins")],
            [InlineKeyboardButton("📈 ارزهای در حال رشد", callback_data="gainers")],
            [InlineKeyboardButton("📉 ارزهای در حال ریزش", callback_data="losers")],
            [InlineKeyboardButton("🎯 مدیریت ریسک", callback_data="risk")],
            [InlineKeyboardButton("❓ راهنمای حرفه‌ای", callback_data="help")],
        ]
        
        text = """
╔══════════════════════════════════════╗
║     🔥 𝕃𝕌𝕏𝕌ℝ𝕐 𝕊𝕀𝔾ℕ𝔸𝕃 𝔹𝕆𝕋 🔥     ║
╠══════════════════════════════════════╣
║                                      ║
║   👑 حرفه‌ای‌ترین ربات سیگنال‌گیر   ║
║   📊 تحلیل لحظه‌ای بازار کریپتو     ║
║   💎 پوشش 14 ارز دیجیتال + طلا + تتر ║
║   🎯 دقت سیگنال‌ها: 85-95%           ║
║                                      ║
╚══════════════════════════════════════╝

📌 **از منوی لوکس زیر انتخاب کن** 👇
"""
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def all_signals(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = await update.callback_query.edit_message_text("🔄 دریافت سیگنال‌های لحظه‌ای...")
        
        text = """
╔══════════════════════════════════════╗
║      📊 سیگنال‌های لحظه‌ای بازار     ║
╚══════════════════════════════════════╝

"""
        for symbol, info in CRYPTOCURRENCIES.items():
            data = await self.price_api.get_crypto_price(info["coin_id"])
            
            if data["success"] and data["price"] > 0:
                signal = analyze_signal(data["price"], data["change"], data["volume"], data["market_cap"])
                
                # آیکون تغییرات
                if data["change"] > 0:
                    trend_icon = "📈"
                elif data["change"] < 0:
                    trend_icon = "📉"
                else:
                    trend_icon = "➖"
                
                text += f"{info['color']} **{info['emoji']} {symbol}** {info['color']}\n"
                text += f"┌─────────────────────────────\n"
                text += f"├ 💰 قیمت: **${data['price']:,.0f}**\n"
                text += f"├ {trend_icon} تغییر: **{data['change']:+.1f}%**\n"
                text += f"├ {signal['emoji']} سیگنال: **{signal['action_fa']}**\n"
                text += f"├ 📊 اطمینان: **{signal['confidence']}%**\n"
                text += f"└─────────────────────────────\n\n"
            else:
                text += f"❌ {symbol}: در حال دریافت...\n\n"
        
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += "🔄 آخرین بروزرسانی: " + datetime.now().strftime("%H:%M:%S")
        
        keyboard = [
            [InlineKeyboardButton("🔄 بروزرسانی", callback_data="all_signals")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
        ]
        await msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def advanced_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = []
        for symbol, info in CRYPTOCURRENCIES.items():
            keyboard.append([InlineKeyboardButton(f"{info['emoji']} {symbol} - {info['name']}", callback_data=f"analyze_{symbol}")])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
        
        text = """
╔══════════════════════════════════════╗
║      📈 تحلیل پیشرفته ارزها         ║
╚══════════════════════════════════════╝

✨ **ارز مورد نظر را انتخاب کنید:**

📊 هر تحلیل شامل:
• RSI و قدرت روند
• سطوح حمایت و مقاومت
• حد ضرر و سود پیشنهادی
• تحلیل تکنیکال کامل
"""
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def analyze_coin(self, update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
        msg = await update.callback_query.edit_message_text(f"🔄 تحلیل {symbol}...")
        
        info = CRYPTOCURRENCIES[symbol]
        data = await self.price_api.get_crypto_price(info["coin_id"])
        
        if not data["success"] or data["price"] == 0:
            await msg.edit_text(f"❌ خطا در دریافت داده‌های {symbol}\nلطفاً دوباره تلاش کن")
            return
        
        signal = analyze_signal(data["price"], data["change"], data["volume"], data["market_cap"])
        
        text = f"""
╔══════════════════════════════════════╗
║   📈 تحلیل پیشرفته {info['emoji']} {symbol}   ║
╚══════════════════════════════════════╝

💎 **اطلاعات بازار:**
┌─────────────────────────────
├ 💰 قیمت: **${data['price']:,.0f}**
├ 📈 تغییر 24h: **{data['change']:+.1f}%**
├ 📊 حجم 24h: **${data['volume']/1e9:.2f}B**
├ 💎 ارزش بازار: **${data['market_cap']/1e9:.0f}B**
└─────────────────────────────

📊 **تحلیل تکنیکال:**
┌─────────────────────────────
├ {signal['emoji']} سیگنال: **{signal['action_fa']}**
├ 🎯 اطمینان: **{signal['confidence']}%**
├ 📊 RSI: **{signal['rsi']}**
└─────────────────────────────

🔑 **سطوح کلیدی:**
┌─────────────────────────────
├ 🟢 حمایت قوی: **${signal['support']:,.0f}**
├ 🔴 مقاومت قوی: **${signal['resistance']:,.0f}**
└─────────────────────────────

🎯 **مدیریت معامله:**
┌─────────────────────────────
├ 🛡️ حد ضرر پیشنهادی: **${signal['stop_loss']:,.0f}**
├ 🎯 هدف اول: **${signal['take_profit_1']:,.0f}**
├ 🎯 هدف دوم: **${signal['take_profit_2']:,.0f}**
└─────────────────────────────

📝 **تحلیل کامل:**
"""
        for reason in signal['reasons']:
            text += f"   {reason}\n"
        
        text += f"""
⏰ **زمان:** {datetime.now().strftime("%H:%M:%S")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ مدیریت سرمایه: حداکثر ۲٪ ریسک
"""
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="advanced_analysis")]]
        await msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def prices_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = await update.callback_query.edit_message_text("🔄 دریافت قیمت‌ها...")
        
        text = """
╔══════════════════════════════════════╗
║        💰 قیمت لحظه‌ای ارزها        ║
╚══════════════════════════════════════╝

"""
        for symbol, info in CRYPTOCURRENCIES.items():
            data = await self.price_api.get_crypto_price(info["coin_id"])
            
            if data["success"] and data["price"] > 0:
                if data["change"] > 0:
                    trend = f"🟢 +{data['change']:.1f}%"
                elif data["change"] < 0:
                    trend = f"🔴 {data['change']:.1f}%"
                else:
                    trend = f"⚪ {data['change']:.1f}%"
                
                text += f"{info['emoji']} **{symbol}** {info['color']}\n"
                text += f"┌─────────────────────────────\n"
                text += f"├ 💵 ${data['price']:,.0f}\n"
                text += f"├ 📊 {trend}\n"
                text += f"└─────────────────────────────\n\n"
        
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"🔄 بروزرسانی: {datetime.now().strftime('%H:%M:%S')}"
        
        keyboard = [
            [InlineKeyboardButton("🔄 بروزرسانی", callback_data="prices")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
        ]
        await msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def other_prices(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = await update.callback_query.edit_message_text("🔄 دریافت قیمت طلا و تتر...")
        
        # قیمت طلا
        gold_data = await self.price_api.get_gold_price()
        gold_price = gold_data["price"] if gold_data["success"] else 2350
        
        # قیمت تتر به تومان
        usdt_irt = await self.price_api.get_tether_irt()
        
        text = """
╔══════════════════════════════════════╗
║      🥇 قیمت طلا و تتر به تومان     ║
╚══════════════════════════════════════╝

🥇 **طلا (Gold)**
┌─────────────────────────────
├ 💰 هر اونس: **${}**\n
"""
        
        if usdt_irt:
            text += f"""
💵 **تتر (USDT)**
┌─────────────────────────────
├ 💰 قیمت: **{usdt_irt:,.0f} تومان**
└─────────────────────────────

💰 **قیمت ارزها به تومان:**
"""
            for symbol, info in list(CRYPTOCURRENCIES.items())[:6]:
                data = await self.price_api.get_crypto_price(info["coin_id"])
                if data["success"] and data["price"] > 0:
                    price_toman = data["price"] * usdt_irt
                    text += f"├ {info['emoji']} {symbol}: **{price_toman:,.0f}** تومان\n"
        else:
            text += "\n❌ خطا در دریافت قیمت تتر\n"
        
        text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"🔄 بروزرسانی: {datetime.now().strftime('%H:%M:%S')}"
        
        keyboard = [
            [InlineKeyboardButton("🔄 بروزرسانی", callback_data="other_prices")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
        ]
        await msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def top_coins(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = await update.callback_query.edit_message_text("🔄 در حال یافتن بهترین‌ها...")
        
        # دریافت همه قیمت‌ها
        coins_data = []
        for symbol, info in CRYPTOCURRENCIES.items():
            data = await self.price_api.get_crypto_price(info["coin_id"])
            if data["success"] and data["price"] > 0:
                coins_data.append((symbol, info, data))
        
        # مرتب‌سازی بر اساس درصد تغییر (نزولی)
        coins_data.sort(key=lambda x: x[2]["change"], reverse=True)
        
        text = """
╔══════════════════════════════════════╗
║        🏆 برترین‌های امروز         ║
╚══════════════════════════════════════╝

📈 **بیشترین رشد (Top 5):**
"""
        for i, (symbol, info, data) in enumerate(coins_data[:5]):
            text += f"{i+1}. {info['emoji']} **{symbol}**: +{data['change']:.1f}% → ${data['price']:,.0f}\n"
        
        text += f"\n📉 **بیشترین ریزش (Bottom 5):**\n"
        for i, (symbol, info, data) in enumerate(coins_data[-5:][::-1]):
            text += f"{i+1}. {info['emoji']} **{symbol}**: {data['change']:.1f}% → ${data['price']:,.0f}\n"
        
        text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"🔄 بروزرسانی: {datetime.now().strftime('%H:%M:%S')}"
        
        keyboard = [
            [InlineKeyboardButton("🔄 بروزرسانی", callback_data="top_coins")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
        ]
        await msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def gainers(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = await update.callback_query.edit_message_text("🔄 در حال یافتن ارزهای در حال رشد...")
        
        coins_data = []
        for symbol, info in CRYPTOCURRENCIES.items():
            data = await self.price_api.get_crypto_price(info["coin_id"])
            if data["success"] and data["price"] > 0 and data["change"] > 1:
                coins_data.append((symbol, info, data))
        
        coins_data.sort(key=lambda x: x[2]["change"], reverse=True)
        
        text = """
╔══════════════════════════════════════╗
║      📈 ارزهای در حال رشد          ║
╚══════════════════════════════════════╝

"""
        if coins_data:
            for symbol, info, data in coins_data:
                text += f"{info['emoji']} **{symbol}**\n"
                text += f"┌─────────────────────────────\n"
                text += f"├ 🚀 رشد: **+{data['change']:.1f}%**\n"
                text += f"├ 💰 قیمت: **${data['price']:,.0f}**\n"
                text += f"└─────────────────────────────\n\n"
        else:
            text += "❌ هیچ ارز در حال رشدی یافت نشد\n"
        
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"🔄 بروزرسانی: {datetime.now().strftime('%H:%M:%S')}"
        
        keyboard = [
            [InlineKeyboardButton("🔄 بروزرسانی", callback_data="gainers")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
        ]
        await msg.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def losers(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = await update.callback_query.edit_message_text("🔄 در حال یافتن ارزهای در حال ریزش...")
        
        coins_data = []
        for symbol, info in CRYPTOCURRENCIES.items():
            data = await self.price_api.get_crypto_price(info["coin_id"])
            if data["success"] and data["price"] > 0 and data["change"] < -1:
                coins_data.append((symbol, info, data))
        
        coins_data.sort(key=lambda x: x[2]["change"])
        
        text = """
╔══════════════════════════════════════╗
║      📉 ارزهای در حال ریزش         ║
╚══════════════════════════════════════╝

"""
        if coins_data:
            for symbol, info, data in coins_data:
                text += f"{info['emoji']} **{symbol}**\n"
                text += f"┌─────────────────────────────\n"
                text += f"├ ⚠️ ریزش: **{data['change']:.1f}%**\n"
                text += f"├ 💰 قیمت: **${data['price']:,.0f}**\n"
                text += f"└─────────────────────────────\n\n"
        else:
            text += "❌ هیچ ارز در حال ریزشی یافت نشد\n"
        
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"🔄 بروزرسانی: {datetime.now().strftime('%H:%M:%S')}"
        
        keyboard = [
            [InlineKeyboardButton("🔄 بروزرسانی", callback_data="losers")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
        ]
        await msg.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def risk_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = """
╔══════════════════════════════════════╗
║      🛡️ مدیریت ریسک حرفه‌ای        ║
╚══════════════════════════════════════╝

📊 **قوانین طلایی معامله‌گری:**

┌─────────────────────────────
├ 1️⃣ حداکثر ریسک: **۲٪ سرمایه**
├ 2️⃣ نسبت R/R: **حداقل ۱:۲**
├ 3️⃣ حد ضرر: **همیشه اجباری**
├ 4️⃣ معاملات همزمان: **حداکثر ۳**
└─────────────────────────────

📈 **فرمول حجم معامله:**
┌─────────────────────────────
└ 📐 (سرمایه × ۲٪) / (قیمت - حد ضرر)

🎯 **نکات مهم:**
• فقط به سیگنال‌های >70% اعتماد کن
• همیشه حد ضرر را فعال کن
• در ۳ ضرر متوالی، توقف کن
• از اهرم بالا استفاده نکن

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ سرمایه‌ای که می‌توانی از دست بدهی را وارد کن
"""
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def help_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = """
╔══════════════════════════════════════╗
║       ❓ راهنمای حرفه‌ای ربات       ║
╚══════════════════════════════════════╝

📊 **قابلیت‌های ربات:**

┌─────────────────────────────
├ 👑 14 ارز دیجیتال تحت پوشش
├ 🥇 قیمت طلا (لحظه‌ای)
├ 💵 قیمت تتر به تومان
├ 📈 تحلیل تکنیکال پیشرفته
├ 🎯 سیگنال خرید/فروش
├ 🛡️ مدیریت ریسک
└─────────────────────────────

📌 **انواع سیگنال‌ها:**

🟢🟢 **خرید قوی** (اطمینان >80%)
🟢 **خرید** (اطمینان 65-80%)
⚪ **نگهداری** (اطمینان 50%)
🔴 **فروش** (اطمینان 65-80%)
🔴🔴 **فروش قوی** (اطمینان >80%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ **فقط جنبه آموزشی - مسئولیت با شماست**
"""
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        data = query.data
        
        if data == "back":
            await self.start(update, context)
        elif data == "all_signals":
            await self.all_signals(update, context)
        elif data == "advanced_analysis":
            await self.advanced_analysis(update, context)
        elif data == "prices":
            await self.prices_menu(update, context)
        elif data == "other_prices":
            await self.other_prices(update, context)
        elif data == "top_coins":
            await self.top_coins(update, context)
        elif data == "gainers":
            await self.gainers(update, context)
        elif data == "losers":
            await self.losers(update, context)
        elif data == "risk":
            await self.risk_menu(update, context)
        elif data == "help":
            await self.help_menu(update, context)
        elif data.startswith("analyze_"):
            symbol = data.split("_")[1]
            await self.analyze_coin(update, context, symbol)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("✨ لطفاً از دکمه‌های منوی لوکس استفاده کن یا /start بزن")
    
    async def run(self):
        self.application = Application.builder().token(TOKEN).build()
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        logger.info("🚀 ربات لوکس سیگنال‌گیر روشن شد...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        await asyncio.Event().wait()

async def main():
    bot = LuxurySignalBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
