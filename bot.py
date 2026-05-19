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

# ========== کلاس قیمت با نوبیتکس ==========
class PriceAPI:
    def __init__(self):
        self.cache = {}
    
    async def get_realtime_price(self, symbol="BTC"):
        """دریافت قیمت لحظه‌ای از نوبیتکس"""
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
                        # قیمت فروش یا خرید
                        price = stats.get("bestSell") or stats.get("bestBuy")
                        if price:
                            return {
                                "symbol": symbol,
                                "price": float(price),
                                "change": float(stats.get("change24h", 0)),
                                "high": float(stats.get("high24h", 0)) if stats.get("high24h") else float(price),
                                "low": float(stats.get("low24h", 0)) if stats.get("low24h") else float(price),
                                "volume": float(stats.get("volumeSrc", 0)),
                                "source": "Nobitex",
                                "timestamp": datetime.now().strftime("%H:%M:%S")
                            }
                else:
                    logger.error(f"Nobitex error: {response.status_code}")
        except Exception as e:
            logger.error(f"Price error {symbol}: {e}")
        
        # اگر نوبیتکس جواب نداد، از داده دمو استفاده کن
        return self.get_demo_price(symbol)
    
    def get_demo_price(self, symbol):
        """قیمت دمو (برای زمانی که API در دسترس نیست)"""
        demo_prices = {
            "BTC": {"price": 65000, "change": 2.5, "volume": 25000000000},
            "ETH": {"price": 3500, "change": 1.8, "volume": 15000000000},
            "SOL": {"price": 160, "change": 5.2, "volume": 5000000000},
            "BNB": {"price": 580, "change": -1.2, "volume": 3000000000},
        }
        data = demo_prices.get(symbol, {"price": 100, "change": 0, "volume": 0})
        return {
            "symbol": symbol,
            "price": data["price"],
            "change": data["change"],
            "high": data["price"] * 1.02,
            "low": data["price"] * 0.98,
            "volume": data["volume"],
            "source": "Demo",
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "demo": True
        }
    
    async def get_usdt_irt(self):
        """دریافت قیمت تتر به تومان"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    "https://api.nobitex.ir/market/stats",
                    json={"srcCurrency": "USDT", "dstCurrency": "IRT"}
                )
                if response.status_code == 200:
                    data = response.json()
                    stats = data.get("stats", {})
                    return float(stats.get("bestSell", 0)) or float(stats.get("bestBuy", 0))
        except:
            pass
        return 65000  # قیمت دمو

# ========== محاسبات سیگنال ==========
def generate_signal(price, change, volume):
    """تولید سیگنال بر اساس داده‌ها"""
    buy_score = 0
    sell_score = 0
    reasons = []
    
    # تغییر قیمت
    if change > 3:
        buy_score += 40
        reasons.append(f"🟢 رشد قوی: +{change:.1f}%")
    elif change > 1:
        buy_score += 25
        reasons.append(f"🟢 رشد ملایم: +{change:.1f}%")
    elif change > 0:
        buy_score += 10
        reasons.append(f"📈 رشد خفیف: +{change:.1f}%")
    elif change < -3:
        sell_score += 40
        reasons.append(f"🔴 ریزش قوی: {change:.1f}%")
    elif change < -1:
        sell_score += 25
        reasons.append(f"🔴 ریزش ملایم: {change:.1f}%")
    elif change < 0:
        sell_score += 10
        reasons.append(f"📉 ریزش خفیف: {change:.1f}%")
    else:
        reasons.append(f"⚪ تغییر خنثی: {change:+.1f}%")
    
    # حجم معاملات
    if volume > 10_000_000_000:
        if buy_score > sell_score:
            buy_score += 15
            reasons.append("🟢 حجم بالا تأیید صعود")
        elif sell_score > buy_score:
            sell_score += 15
            reasons.append("🔴 حجم بالا تأیید نزول")
    
    # RSI تقریبی
    rsi = 50 + (change * 2.5)
    rsi = max(20, min(80, rsi))
    
    if rsi < 35:
        buy_score += 15
        reasons.append(f"🟢 منطقه خرید (RSI: {rsi:.0f})")
    elif rsi > 65:
        sell_score += 15
        reasons.append(f"🔴 منطقه فروش (RSI: {rsi:.0f})")
    
    # تصمیم نهایی
    total_score = buy_score - sell_score
    
    if total_score >= 50:
        action = "STRONG_BUY"
        confidence = min(90, 70 + total_score // 3)
    elif total_score >= 25:
        action = "BUY"
        confidence = 60 + total_score // 3
    elif total_score <= -50:
        action = "STRONG_SELL"
        confidence = min(90, 70 + abs(total_score) // 3)
    elif total_score <= -25:
        action = "SELL"
        confidence = 60 + abs(total_score) // 3
    else:
        action = "HOLD"
        confidence = 50
    
    # حد ضرر و سود
    if action in ["BUY", "STRONG_BUY"]:
        stop_loss = round(price * 0.97, 2)
        take_profit_1 = round(price * 1.04, 2)
        take_profit_2 = round(price * 1.07, 2)
    elif action in ["SELL", "STRONG_SELL"]:
        stop_loss = round(price * 1.03, 2)
        take_profit_1 = round(price * 0.96, 2)
        take_profit_2 = round(price * 0.93, 2)
    else:
        stop_loss = 0
        take_profit_1 = 0
        take_profit_2 = 0
    
    # سطوح حمایت و مقاومت
    if change > 0:
        support = round(price * 0.96, 2)
        resistance = round(price * 1.04, 2)
    else:
        support = round(price * 0.94, 2)
        resistance = round(price * 1.02, 2)
    pivot = round((support + resistance) / 2, 2)
    
    return {
        "action": action,
        "confidence": confidence,
        "score": total_score,
        "rsi": rsi,
        "support": support,
        "resistance": resistance,
        "pivot": pivot,
        "stop_loss": stop_loss,
        "take_profit_1": take_profit_1,
        "take_profit_2": take_profit_2,
        "reasons": reasons[:4]
    }

# ========== ربات تلگرام ==========
class SignalBot:
    def __init__(self):
        self.price_api = PriceAPI()
        self.application = None
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("🎯 سیگنال BTC", callback_data="signal_btc")],
            [InlineKeyboardButton("🎯 سیگنال ETH", callback_data="signal_eth")],
            [InlineKeyboardButton("🎯 سیگنال SOL", callback_data="signal_sol")],
            [InlineKeyboardButton("🎯 سیگنال BNB", callback_data="signal_bnb")],
            [InlineKeyboardButton("📊 همه سیگنال‌ها", callback_data="all_signals")],
            [InlineKeyboardButton("💰 قیمت لحظه‌ای", callback_data="prices")],
            [InlineKeyboardButton("🇮🇷 قیمت تتر", callback_data="tether")],
            [InlineKeyboardButton("🛡️ مدیریت ریسک", callback_data="risk")],
            [InlineKeyboardButton("❓ راهنما", callback_data="help")],
        ]
        
        text = """
