import os
import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import httpx
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ========== کلاس قیمت ==========
class PriceAPI:
    def __init__(self):
        self.cache = {}
    
    async def get_realtime_price(self, symbol="BTC"):
        """دریافت قیمت لحظه‌ای از بایننس"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}USDT")
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "symbol": symbol,
                        "price": float(data['lastPrice']),
                        "change": float(data['priceChangePercent']),
                        "high": float(data['highPrice']),
                        "low": float(data['lowPrice']),
                        "volume": float(data['quoteVolume']),
                        "source": "Binance",
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    }
        except Exception as e:
            logger.error(f"Price error {symbol}: {e}")
        return None
    
    async def get_multiple_prices(self, symbols):
        tasks = [self.get_realtime_price(s) for s in symbols]
        results = await asyncio.gather(*tasks)
        return {r['symbol']: r for r in results if r}

# ========== محاسبات ساده ==========
def calculate_rsi_from_change(change):
    """محاسبه RSI تقریبی از روی تغییر قیمت"""
    rsi = 50 + (change * 3)
    return max(20, min(80, rsi))

def calculate_support_resistance(price, change):
    """محاسبه سطوح حمایت و مقاومت"""
    if change > 0:
        support = round(price * 0.97, 2)
        resistance = round(price * 1.05, 2)
    else:
        support = round(price * 0.95, 2)
        resistance = round(price * 1.03, 2)
    pivot = round((support + resistance) / 2, 2)
    return support, resistance, pivot

def generate_signal(price, change, volume):
    """تولید سیگنال بر اساس داده‌های واقعی"""
    buy_score = 0
    sell_score = 0
    reasons = []
    
    # 1. تغییر قیمت
    if change > 3:
        buy_score += 35
        reasons.append(f"🟢 رشد قوی: +{change:.1f}%")
    elif change > 1:
        buy_score += 20
        reasons.append(f"🟢 رشد ملایم: +{change:.1f}%")
    elif change < -3:
        sell_score += 35
        reasons.append(f"🔴 ریزش قوی: {change:.1f}%")
    elif change < -1:
        sell_score += 20
        reasons.append(f"🔴 ریزش ملایم: {change:.1f}%")
    else:
        reasons.append(f"⚪ تغییر خنثی: {change:+.1f}%")
    
    # 2. حجم معاملات
    if volume > 2_000_000_000:
        if buy_score > sell_score:
            buy_score += 15
            reasons.append("🟢 حجم بالا تأیید صعود")
        elif sell_score > buy_score:
            sell_score += 15
            reasons.append("🔴 حجم بالا تأیید نزول")
    
    # 3. RSI تقریبی
    rsi = calculate_rsi_from_change(change)
    if rsi < 35:
        buy_score += 15
        reasons.append(f"🟢 منطقه خرید (RSI: {rsi:.0f})")
    elif rsi > 65:
        sell_score += 15
        reasons.append(f"🔴 منطقه فروش (RSI: {rsi:.0f})")
    
    # تصمیم نهایی
    total_score = buy_score - sell_score
    
    if total_score >= 45:
        action = "STRONG_BUY"
        confidence = min(90, 65 + total_score // 2)
    elif total_score >= 20:
        action = "BUY"
        confidence = 55 + total_score // 2
    elif total_score <= -45:
        action = "STRONG_SELL"
        confidence = min(90, 65 + abs(total_score) // 2)
    elif total_score <= -20:
        action = "SELL"
        confidence = 55 + abs(total_score) // 2
    else:
        action = "HOLD"
        confidence = 50
    
    # حد ضرر و سود
    if action in ["BUY", "STRONG_BUY"]:
        stop_loss = round(price * 0.97, 2)
        take_profit = round(price * 1.05, 2)
    elif action in ["SELL", "STRONG_SELL"]:
        stop_loss = round(price * 1.03, 2)
        take_profit = round(price * 0.95, 2)
    else:
        stop_loss = 0
        take_profit = 0
    
    support, resistance, pivot = calculate_support_resistance(price, change)
    
    return {
        "action": action,
        "confidence": confidence,
        "score": total_score,
        "rsi": rsi,
        "support": support,
        "resistance": resistance,
        "pivot": pivot,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
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
            [InlineKeyboardButton("🛡️ مدیریت ریسک", callback_data="risk")],
            [InlineKeyboardButton("❓ راهنما", callback_data="help")],
        ]
        
        text = """
