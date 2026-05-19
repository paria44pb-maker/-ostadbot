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

# ========== قیمت‌های دمو (فال‌بک) ==========
DEMO_PRICES = {
    "BTC": {"price": 67234, "change": 2.3, "volume": 28500000000},
    "ETH": {"price": 3456, "change": 1.8, "volume": 15200000000},
    "SOL": {"price": 156.7, "change": 5.2, "volume": 8300000000},
    "BNB": {"price": 582, "change": -1.2, "volume": 3100000000},
}

# ========== API CoinGecko (بدون تحریم) ==========
class PriceAPI:
    async def get_price(self, symbol="BTC"):
        """دریافت قیمت از CoinGecko"""
        coin_ids = {
            "BTC": "bitcoin",
            "ETH": "ethereum", 
            "SOL": "solana",
            "BNB": "binancecoin"
        }
        coin_id = coin_ids.get(symbol, "bitcoin")
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    "https://api.coingecko.com/api/v3/simple/price",
                    params={
                        "ids": coin_id, 
                        "vs_currencies": "usd", 
                        "include_24hr_change": "true",
                        "include_24hr_vol": "true"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    coin_data = data.get(coin_id, {})
                    
                    if coin_data:
                        return {
                            "symbol": symbol,
                            "price": coin_data.get("usd", 0),
                            "change": coin_data.get("usd_24h_change", 0),
                            "volume": coin_data.get("usd_24h_vol", 0),
                            "source": "CoinGecko",
                            "timestamp": datetime.now().strftime("%H:%M:%S"),
                            "demo": False
                        }
                    else:
                        logger.error(f"No data for {symbol}")
                else:
                    logger.error(f"CoinGecko error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"CoinGecko exception: {e}")
        
        # فال‌بک: استفاده از داده دمو
        demo = DEMO_PRICES.get(symbol, {"price": 100, "change": 0, "volume": 0})
        return {
            "symbol": symbol,
            "price": demo["price"],
            "change": demo["change"],
            "volume": demo["volume"],
            "source": "Demo",
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "demo": True
        }
    
    async def get_all_prices(self):
        """دریافت قیمت همه ارزها همزمان"""
        symbols = ["BTC", "ETH", "SOL", "BNB"]
        tasks = [self.get_price(s) for s in symbols]
        results = await asyncio.gather(*tasks)
        return {r["symbol"]: r for r in results}

# ========== تولید سیگنال ==========
def generate_signal(price, change):
    """تولید سیگنال بر اساس تغییر قیمت"""
    if change > 3:
        action = "STRONG_BUY"
        action_fa = "خرید قوی"
        confidence = 85
        stop_loss = round(price * 0.97, 2)
        take_profit = round(price * 1.05, 2)
        emoji = "🟢🟢"
    elif change > 1:
        action = "BUY"
        action_fa = "خرید"
        confidence = 65
        stop_loss = round(price * 0.98, 2)
        take_profit = round(price * 1.03, 2)
        emoji = "🟢"
    elif change < -3:
        action = "STRONG_SELL"
        action_fa = "فروش قوی"
        confidence = 85
        stop_loss = round(price * 1.03, 2)
        take_profit = round(price * 0.95, 2)
        emoji = "🔴🔴"
    elif change < -1:
        action = "SELL"
        action_fa = "فروش"
        confidence = 65
        stop_loss = round(price * 1.02, 2)
        take_profit = round(price * 0.97, 2)
        emoji = "🔴"
    else:
        action = "HOLD"
        action_fa = "نگهداری"
        confidence = 50
        stop_loss = 0
        take_profit = 0
        emoji = "⚪"
    
    # RSI تقریبی
    rsi = 50 + (change * 2.5)
    rsi = max(20, min(80, rsi))
    
    # سطوح حمایت و مقاومت
    if change > 0:
        support = round(price * 0.95, 2)
        resistance = round(price * 1.05, 2)
    else:
        support = round(price * 0.94, 2)
        resistance = round(price * 1.04, 2)
    
    return {
        "action": action,
        "action_fa": action_fa,
        "emoji": emoji,
        "confidence": confidence,
        "rsi": round(rsi, 1),
        "support": support,
        "resistance": resistance,
        "stop_loss": stop_loss,
        "take_profit": take_profit
    }

# ========== ربات تلگرام ==========
class SignalBot:
    def __init__(self):
        self.price_api = PriceAPI()
        self.application = None
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("🎯 سیگنال BTC", callback_data="signal_BTC")],
            [InlineKeyboardButton("🎯 سیگنال ETH", callback_data="signal_ETH")],
            [InlineKeyboardButton("🎯 سیگنال SOL", callback_data="signal_SOL")],
            [InlineKeyboardButton("🎯 سیگنال BNB", callback_data="signal_BNB")],
            [InlineKeyboardButton("📊 همه سیگنال‌ها", callback_data="all_signals")],
            [InlineKeyboardButton("💰 قیمت لحظه‌ای", callback_data="prices")],
            [InlineKeyboardButton("🛡️ مدیریت ریسک", callback_data="risk")],
            [InlineKeyboardButton("❓ راهنما", callback_data="help")],
        ]
        
        text = """
🔥 **ربات سیگنال‌گیر حرفه‌ای** 🔥

📊 **منبع داده:** CoinGecko (بدون تحریم)

🎯 **قابلیت‌ها:**
• سیگنال لحظه‌ای BTC, ETH, SOL, BNB
• تحلیل تغییرات قیمت 24 ساعته
• تعیین حد ضرر و حد سود
• سطوح حمایت و مقاومت

📌 **از دکمه‌های زیر استفاده کن 👇**
"""
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def signal_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
        msg = await update.callback_query.edit_message_text(f"🔄 در حال دریافت سیگنال {symbol}...")
        
        data = await self.price_api.get_price(symbol)
        signal = generate_signal(data['price'], data['change'])
        
        # نمایش منبع
        source_tag = " ⚠️ [دمو]" if data.get('demo') else ""
        
        text = f"🎯 **سیگنال {symbol}/USDT**{source_tag}\n\n"
        text += f"💰 **قیمت:** ${data['price']:,.0f}\n"
        text += f"📈 **تغییر 24h:** {data['change']:+.1f}%\n"
        text += f"📊 **حجم 24h:** ${data['volume']/1e9:.1f}B\n\n"
        
        text += f"{signal['emoji']} **سیگنال:** {signal['action_fa']}\n"
        text += f"📊 **اطمینان:** {signal['confidence']}%\n"
        text += f"📊 **RSI تقریبی:** {signal['rsi']}\n\n"
        
        text += f"🟢 **حمایت:** ${signal['support']:,.0f}\n"
        text += f"🔴 **مقاومت:** ${signal['resistance']:,.0f}\n\n"
        
        if signal['action'] in ["BUY", "STRONG_BUY", "SELL", "STRONG_SELL"]:
            text += f"🛡️ **حد ضرر پیشنهادی:** ${signal['stop_loss']:,.0f}\n"
            text += f"🎯 **حد سود پیشنهادی:** ${signal['take_profit']:,.0f}\n\n"
        
        text += f"📍 **منبع:** {data['source']}\n"
        text += f"⏰ **زمان:** {data['timestamp']}"
        
        if data.get('demo'):
            text += "\n\n💡 داده‌ها شبیه‌سازی شده‌اند (API در دسترس نبود)"
        
        keyboard = [[InlineKeyboardButton("🔄 بروزرسانی", callback_data=f"signal_{symbol}")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
        await msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def all_signals(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = await update.callback_query.edit_message_text("🔄 در حال دریافت سیگنال‌ها...")
        
        all_data = await self.price_api.get_all_prices()
        
        text = "📊 **سیگنال‌های لحظه‌ای بازار** 📊\n\n"
        demo_mode = False
        
        for symbol, data in all_data.items():
            signal = generate_signal(data['price'], data['change'])
            
            text += f"**{symbol}/USDT**\n"
            text += f"💰 ${data['price']:,.0f} | تغییر: {data['change']:+.1f}%\n"
            text += f"{signal['emoji']} {signal['action_fa']} (اطمینان: {signal['confidence']}%)\n\n"
            
            if data.get('demo'):
                demo_mode = True
        
        if demo_mode:
            text += "⚠️ **نکته:** برخی داده‌ها شبیه‌سازی شده‌اند\n"
        
        keyboard = [
            [InlineKeyboardButton("🔄 بروزرسانی", callback_data="all_signals")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
        ]
        await msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def prices_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = await update.callback_query.edit_message_text("🔄 دریافت قیمت‌ها...")
        
        all_data = await self.price_api.get_all_prices()
        
        text = "💰 **قیمت لحظه‌ای ارزها** 💰\n\n"
        demo_mode = False
        
        for symbol, data in all_data.items():
            emoji = "🟢" if data['change'] > 0 else "🔴" if data['change'] < 0 else "⚪"
            text += f"{emoji} **{symbol}/USDT**\n"
            text += f"   💵 قیمت: ${data['price']:,.0f}\n"
            text += f"   📈 تغییر: {data['change']:+.1f}%\n"
            text += f"   📊 حجم: ${data['volume']/1e9:.1f}B\n"
            text += f"   📍 منبع: {data['source']}\n\n"
            
            if data.get('demo'):
                demo_mode = True
        
        if demo_mode:
            text += "⚠️ حالت دمو - داده‌ها شبیه‌سازی شده‌اند\n"
        
        keyboard = [
            [InlineKeyboardButton("🔄 بروزرسانی", callback_data="prices")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
        ]
        await msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def risk_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = """
🛡️ **مدیریت ریسک حرفه‌ای** 🛡️

📊 **قوانین طلایی:**

1️⃣ **حداکثر ریسک:** ۲٪ سرمایه در هر معامله

2️⃣ **نسبت ریسک به ریوارد:** حداقل ۱:۲

3️⃣ **حد ضرر:** همیشه اجباری

4️⃣ **فرمول حجم معامله:**
   `حجم = (سرمایه × ۲٪) / (قیمت ورود - حد ضرر)`

5️⃣ **حداکثر معاملات همزمان:** ۳ عدد

---
📈 **نکات مهم:**
• فقط به سیگنال‌های با اطمینان >70% اعتماد کن
• همیشه حد ضرر را فعال کن
• در ضررهای متوالی، معامله را متوقف کن

⚠️ **هشدار:** هیچ سیگنالی ۱۰۰٪ دقیق نیست
"""
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def help_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = """
❓ **راهنمای ربات** ❓

📊 **انواع سیگنال‌ها:**

🟢🟢 **خرید قوی** (اطمینان >70%)
   مناسب برای ورود با حجم معمولی

🟢 **خرید** (اطمینان 55-70%)
   ورود با احتیاط

⚪ **نگهداری** (اطمینان 50%)
   صبر کن - بازار خنثی

🔴 **فروش** (اطمینان 55-70%)
   خروج تدریجی

🔴🔴 **فروش قوی** (اطمینان >70%)
   خروج فوری

---
📈 **فاکتورهای سیگنال:**
• تغییر قیمت 24 ساعته
• حجم معاملات
• RSI تقریبی

---
📍 **منبع داده:** CoinGecko (بدون تحریم)

⚠️ **هشدار:** فقط جنبه آموزشی - مسئولیت با شماست
"""
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        data = query.data
        
        if data == "back":
            await self.start(update, context)
        elif data.startswith("signal_"):
            symbol = data.split("_")[1]
            await self.signal_command(update, context, symbol)
        elif data == "all_signals":
            await self.all_signals(update, context)
        elif data == "prices":
            await self.prices_menu(update, context)
        elif data == "risk":
            await self.risk_menu(update, context)
        elif data == "help":
            await self.help_menu(update, context)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("لطفاً از دکمه‌های منو استفاده کن یا /start بزن")
    
    async def run(self):
        self.application = Application.builder().token(TOKEN).build()
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        logger.info("🚀 ربات سیگنال‌گیر با CoinGecko روشن شد...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        await asyncio.Event().wait()

async def main():
    bot = SignalBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