🔥 **ربات سیگنال‌گیر لحظه‌ای** 🔥

📊 **قابلیت‌ها:**
• سیگنال لحظه‌ای از نوبیتکس
• تحلیل تغییرات قیمت و حجم
• تعیین حد ضرر و حد سود
• قیمت تتر به تومان

🎯 **نحوه استفاده:**
از دکمه‌های زیر سیگنال مورد نظر را انتخاب کن

📌 **منبع داده:** Nobitex + Binance
"""
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def get_signal_response(self, symbol):
        data = await self.price_api.get_realtime_price(symbol)
        if data:
            signal = generate_signal(data['price'], data['change'], data['volume'])
            return data, signal
        return None, None
    
    async def signal_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
        await update.callback_query.edit_message_text(f"🔄 در حال دریافت سیگنال {symbol}...")
        
        data, signal = await self.get_signal_response(symbol)
        
        if not data:
            await update.callback_query.edit_message_text(
                f"❌ خطا در دریافت سیگنال {symbol}\n\n"
                f"لطفاً دوباره تلاش کن\n\n"
                f"💡 نکته: ربات از نوبیتکس استفاده می‌کند و برای اتصال به اینترنت نیاز ندارد"
            )
            return
        
        # نمایش منبع داده
        source_text = ""
        if data.get('demo'):
            source_text = "\n⚠️ حالت دمو (API در دسترس نیست)"
        
        # نمایش سیگنال
        if signal['action'] == "STRONG_BUY":
            action_text = "🟢🟢 خرید قوی 🟢🟢"
        elif signal['action'] == "BUY":
            action_text = "🟢 خرید 🟢"
        elif signal['action'] == "STRONG_SELL":
            action_text = "🔴🔴 فروش قوی 🔴🔴"
        elif signal['action'] == "SELL":
            action_text = "🔴 فروش 🔴"
        else:
            action_text = "⚪ نگهداری ⚪"
        
        text = f"🎯 **سیگنال {symbol}/USDT** 🎯{source_text}\n\n"
        text += f"💰 **قیمت:** ${data['price']:,.0f}\n"
        text += f"📈 **تغییر 24h:** {data['change']:+.1f}%\n"
        text += f"📊 **حجم 24h:** ${data['volume']/1e9:.2f}B\n"
        text += f"🎯 **سیگنال:** {action_text}\n"
        text += f"📊 **اطمینان:** {signal['confidence']}%\n\n"
        
        text += f"📊 **RSI تقریبی:** {signal['rsi']:.0f}\n\n"
        
        text += f"🟢 **حمایت:** ${signal['support']:,.0f}\n"
        text += f"🔴 **مقاومت:** ${signal['resistance']:,.0f}\n"
        text += f"🟡 **نقطه محوری:** ${signal['pivot']:,.0f}\n\n"
        
        if signal['action'] in ["BUY", "STRONG_BUY"]:
            text += f"🛡️ **حد ضرر:** ${signal['stop_loss']:,.0f}\n"
            text += f"🎯 **هدف اول:** ${signal['take_profit_1']:,.0f}\n"
            text += f"🎯 **هدف دوم:** ${signal['take_profit_2']:,.0f}\n\n"
        elif signal['action'] in ["SELL", "STRONG_SELL"]:
            text += f"🛡️ **حد ضرر:** ${signal['stop_loss']:,.0f}\n"
            text += f"🎯 **هدف اول:** ${signal['take_profit_1']:,.0f}\n"
            text += f"🎯 **هدف دوم:** ${signal['take_profit_2']:,.0f}\n\n"
        
        if signal['reasons']:
            text += f"📝 **دلایل سیگنال:**\n"
            for r in signal['reasons']:
                text += f"   {r}\n"
        
        text += f"\n⏰ **زمان:** {data['timestamp']}"
        text += f"\n📍 **منبع:** {data['source']}"
        
        keyboard = [[InlineKeyboardButton("🔄 بروزرسانی", callback_data=f"signal_{symbol.lower()}")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def all_signals(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.callback_query.edit_message_text("🔄 در حال دریافت سیگنال‌ها...")
        
        symbols = ["BTC", "ETH", "SOL", "BNB"]
        results = []
        
        for symbol in symbols:
            data = await self.price_api.get_realtime_price(symbol)
            if data:
                signal = generate_signal(data['price'], data['change'], data['volume'])
                results.append((symbol, data, signal))
        
        if not results:
            await update.callback_query.edit_message_text(
                "❌ خطا در دریافت سیگنال‌ها\n\n"
                "لطفاً دوباره تلاش کن\n\n"
                "💡 ربات از نوبیتکس استفاده می‌کند"
            )
            return
        
        text = "📊 **سیگنال‌های لحظه‌ای بازار** 📊\n\n"
        
        for symbol, data, signal in results:
            if signal['action'] == "STRONG_BUY":
                action_display = "🟢🟢 خرید قوی"
            elif signal['action'] == "BUY":
                action_display = "🟢 خرید"
            elif signal['action'] == "STRONG_SELL":
                action_display = "🔴🔴 فروش قوی"
            elif signal['action'] == "SELL":
                action_display = "🔴 فروش"
            else:
                action_display = "⚪ نگهداری"
            
            text += f"**{symbol}/USDT**\n"
            text += f"💰 ${data['price']:,.0f} | تغییر: {data['change']:+.1f}%\n"
            text += f"🎯 {action_display} ({signal['confidence']}%)\n\n"
        
        keyboard = [
            [InlineKeyboardButton("🔄 بروزرسانی", callback_data="all_signals")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
        ]
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def prices_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.callback_query.edit_message_text("🔄 دریافت قیمت‌ها...")
        
        symbols = ["BTC", "ETH", "SOL", "BNB"]
        text = "💰 **قیمت لحظه‌ای ارزها** 💰\n\n"
        demo_mode = False
        
        for symbol in symbols:
            data = await self.price_api.get_realtime_price(symbol)
            if data:
                emoji = "🟢" if data['change'] > 0 else "🔴" if data['change'] < 0 else "⚪"
                text += f"{emoji} **{symbol}/USDT**\n"
                text += f"   💵 قیمت: ${data['price']:,.0f}\n"
                text += f"   📈 تغییر: {data['change']:+.1f}%\n"
                text += f"   📊 حجم: ${data['volume']/1e9:.2f}B\n\n"
                if data.get('demo'):
                    demo_mode = True
            else:
                text += f"⚪ **{symbol}**: خطا در دریافت\n\n"
        
        if demo_mode:
            text += "\n⚠️ **حالت دمو فعال است** (API در دسترس نیست)\n"
            text += "💡 داده‌ها شبیه‌سازی شده هستند\n"
        
        keyboard = [
            [InlineKeyboardButton("🔄 بروزرسانی", callback_data="prices")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
        ]
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def tether_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.callback_query.edit_message_text("🔄 دریافت قیمت تتر...")
        
        usdt_irt = await self.price_api.get_usdt_irt()
        
        text = "🇮🇷 **قیمت تتر به تومان** 🇮🇷\n\n"
        
        if usdt_irt:
            text += f"💵 **USDT/IRT**: {usdt_irt:,.0f} تومان\n\n"
            text += "📊 **محاسبه قیمت ارزها به تومان:**\n"
            
            symbols = ["BTC", "ETH", "SOL", "BNB"]
            for symbol in symbols:
                data = await self.price_api.get_realtime_price(symbol)
                if data:
                    price_toman = data['price'] * usdt_irt
                    text += f"• {symbol}: {price_toman:,.0f} تومان\n"
        else:
            text += "❌ خطا در دریافت قیمت تتر\n\n"
            text += "💡 قیمت پیش‌فرض: 65,000 تومان\n"
        
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def risk_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = """
🛡️ **مدیریت ریسک** 🛡️

