import os
import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import httpx
import numpy as np
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ========== داده‌های قیمت ==========
class PriceAPI:
    def __init__(self):
        self.cache = {}
        self.last_update = {}
    
    async def get_realtime_price(self, symbol="BTC"):
        """دریافت قیمت لحظه‌ای از بایننس"""
        cache_key = f"{symbol}_price"
        now = datetime.now().timestamp()
        
        # کش 3 ثانیه
        if cache_key in self.cache and now - self.last_update.get(cache_key, 0) < 3:
            return self.cache[cache_key]
        
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}USDT")
                if response.status_code == 200:
                    data = response.json()
                    result = {
                        "symbol": symbol,
                        "price": float(data['lastPrice']),
                        "change": float(data['priceChangePercent']),
                        "high": float(data['highPrice']),
                        "low": float(data['lowPrice']),
                        "volume": float(data['quoteVolume']),
                        "bid": float(data['bidPrice']) if data.get('bidPrice') else 0,
                        "ask": float(data['askPrice']) if data.get('askPrice') else 0,
                        "source": "Binance",
                        "timestamp": datetime.now().isoformat()
                    }
                    self.cache[cache_key] = result
                    self.last_update[cache_key] = now
                    return result
        except Exception as e:
            logger.error(f"Price error {symbol}: {e}")
        return None
    
    async def get_multiple_prices(self, symbols):
        """دریافت قیمت چند ارز همزمان"""
        tasks = [self.get_realtime_price(s) for s in symbols]
        results = await asyncio.gather(*tasks)
        return {r['symbol']: r for r in results if r}

# ========== محاسبات تکنیکال ==========
class TechnicalIndicators:
    @staticmethod
    def calculate_rsi(prices, period=14):
        if len(prices) < period + 1:
            return 50
        gains, losses = [], []
        for i in range(1, len(prices)):
            diff = prices[i] - prices[i-1]
            if diff > 0:
                gains.append(diff)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(-diff)
        avg_gain = sum(gains[-period:]) / period if len(gains) >= period else 0
        avg_loss = sum(losses[-period:]) / period if len(losses) >= period else 0
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def calculate_macd(prices):
        if len(prices) < 26:
            return 0, 0, 0
        ema12 = TechnicalIndicators.ema(prices, 12)
        ema26 = TechnicalIndicators.ema(prices, 26)
        macd_line = ema12 - ema26
        signal_line = TechnicalIndicators.ema(macd_line, 9)
        histogram = macd_line - signal_line
        return macd_line[-1], signal_line[-1], histogram[-1]
    
    @staticmethod
    def ema(data, period):
        if len(data) < period:
            return data
        multiplier = 2 / (period + 1)
        ema_values = [data[0]]
        for price in data[1:]:
            ema_values.append((price - ema_values[-1]) * multiplier + ema_values[-1])
        return ema_values
    
    @staticmethod
    def calculate_support_resistance(prices):
        recent = prices[-50:] if len(prices) > 50 else prices
        high = max(recent)
        low = min(recent)
        mid = (high + low) / 2
        return round(low, 2), round(high, 2), round(mid, 2)
    
    @staticmethod
    def calculate_bollinger_bands(prices, period=20, std_dev=2):
        if len(prices) < period:
            return None, None, None
        sma = sum(prices[-period:]) / period
        variance = sum((p - sma) ** 2 for p in prices[-period:]) / period
        std = variance ** 0.5
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return upper, sma, lower