🔥 **ربات سیگنال‌گیر لحظه‌ای** 🔥

📊 **قابلیت‌ها:**
• سیگنال لحظه‌ای از بایننس
• تحلیل تغییرات قیمت و حجم
• تعیین حد ضرر و حد سود
• دقت بالا با چندین فاکتور

🎯 **نحوه استفاده:**
از دکمه‌های زیر سیگنال مورد نظر را انتخاب کن

📌 **منبع داده:** Binance (لحظه‌ای)
"""
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def get_signal_response(self, symbol):
        """دریافت سیگنال برای یک نماد"""
        data = await self.price_api.get_realtime_price(symbol)
        if not data:
            return None, None
        
        signal = generate_signal(data['price'], data['change'], data['volume'])
        return data, signal
    
    async def signal_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
        await update.callback_query.edit_message_text(f"🔄 در حال دریافت سیگنال {symbol}...")
        
        data, signal = await self.get_signal_response(symbol)
        
        if not data or not signal:
            await update.callback_query.edit_message_text(f"❌ خطا در دریافت سیگنال {symbol}\n\nلطفاً دوباره تلاش کن")
            return
        
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
        
        text = f"🎯 **سیگنال {symbol}/USDT** 🎯\n\n"
        text += f"💰 **قیمت:** ${data['price']:,.0f}\n"
        text += f"📈 **تغییر 24h:** {data['change']:+.1f}%\n"
        text += f"📊 **حجم:** ${data['volume']/1e9:.1f}B\n"
        text += f"🎯 **سیگنال:** {action_text}\n"
        text += f"📊 **اطمینان:** {signal['confidence']}%\n\n"
        
        text += f"📊 **RSI تقریبی:** {signal['rsi']:.0f}\n\n"
        
        text += f"🟢 **حمایت:** ${signal['support']:,.0f}\n"
        text += f"🔴 **مقاومت:** ${signal['resistance']:,.0f}\n"
        text += f"🟡 **نقطه محوری:** ${signal['pivot']:,.0f}\n\n"
        
        if signal['action'] in ["BUY", "STRONG_BUY", "SELL", "STRONG_SELL"]:
            text += f"🛡️ **حد ضرر:** ${signal['stop_loss']:,.0f}\n"
            text += f"🎯 **حد سود:** ${signal['take_profit']:,.0f}\n\n"
        
        if signal['reasons']:
            text += f"📝 **دلایل:**\n"
            for r in signal['reasons']:
                text += f"   {r}\n"
        
        text += f"\n⏰ **زمان:** {data['timestamp']}"
        
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
            await update.callback_query.edit_message_text("❌ خطا در دریافت سیگنال‌ها\n\nلطفاً دوباره تلاش کن")
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
        
        for symbol in symbols:
            data = await self.price_api.get_realtime_price(symbol)
            if data:
                emoji = "🟢" if data['change'] > 0 else "🔴" if data['change'] < 0 else "⚪"
                text += f"{emoji} **{symbol}/USDT**\n"
                text += f"   قیمت: ${data['price']:,.0f}\n"
                text += f"   تغییر: {data['change']:+.1f}%\n"
                text += f"   حجم: ${data['volume']/1e9:.1f}B\n\n"
            else:
                text += f"⚪ **{symbol}**: خطا در دریافت\n\n"
        
        keyboard = [
            [InlineKeyboardButton("🔄 بروزرسانی", callback_data="prices")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
        ]
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
• منبع داده: Binance (لحظه‌ای)
• سیگنال‌ها با هر بار درخواست بروز می‌شوند
• برای بهترین نتیجه، سیگنال‌های قوی را انتخاب کن

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