📊 **قوانین طلایی:**

1️⃣ حداکثر ریسک در هر معامله: **۲٪ سرمایه**

2️⃣ نسبت حد ضرر به حد سود: **حداقل ۱:۲**

3️⃣ همیشه از **حد ضرر** استفاده کن

4️⃣ **فرمول حجم معامله:**
   حجم = (سرمایه × ۲٪) / (قیمت ورود - حد ضرر)

5️⃣ حداکثر معاملات همزمان: **۳ عدد**

---
📈 **نکات مهم:**
• به سیگنال‌های با اطمینان >70% اعتماد کن
• در سیگنال‌های ضعیف (<55%) وارد نشو
• همیشه حد ضرر را فعال کن

⚠️ **هشدار:** هیچ سیگنالی ۱۰۰٪ دقیق نیست
"""
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def help_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = """
❓ **راهنمای ربات سیگنال‌گیر** ❓

📊 **انواع سیگنال‌ها:**

🟢🟢 **خرید قوی** (اطمینان >70%)
   مناسب برای ورود با حجم معمولی

🟢 **خرید** (اطمینان 55-70%)
   ورود با احتیاط و حجم کم

⚪ **نگهداری** (اطمینان 50%)
   بازار خنثی - صبر کن

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
💡 **نکات:**
• منبع داده: نوبیتکس (دلاری) + دمو
• در صورت عدم دسترسی به API، حالت دمو فعال می‌شود
• قیمت تتر به تومان نیز قابل مشاهده است

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
        elif data == "signal_btc":
            await self.signal_command(update, context, "BTC")
        elif data == "signal_eth":
            await self.signal_command(update, context, "ETH")
        elif data == "signal_sol":
            await self.signal_command(update, context, "SOL")
        elif data == "signal_bnb":
            await self.signal_command(update, context, "BNB")
        elif data == "all_signals":
            await self.all_signals(update, context)
        elif data == "prices":
            await self.prices_menu(update, context)
        elif data == "tether":
            await self.tether_menu(update, context)
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
        
        logger.info("🚀 ربات سیگنال‌گیر لحظه‌ای روشن شد...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        await asyncio.Event().wait()

async def main():
    bot = SignalBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