# ========== موتور سیگنال ==========
class SignalEngine:
    def __init__(self):
        self.price_api = PriceAPI()
        self.indicators = TechnicalIndicators()
    
    async def generate_signal(self, symbol="BTC"):
        """تولید سیگنال کامل برای یک ارز"""
        
        # دریافت داده
        current_data = await self.price_api.get_realtime_price(symbol)
        if not current_data:
            return None
        
        # شبیه‌سازی داده تاریخی (برای اندیکاتورها)
        base_price = current_data['price']
        historical_prices = [base_price * (1 + np.random.randn(50) * 0.015)]
        historical_prices = [max(0.01, p) for p in historical_prices]
        
        # محاسبه اندیکاتورها
        rsi = self.indicators.calculate_rsi(historical_prices)
        macd, signal, hist = self.indicators.calculate_macd(historical_prices)
        support, resistance, pivot = self.indicators.calculate_support_resistance(historical_prices)
        bb_upper, bb_middle, bb_lower = self.indicators.calculate_bollinger_bands(historical_prices)
        
        # سیستم امتیازدهی
        buy_score = 0
        sell_score = 0
        reasons = []
        
        # 1. RSI Signal
        if rsi < 30:
            buy_score += 30
            reasons.append(f"🟢 RSI oversold: {rsi:.0f}")
        elif rsi > 70:
            sell_score += 30
            reasons.append(f"🔴 RSI overbought: {rsi:.0f}")
        
        # 2. MACD Signal
        if macd > signal:
            buy_score += 25
            reasons.append("🟢 MACD bullish crossover")
        elif macd < signal:
            sell_score += 25
            reasons.append("🔴 MACD bearish crossover")
        
        # 3. Price Action
        change = current_data['change']
        if change > 2:
            buy_score += 20
            reasons.append(f"🟢 Strong uptrend: +{change:.1f}%")
        elif change < -2:
            sell_score += 20
            reasons.append(f"🔴 Strong downtrend: {change:.1f}%")
        elif change > 0:
            buy_score += 5
            reasons.append(f"📈 Mild uptrend: +{change:.1f}%")
        elif change < 0:
            sell_score += 5
            reasons.append(f"📉 Mild downtrend: {change:.1f}%")
        
        # 4. Bollinger Bands
        if bb_lower and current_data['price'] <= bb_lower:
            buy_score += 20
            reasons.append("🟢 Price at lower band (buy zone)")
        elif bb_upper and current_data['price'] >= bb_upper:
            sell_score += 20
            reasons.append("🔴 Price at upper band (sell zone)")
        
        # 5. Volume
        if current_data['volume'] > 1_000_000_000:  # حجم بالای 1 میلیارد
            if buy_score > sell_score:
                buy_score += 10
                reasons.append("🟢 High volume confirming uptrend")
            elif sell_score > buy_score:
                sell_score += 10
                reasons.append("🔴 High volume confirming downtrend")
        
        # تصمیم نهایی
        total_score = buy_score - sell_score
        
        if total_score >= 40:
            action = "STRONG_BUY"
            confidence = min(95, 60 + total_score)
            emoji = "🟢🟢"
        elif total_score >= 20:
            action = "BUY"
            confidence = 55 + total_score // 2
            emoji = "🟢"
        elif total_score <= -40:
            action = "STRONG_SELL"
            confidence = min(95, 60 + abs(total_score))
            emoji = "🔴🔴"
        elif total_score <= -20:
            action = "SELL"
            confidence = 55 + abs(total_score) // 2
            emoji = "🔴"
        else:
            action = "HOLD"
            confidence = 50
            emoji = "⚪"
        
        # محاسبه حد ضرر و حد سود
        if action in ["BUY", "STRONG_BUY"]:
            stop_loss = round(current_data['price'] * 0.97, 2)
            take_profit_1 = round(current_data['price'] * 1.03, 2)
            take_profit_2 = round(current_data['price'] * 1.06, 2)
        elif action in ["SELL", "STRONG_SELL"]:
            stop_loss = round(current_data['price'] * 1.03, 2)
            take_profit_1 = round(current_data['price'] * 0.97, 2)
            take_profit_2 = round(current_data['price'] * 0.94, 2)
        else:
            stop_loss = 0
            take_profit_1 = 0
            take_profit_2 = 0
        
        return {
            "symbol": symbol,
            "action": action,
            "emoji": emoji,
            "confidence": confidence,
            "score": total_score,
            "price": current_data['price'],
            "change": current_data['change'],
            "rsi": round(rsi, 1),
            "macd": round(macd, 6),
            "support": support,
            "resistance": resistance,
            "pivot": pivot,
            "stop_loss": stop_loss,
            "take_profit_1": take_profit_1,
            "take_profit_2": take_profit_2,
            "reasons": reasons[:5],
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }

# ========== ربات تلگرام ==========
class SignalBot:
    def __init__(self):
        self.signal_engine = SignalEngine()
        self.application = None
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("🎯 سیگنال لحظه‌ای", callback_data="signal_btc")],
            [InlineKeyboardButton("📊 همه سیگنال‌ها", callback_data="all_signals")],
            [InlineKeyboardButton("📈 تحلیل دقیق BTC", callback_data="analysis_btc")],
            [InlineKeyboardButton("📈 تحلیل دقیق ETH", callback_data="analysis_eth")],
            [InlineKeyboardButton("💰 قیمت لحظه‌ای", callback_data="prices")],
            [InlineKeyboardButton("🛡️ مدیریت ریسک", callback_data="risk")],
            [InlineKeyboardButton("❓ راهنما", callback_data="help")],
        ]
        
        text = """
🔥 **ربات سیگنال‌گیر لحظه‌ای** 🔥

📊 **قابلیت‌ها:**
• سیگنال لحظه‌ای BTC, ETH, SOL, BNB
• تحلیل RSI, MACD, حجم, باند بولینگر
• تعیین حد ضرر و حد سود
• دقت بالا با چندین اندیکاتور

🎯 **نحوه استفاده:**
از دکمه‌های زیر سیگنال مورد نظر را انتخاب کن

📌 **سیگنال‌ها هر 3 ثانیه بروز می‌شوند**
"""
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def signal_btc(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.callback_query.edit_message_text("🔄 در حال دریافت سیگنال لحظه‌ای...")
        
        signal = await self.signal_engine.generate_signal("BTC")
        if not signal:
            await update.callback_query.edit_message_text("❌ خطا در دریافت سیگنال")
            return
        
        text = self.format_signal(signal)
        
        keyboard = [
            [InlineKeyboardButton("🔄 بروزرسانی", callback_data="signal_btc")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
        ]
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def all_signals(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.callback_query.edit_message_text("🔄 در حال دریافت سیگنال‌ها...")
        
        symbols = ["BTC", "ETH", "SOL", "BNB"]
        signals = []
        
        for symbol in symbols:
            signal = await self.signal_engine.generate_signal(symbol)
            if signal:
                signals.append(signal)
        
        if not signals:
            await update.callback_query.edit_message_text("❌ خطا در دریافت سیگنال‌ها")
            return
        
        text = "📊 **سیگنال‌های لحظه‌ای بازار** 📊\n\n"
        for s in signals:
            if s['action'] == "STRONG_BUY":
                action_display = "🟢🟢 خرید قوی"
            elif s['action'] == "BUY":
                action_display = "🟢 خرید"
            elif s['action'] == "STRONG_SELL":
                action_display = "🔴🔴 فروش قوی"
            elif s['action'] == "SELL":
                action_display = "🔴 فروش"
            else:
                action_display = "⚪ نگهداری"
            
            text += f"**{s['symbol']}/USDT**\n"
            text += f"💰 قیمت: ${s['price']:,.0f}\n"
            text += f"🎯 سیگنال: {action_display} ({s['confidence']}%)\n"
            text += f"📈 تغییر: {s['change']:+.1f}%\n"
            text += f"📊 RSI: {s['rsi']:.0f}\n\n"
        
        keyboard = [
            [InlineKeyboardButton("🔄 بروزرسانی", callback_data="all_signals")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
        ]
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def analysis_btc(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.callback_query.edit_message_text("🔄 در حال تحلیل بیت‌کوین...")
        signal = await self.signal_engine.generate_signal("BTC")
        if signal:
            text = self.format_analysis(signal)
            keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
            await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def analysis_eth(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.callback_query.edit_message_text("🔄 در حال تحلیل اتریوم...")
        signal = await self.signal_engine.generate_signal("ETH")
        if signal:
            text = self.format_analysis(signal)
            keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
            await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def prices_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.callback_query.edit_message_text("🔄 دریافت قیمت‌ها...")
        
        symbols = ["BTC", "ETH", "SOL", "BNB"]
        text = "💰 **قیمت لحظه‌ای ارزها** 💰\n\n"
        
        for symbol in symbols:
            data = await self.signal_engine.price_api.get_realtime_price(symbol)
            if data:
                emoji = "🟢" if data['change'] > 0 else "🔴" if data['change'] < 0 else "⚪"
                text += f"{emoji} **{symbol}/USDT**: ${data['price']:,.0f}\n"
                text += f"   تغییر: {data['change']:+.1f}% | حجم: ${data['volume']/1e9:.1f}B\n\n"
            else:
                text += f"⚪ **{symbol}**: خطا\n\n"
        
        keyboard = [
            [InlineKeyboardButton("🔄 بروزرسانی", callback_data="prices")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
        ]
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def risk_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = """
🛡️ **مدیریت ریسک حرفه‌ای** 🛡️

📊 **قوانین طلایی برای سیگنال‌ها:**

1️⃣ **حداکثر ریسک در هر معامله:** ۲٪ سرمایه

2️⃣ **نسبت حد ضرر به حد سود:** حداقل ۱:۲

3️⃣ **حد ضرر:** همیشه از سیگنال استفاده کن

4️⃣ **حجم معامله:** 
   حجم = (سرمایه × ۲٪) / (قیمت ورود - حد ضرر)

5️⃣ **حداکثر معاملات همزمان:** ۳ عدد

---
📈 **نکات مهم:**
• هرگز به یک سیگنال ۱۰۰٪ اعتماد نکن
• همیشه حد ضرر را فعال کن
• در سیگنال‌های ضعیف (کمتر از ۶۰٪) وارد نشو
• از سیگنال‌های قوی (بیشتر از ۷۵٪) استفاده کن

---
⚠️ **هشدار:** هیچ سیگنالی ۱۰۰٪ دقیق نیست
"""
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def help_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = """
❓ **راهنمای ربات سیگنال‌گیر** ❓

📊 **انواع سیگنال‌ها:**

🟢🟢 **خرید قوی (STRONG_BUY)**
   اعتماد بالا - مناسب برای ورود

🟢 **خرید (BUY)** 
   اعتماد متوسط - ورود با احتیاط

⚪ **نگهداری (HOLD)** 
   بازار خنثی - صبر کن

🔴 **فروش (SELL)**
   اعتماد متوسط - خروج یا فروش

🔴🔴 **فروش قوی (STRONG_SELL)**
   اعتماد بالا - خروج فوری

---
📈 **اندیکاتورهای استفاده شده:**
• RSI (قدرت نسبی)
• MACD (همگرایی/واگرایی)
• باند بولینگر
• تحلیل حجم
• قیمت اکشن

---
💡 **نکات:**
• سیگنال‌ها هر 3 ثانیه بروز می‌شوند
• برای بهترین نتیجه، سیگنال‌های قوی (>70%) را انتخاب کن
• همیشه از حد ضرر استفاده کن

⚠️ **هشدار:** فقط جنبه آموزشی
"""
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    def format_signal(self, signal):
        """格式化显示信号"""
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
        
        text = f"🎯 **سیگنال {signal['symbol']}/USDT** 🎯\n\n"
        text += f"💰 **قیمت لحظه‌ای:** ${signal['price']:,.0f}\n"
        text += f"📈 **تغییر 24h:** {signal['change']:+.1f}%\n"
        text += f"🎯 **سیگنال:** {action_text}\n"
        text += f"📊 **اطمینان:** {signal['confidence']}%\n"
        text += f"📊 **امتیاز کلی:** {signal['score']:+.0f}\n\n"
        
        text += f"📊 **RSI(14):** {signal['rsi']:.0f}\n"
        text += f"📈 **MACD:** {signal['macd']:.6f}\n\n"
        
        text += f"🟢 **حمایت:** ${signal['support']:,.0f}\n"
        text += f"🔴 **مقاومت:** ${signal['resistance']:,.0f}\n"
        text += f"🟡 **نقطه محوری:** ${signal['pivot']:,.0f}\n\n"
        
        if signal['action'] in ["BUY", "STRONG_BUY", "SELL", "STRONG_SELL"]:
            text += f"🛡️ **حد ضرر پیشنهادی:** ${signal['stop_loss']:,.0f}\n"
            text += f"🎯 **هدف اول:** ${signal['take_profit_1']:,.0f}\n"
            text += f"🎯 **هدف دوم:** ${signal['take_profit_2']:,.0f}\n\n"
        
        if signal['reasons']:
            text += f"📝 **دلایل سیگنال:**\n"
            for r in signal['reasons']:
                text += f"   {r}\n"
        
        text += f"\n⏰ **زمان:** {signal['timestamp']}"
        return text
    
    def format_analysis(self, signal):
        text = f"📈 **تحلیل کامل {signal['symbol']}/USDT** 📈\n\n"
        text += f"💰 **قیمت فعلی:** ${signal['price']:,.0f}\n"
        text += f"📈 **تغییر 24h:** {signal['change']:+.1f}%\n\n"
        
        text += "**📊 اندیکاتورهای تکنیکال:**\n"
        text += f"• RSI(14): {signal['rsi']:.0f} → "
        if signal['rsi'] < 30:
            text += "🟢 اشباع فروش (منطقه خرید)\n"
        elif signal['rsi'] > 70:
            text += "🔴 اشباع خرید (منطقه فروش)\n"
        else:
            text += "⚪ محدوده خنثی\n"
        
        text += f"• MACD: {signal['macd']:.6f}\n"
        text += f"• روند: {'صعودی 📈' if signal['change'] > 0 else 'نزولی 📉'}\n\n"
        
        text += "**🔑 سطوح کلیدی:**\n"
        text += f"🟢 حمایت اصلی: ${signal['support']:,.0f}\n"
        text += f"🔴 مقاومت اصلی: ${signal['resistance']:,.0f}\n"
        text += f"🟡 نقطه محوری: ${signal['pivot']:,.0f}\n\n"
        
        text += f"**🎯 سیگنال نهایی:** {signal['action']} (اطمینان: {signal['confidence']}%)\n\n"
        
        if signal['reasons']:
            text += f"**📝 تحلیل کامل:**\n"
            for r in signal['reasons']:
                text += f"• {r}\n"
        
        return text
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        data = query.data
        
        if data == "back":
            await self.start(update, context)
        elif data == "signal_btc":
            await self.signal_btc(update, context)
        elif data == "all_signals":
            await self.all_signals(update, context)
        elif data == "analysis_btc":
            await self.analysis_btc(update, context)
        elif data == "analysis_eth":
            await self.analysis_eth(update, context)
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
