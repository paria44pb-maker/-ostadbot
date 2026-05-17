import os
import json
import logging
import random
import httpx
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MEMORY_FILE = "memory.json"
PORTFOLIO_FILE = "portfolio.json"
SIGNALS_FILE = "signals.json"

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

# ========== قیمت‌های شبیه‌سازی شده (فیک) ==========
fake_prices = {
    "BTC": {"usdt": 67234, "change": 2.3, "high": 68500, "low": 66500, "volume": 28.5, "support": 66000, "resistance": 69000},
    "ETH": {"usdt": 3456, "change": 1.8, "high": 3520, "low": 3400, "volume": 15.2, "support": 3380, "resistance": 3550},
    "SOL": {"usdt": 156.7, "change": 5.2, "high": 162, "low": 148, "volume": 8.3, "support": 145, "resistance": 165},
    "BNB": {"usdt": 582, "change": -1.2, "high": 595, "low": 575, "volume": 3.1, "support": 570, "resistance": 600},
    "XRP": {"usdt": 0.52, "change": 0.5, "high": 0.54, "low": 0.51, "volume": 2.8, "support": 0.50, "resistance": 0.55},
    "DOGE": {"usdt": 0.125, "change": 3.1, "high": 0.13, "low": 0.121, "volume": 1.9, "support": 0.12, "resistance": 0.135},
    "ADA": {"usdt": 0.35, "change": -0.8, "high": 0.36, "low": 0.34, "volume": 1.5, "support": 0.33, "resistance": 0.37},
    "AVAX": {"usdt": 34.2, "change": 4.5, "high": 35.5, "low": 33, "volume": 0.7, "support": 32, "resistance": 36},
    "MATIC": {"usdt": 0.72, "change": -2.1, "high": 0.74, "low": 0.71, "volume": 1.1, "support": 0.70, "resistance": 0.75},
}

# ========== شخصیت‌ها ==========
personalities = {
    "تریدر حرفه‌ای": {"emoji": "📊", "prompt": "تو یک تریدر حرفه‌ای هستی. با تحلیل تکنیکال و مدیریت ریسک پاسخ بده.", "color": "🔥"},
    "تحلیلگر بازار": {"emoji": "📈", "prompt": "تو یک تحلیلگر بازار هستی. با داده‌ها و آمار دقیق صحبت کن.", "color": "📊"},
    "مدیر ریسک": {"emoji": "🛡️", "prompt": "تو یک مدیر ریسک هستی. همیشه روی حد ضرر و مدیریت سرمایه تاکید کن.", "color": "⚖️"},
    "نهنگ بازار": {"emoji": "🐋", "prompt": "تو مثل یک نهنگ بازار فکر کن. حرکت‌های بزرگ رو پیش‌بینی کن.", "color": "💎"},
    "معلم ترید": {"emoji": "📚", "prompt": "تو یک معلم ترید هستی. قدم به قدم آموزش بده.", "color": "✏️"},
    "رسمی": {"emoji": "👔", "prompt": "تو یک دستیار رسمی و حرفه‌ای هستی.", "color": "🔵"},
    "شوخ‌طبع": {"emoji": "😄", "prompt": "تو یک دستیار شوخ و بامزه هستی.", "color": "🟡"},
    "علمی": {"emoji": "🔬", "prompt": "تو یک دانشمند و محقق هستی.", "color": "🧪"},
    "شاعرانه": {"emoji": "🎭", "prompt": "تو یک شاعر و نویسنده هستی.", "color": "🌸"},
}

# ========== ASCII Art ==========
ascii_arts = {
    "chart": """
    📈 BTC/USDT
    $67,234 ▲ +2.3%
    ━━━━━━━━━━━━━━━
    ████████░░░░ 62%
    RSI: 54 | MACD: ↗️
    """,
    "candle": """
    🕯️ کندل هفتگی
    ▲ High: $69,000
    ━━━━━━━━━
    ██████████
    ██████████
    ━━━━━━━━━
    ▼ Low: $66,000
    """,
    "signal_buy": "🟢 سیگنال خرید - قدرت بالا",
    "signal_sell": "🔴 سیگنال فروش - قدرت بالا",
    "signal_hold": "⚪ سیگنال نگهداری - صبر کن",
}

# ========== محاسبات تکنیکال ==========
def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50
    gains = []
    losses = []
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

def generate_signal(symbol, data):
    """تولید سیگنال معاملاتی بر اساس داده‌ها"""
    change = data["change"]
    price = data["usdt"]
    support = data["support"]
    resistance = data["resistance"]
    
    # محاسبه فاصله تا حمایت و مقاومت
    dist_to_support = (price - support) / support * 100
    dist_to_resistance = (resistance - price) / price * 100
    
    signal = {
        "action": "HOLD",
        "strength": 0,
        "entry": price,
        "stop_loss": 0,
        "take_profit": 0,
        "reason": ""
    }
    
    # منطق سیگنال
    if change > 3 and dist_to_resistance > 5:
        signal["action"] = "BUY"
        signal["strength"] = min(85, 50 + change * 5)
        signal["stop_loss"] = round(price * 0.97, 2)
        signal["take_profit"] = round(price * 1.08, 2)
        signal["reason"] = f"روند صعودی قوی + {change}% رشد"
    elif change < -3 and dist_to_support > 5:
        signal["action"] = "SELL"
        signal["strength"] = min(85, 50 + abs(change) * 5)
        signal["stop_loss"] = round(price * 1.03, 2)
        signal["take_profit"] = round(price * 0.92, 2)
        signal["reason"] = f"روند نزولی قوی + {abs(change)}% افت"
    elif change > 1 and dist_to_resistance > 3:
        signal["action"] = "BUY"
        signal["strength"] = 65
        signal["stop_loss"] = round(price * 0.98, 2)
        signal["take_profit"] = round(price * 1.05, 2)
        signal["reason"] = "روند صعودی ملایم"
    elif change < -1 and dist_to_support > 3:
        signal["action"] = "SELL"
        signal["strength"] = 65
        signal["stop_loss"] = round(price * 1.02, 2)
        signal["take_profit"] = round(price * 0.95, 2)
        signal["reason"] = "روند نزولی ملایم"
    else:
        signal["action"] = "HOLD"
        signal["strength"] = 50
        signal["reason"] = "بازار در حالت خنثی - منتظر تایید روند"
    
    return signal

# ========== منوی اصلی ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    personality = context.user_data.get("personality", "تریدر حرفه‌ای")
    keyboard = [
        [InlineKeyboardButton("📊 قیمت لحظه‌ای", callback_data="prices")],
        [InlineKeyboardButton("🎯 سیگنال معاملاتی", callback_data="signals")],
        [InlineKeyboardButton("📈 تحلیل تکنیکال", callback_data="technical")],
        [InlineKeyboardButton("🧠 تحلیل با AI", callback_data="ai_analysis")],
        [InlineKeyboardButton("💰 مدیریت پرتفوی", callback_data="portfolio")],
        [InlineKeyboardButton("🛡️ مدیریت ریسک", callback_data="risk")],
        [InlineKeyboardButton("🐋 نهنگ‌ها", callback_data="whale")],
        [InlineKeyboardButton("📚 آموزش ترید", callback_data="education")],
        [InlineKeyboardButton("🎭 شخصیت", callback_data="personality")],
        [InlineKeyboardButton("🎨 طراحی", callback_data="design")],
        [InlineKeyboardButton("🧘 مدیتیشن", callback_data="meditation")],
        [InlineKeyboardButton("💎 ایده‌پرداز", callback_data="ideas")],
        [InlineKeyboardButton("📜 تاریخچه", callback_data="history")],
        [InlineKeyboardButton("🗑 پاک کردن", callback_data="clear_memory")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    
    text = f"""
{random.choice(['📊', '🔥', '💎', '💰', '⚡'])} **ربات تریدر حرفه‌ای** {random.choice(['📊', '🔥', '💎', '💰', '⚡'])}

`{ascii_arts['chart']}`

🎯 **قابلیت‌های حرفه‌ای:**
• 📊 قیمت لحظه‌ای ۸ ارز
• 🎯 سیگنال خرید/فروش با حد ضرر و سود
• 📈 تحلیل تکنیکال (RSI, MACD, Support/Resistance)
• 🧠 تحلیل هوشمند با AI
• 💰 مدیریت پرتفوی و سود/زیان
• 🛡️ مدیریت ریسک و حد ضرر
• 🐋 ردیابی نهنگ‌ها

---
💫 **شخصیت فعلی:** {personality} {personalities[personality]['emoji']}
⚡ **مدیریت سرمایه:** 2% ریسک در هر معامله
---

📌 **از منوی زیر انتخاب کن:** 👇
"""
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== قیمت لحظه‌ای ==========
async def prices_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for symbol, data in fake_prices.items():
        emoji = "🟢" if data["change"] > 0 else "🔴"
        keyboard.append([InlineKeyboardButton(f"{emoji} {symbol} ${data['usdt']:,.0f}", callback_data=f"price_{symbol}")])
    keyboard.append([InlineKeyboardButton("🔄 بروزرسانی", callback_data="refresh_prices")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    
    text = "📊 **قیمت لحظه‌ای ارزها** 📊\n\n"
    for symbol, data in fake_prices.items():
        emoji = "🟢" if data["change"] > 0 else "🔴"
        text += f"{emoji} **{symbol}**: ${data['usdt']:,.0f} ({data['change']:+.1f}%)\n"
    text += "\n📌 برای مشاهده جزئیات و سیگنال، روی هر ارز کلیک کن"
    
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def price_detail(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    data = fake_prices.get(symbol, {})
    if not data:
        await update.callback_query.edit_message_text("❌ ارز پیدا نشد", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="prices")]]))
        return
    
    signal = generate_signal(symbol, data)
    
    emoji = "🟢" if data["change"] > 0 else "🔴"
    text = f"📊 **{symbol} / USDT** 📊\n\n"
    text += f"{emoji} **قیمت:** ${data['usdt']:,.0f}\n"
    text += f"📈 **تغییر ۲۴h:** {data['change']:+.1f}%\n"
    text += f"📊 **بالاترین:** ${data['high']:,.0f}\n"
    text += f"📉 **پایین‌ترین:** ${data['low']:,.0f}\n"
    text += f"💰 **حجم ۲۴h:** ${data['volume']}B\n"
    text += f"🟢 **حمایت:** ${data['support']:,.0f}\n"
    text += f"🔴 **مقاومت:** ${data['resistance']:,.0f}\n\n"
    
    text += f"🎯 **سیگنال:** "
    if signal["action"] == "BUY":
        text += f"🟢 خرید (قدرت: {signal['strength']}%)\n"
    elif signal["action"] == "SELL":
        text += f"🔴 فروش (قدرت: {signal['strength']}%)\n"
    else:
        text += f"⚪ نگهداری (قدرت: {signal['strength']}%)\n"
    
    text += f"📝 **دلیل:** {signal['reason']}\n"
    if signal["action"] != "HOLD":
        text += f"🛡️ **حد ضرر:** ${signal['stop_loss']:,.0f}\n"
        text += f"🎯 **حد سود:** ${signal['take_profit']:,.0f}\n"
        text += f"📊 **نسبت ریسک به ریوارد:** 1:{((signal['take_profit']/signal['entry'] - 1) / (1 - signal['stop_loss']/signal['entry'])):.1f}\n"
    
    keyboard = [
        [InlineKeyboardButton("📈 تحلیل تکنیکال", callback_data=f"tech_{symbol}")],
        [InlineKeyboardButton("🧠 تحلیل AI", callback_data=f"ai_{symbol}")],
        [InlineKeyboardButton("💰 افزودن به پرتفوی", callback_data=f"add_{symbol}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="prices")]
    ]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== سیگنال‌ها ==========
async def signals_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    signals_list = []
    for symbol, data in fake_prices.items():
        signal = generate_signal(symbol, data)
        signals_list.append((symbol, signal, data["change"]))
    
    signals_list.sort(key=lambda x: x[1]["strength"], reverse=True)
    
    text = "🎯 **سیگنال‌های معاملاتی لحظه‌ای** 🎯\n\n"
    for symbol, signal, change in signals_list[:5]:
        if signal["action"] == "BUY":
            emoji = "🟢"
        elif signal["action"] == "SELL":
            emoji = "🔴"
        else:
            emoji = "⚪"
        text += f"{emoji} **{symbol}**: {signal['action']} | قدرت: {signal['strength']}% | تغییر: {change:+.1f}%\n"
    
    best = signals_list[0]
    worst = signals_list[-1]
    text += f"\n━━━━━━━━━━━━━━━━━━━━\n"
    text += f"🔥 **بهترین سیگنال:** {best[0]} ({best[1]['action']})\n"
    text += f"📉 **ضعیف‌ترین:** {worst[0]} ({worst[1]['action']})\n"
    text += f"\n💡 **مدیریت ریسک:** حداکثر ۲٪ سرمایه در هر معامله"
    
    keyboard = [
        [InlineKeyboardButton("🔄 بروزرسانی", callback_data="refresh_signals")],
        [InlineKeyboardButton("📊 مشاهده همه", callback_data="all_signals")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
    ]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== تحلیل تکنیکال ==========
async def technical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for symbol in fake_prices.keys():
        keyboard.append([InlineKeyboardButton(f"📈 {symbol}", callback_data=f"tech_{symbol}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    
    await update.callback_query.edit_message_text(
        "📈 **تحلیل تکنیکال حرفه‌ای** 📈\n\n"
        "📊 **اندیکاتورهای موجود:**\n"
        "• RSI (قدرت نسبی)\n"
        "• MACD (همگرایی/واگرایی)\n"
        "• سطوح حمایت و مقاومت\n"
        "• میانگین متحرک ساده\n"
        "• حجم معاملات\n\n"
        "ارز مورد نظر را انتخاب کن:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def technical_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    data = fake_prices.get(symbol, {})
    signal = generate_signal(symbol, data)
    
    # محاسبه RSI شبیه‌سازی شده
    rsi = random.randint(25, 75)
    rsi_status = "🟢 اشباع فروش (منطقه خرید)" if rsi < 30 else "🔴 اشباع خرید (منطقه فروش)" if rsi > 70 else "⚪ خنثی"
    
    text = f"📈 **تحلیل تکنیکال {symbol}** 📈\n\n"
    text += f"💰 **قیمت فعلی:** ${data['usdt']:,.0f}\n"
    text += f"📊 **تغییر ۲۴h:** {data['change']:+.1f}%\n\n"
    
    text += "**📊 اندیکاتورها:**\n"
    text += f"• RSI(14): {rsi} → {rsi_status}\n"
    text += f"• MACD: {'صعودی (سیگنال خرید)' if data['change'] > 0 else 'نزولی (سیگنال فروش)'}\n"
    text += f"• میانگین متحرک ۵۰: {'بالا' if data['change'] > 0 else 'پایین'}تر از قیمت\n"
    text += f"• حجم: {data['volume']}B {'(+۱۵%)' if data['change'] > 0 else '(-۵%)'}\n\n"
    
    text += "**🔑 سطوح کلیدی:**\n"
    text += f"🟢 حمایت اصلی: ${data['support']:,.0f}\n"
    text += f"🔴 مقاومت اصلی: ${data['resistance']:,.0f}\n"
    text += f"🟡 حمایت دوم: ${data['support'] * 0.95:,.0f}\n"
    text += f"🔴 مقاومت دوم: ${data['resistance'] * 1.05:,.0f}\n\n"
    
    text += f"**🎯 سیگنال معاملاتی:**\n"
    if signal["action"] == "BUY":
        text += f"🟢 **خرید** با قدرت {signal['strength']}%\n"
    elif signal["action"] == "SELL":
        text += f"🔴 **فروش** با قدرت {signal['strength']}%\n"
    else:
        text += f"⚪ **نگهداری** با قدرت {signal['strength']}%\n"
    
    text += f"📝 **تحلیل:** {signal['reason']}\n"
    
    if signal["action"] != "HOLD":
        text += f"\n**🛡️ مدیریت معامله:**\n"
        text += f"• حد ضرر: ${signal['stop_loss']:,.0f} ({(signal['stop_loss']/signal['entry']-1)*100:+.1f}%)\n"
        text += f"• حد سود: ${signal['take_profit']:,.0f} ({(signal['take_profit']/signal['entry']-1)*100:+.1f}%)\n"
        text += f"• نسبت ریسک به ریوارد: 1:{((signal['take_profit']/signal['entry']-1) / (1 - signal['stop_loss']/signal['entry'])):.1f}\n"
    
    keyboard = [
        [InlineKeyboardButton("🧠 تحلیل با AI", callback_data=f"ai_{symbol}")],
        [InlineKeyboardButton("💰 افزودن به پرتفوی", callback_data=f"add_{symbol}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="technical")]
    ]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== تحلیل با AI ==========
async def ai_analysis_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for symbol in fake_prices.keys():
        keyboard.append([InlineKeyboardButton(f"🧠 {symbol}", callback_data=f"ai_{symbol}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    
    await update.callback_query.edit_message_text(
        "🧠 **تحلیل هوشمند با AI** 🧠\n\n"
        "🤖 هوش مصنوعی Groq بازار رو برات تحلیل می‌کنه:\n"
        "• پیش‌بینی روند\n"
        "• سطوح کلیدی\n"
        "• مدیریت ریسک\n"
        "• بهترین زمان ورود و خروج\n\n"
        "ارز مورد نظر را انتخاب کن:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def ai_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    await update.callback_query.edit_message_text(f"🤖 در حال تحلیل {symbol} با هوش مصنوعی... ⏳", parse_mode="Markdown")
    
    data = fake_prices.get(symbol, {})
    signal = generate_signal(symbol, data)
    
    prompt = f"""به عنوان یک تحلیلگر حرفه‌ای بازار ارزهای دیجیتال، درباره {symbol} تحلیل کن:

قیمت: ${data['usdt']}
تغییر ۲۴h: {data['change']}%
حمایت: ${data['support']}
مقاومت: ${data['resistance']}
سیگنال فعلی: {signal['action']}

لطفاً در ۵ خط تحلیل کن:
1. وضعیت فعلی بازار
2. پیش‌بینی کوتاه مدت
3. توصیه معاملاتی
4. مدیریت ریسک"""
    
    if not GROQ_API_KEY:
        ai_response = f"""📊 **تحلیل {symbol}** 📊

🔍 **وضعیت فعلی:** {signal['reason']}

📈 **پیش‌بینی:** 
{'صعودی تا مقاومت بعدی' if signal['action'] == 'BUY' else 'نزولی تا حمایت بعدی' if signal['action'] == 'SELL' else 'رنج تا شکست یکی از سطوح'}

🎯 **توصیه:** {signal['action']}

🛡️ **مدیریت ریسک:** حد ضرر {signal['stop_loss'] if signal['action'] != 'HOLD' else '۲٪ زیر قیمت'} - حداکثر ۲٪ سرمایه

💡 نکته: همیشه از حد ضرر استفاده کن و بیش از ۲٪ ریسک نکن."""
    else:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 500,
                        "temperature": 0.7
                    }
                )
                if response.status_code == 200:
                    ai_response = response.json()["choices"][0]["message"]["content"]
                else:
                    ai_response = "خطا در ارتباط با AI. لطفاً دوباره تلاش کن."
        except:
            ai_response = "خطا در ارتباط با AI. لطفاً دوباره تلاش کن."
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="ai_analysis")]]
    await update.callback_query.edit_message_text(f"🧠 **تحلیل AI - {symbol}** 🧠\n\n{ai_response}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== مدیریت پرتفوی ==========
async def portfolio_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    portfolio = load_json(PORTFOLIO_FILE)
    user_portfolio = portfolio.get(user_id, {"balance": 10000, "positions": [], "history": []})
    
    total_value = user_portfolio["balance"]
    positions_value = 0
    for pos in user_portfolio["positions"]:
        current_price = fake_prices.get(pos["symbol"], {}).get("usdt", pos["entry_price"])
        positions_value += current_price * pos["amount"]
        total_value += current_price * pos["amount"]
    
    text = f"💰 **پرتفوی شما** 💰\n\n"
    text += f"💵 **موجودی نقد:** ${user_portfolio['balance']:,.0f}\n"
    text += f"📊 **ارزش پوزیشن‌ها:** ${positions_value:,.0f}\n"
    text += f"💎 **ارزش کل:** ${total_value:,.0f}\n"
    text += f"📈 **سود/زیان کل:** ${total_value - 10000:+,.0f} ({((total_value/10000)-1)*100:+.1f}%)\n\n"
    
    if user_portfolio["positions"]:
        text += "**📊 پوزیشن‌های باز:**\n"
        for pos in user_portfolio["positions"]:
            current = fake_prices.get(pos["symbol"], {}).get("usdt", pos["entry_price"])
            pnl = (current - pos["entry_price"]) / pos["entry_price"] * 100
            pnl_direction = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "⚪"
            text += f"{pnl_direction} **{pos['symbol']}**: {pos['amount']} واحد @ ${pos['entry_price']:,.0f} | PnL: {pnl:+.1f}%\n"
    else:
        text += "📭 **هیچ پوزیشن بازی ندارید**\n"
    
    text += f"\n📜 **تعداد کل معاملات:** {len(user_portfolio['history'])}"
    
    keyboard = [
        [InlineKeyboardButton("💰 افزودن موجودی", callback_data="add_balance")],
        [InlineKeyboardButton("📈 بستن پوزیشن", callback_data="close_position")],
        [InlineKeyboardButton("📜 تاریخچه معاملات", callback_data="trade_history")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
    ]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def add_to_portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
    user_id = str(update.effective_user.id)
    portfolio = load_json(PORTFOLIO_FILE)
    user_portfolio = portfolio.get(user_id, {"balance": 10000, "positions": [], "history": []})
    
    data = fake_prices.get(symbol, {})
    price = data["usdt"]
    signal = generate_signal(symbol, data)
    
    if signal["action"] == "HOLD":
        await update.callback_query.edit_message_text(
            f"⚠️ **سیگنال {symbol} نگهداری است**\n\n"
            f"طبق تحلیل، الان زمان مناسبی برای ورود نیست.\n"
            f"📊 قدرت سیگنال: {signal['strength']}%\n"
            f"📝 دلیل: {signal['reason']}\n\n"
            f"صبر کن تا سیگنال خرید یا فروش بدهد.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="prices")]])
        )
        return
    
    # شبیه‌سازی خرید
    amount = user_portfolio["balance"] * 0.2 / price  # 20% سرمایه
    cost = amount * price
    
    if cost > user_portfolio["balance"]:
        await update.callback_query.edit_message_text(
            f"❌ **موجودی کافی نیست!**\n\n"
            f"💰 موجودی: ${user_portfolio['balance']:,.0f}\n"
            f"💰 هزینه مورد نیاز: ${cost:,.0f}\n\n"
            f"لطفاً ابتدا موجودی خود را افزایش دهید.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="portfolio")]])
        )
        return
    
    user_portfolio["balance"] -= cost
    user_portfolio["positions"].append({
        "symbol": symbol,
        "amount": amount,
        "entry_price": price,
        "stop_loss": signal["stop_loss"],
        "take_profit": signal["take_profit"],
        "timestamp": datetime.now().isoformat()
    })
    user_portfolio["history"].append({
        "type": "BUY",
        "symbol": symbol,
        "amount": amount,
        "price": price,
        "timestamp": datetime.now().isoformat()
    })
    
    portfolio[user_id] = user_portfolio
    save_json(PORTFOLIO_FILE, portfolio)
    
    text = f"✅ **خرید {symbol} انجام شد!** ✅\n\n"
    text += f"💰 **مقدار:** {amount:.4f} {symbol}\n"
    text += f"💵 **قیمت:** ${price:,.0f}\n"
    text += f"💎 **کل هزینه:** ${cost:,.0f}\n"
    text += f"🛡️ **حد ضرر:** ${signal['stop_loss']:,.0f}\n"
    text += f"🎯 **حد سود:** ${signal['take_profit']:,.0f}\n"
    text += f"\n💰 **موجودی باقی‌مانده:** ${user_portfolio['balance']:,.0f}"
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="portfolio")]]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== مدیریت ریسک ==========
async def risk_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
🛡️ **مدیریت ریسک حرفه‌ای** 🛡️

━━━━━━━━━━━━━━━━━━━━
📊 **قوانین طلایی:**

1️⃣ **حداکثر ریسک در هر معامله:** ۲٪ سرمایه

2️⃣ **نسبت ریسک به ریوارد:** حداقل ۱:۲

3️⃣ **حد ضرر (Stop Loss):** همیشه اجباری

4️⃣ **حد سود (Take Profit):** حداقل ۲ برابر حد ضرر

5️⃣ **حداکثر معاملات همزمان:** ۳ تا

6️⃣ **حداکثر افت روزانه:** ۶٪ (در صورت رسیدن، توقف)

━━━━━━━━━━━━━━━━━━━━
📈 **فرمول حجم معامله:**

حجم = (سرمایه × ۲٪) / (قیمت ورود - حد ضرر)

━━━━━━━━━━━━━━━━━━━━
💡 **نکات کلیدی:**
• هیچوقت فول مارژین نکن
• از اهرم بالا استفاده نکن
• همیشه به برنامه معاملاتی پایبند باش
• احساسات را از معامله جدا کن
• در ضررهای متوالی، توقف کن

━━━━━━━━━━━━━━━━━━━━
🎯 **وضعیت فعلی بازار:**
• ریسک بازار: متوسط
• نوسان: نرمال
• بهترین استراتژی: اسکالپ و نوسان‌گیری
"""
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== نهنگ‌ها ==========
async def whale_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    whales = [
        {"symbol": "BTC", "amount": 1250, "value": 84000000, "exchange": "Binance", "type": "خرید"},
        {"symbol": "ETH", "amount": 15000, "value": 51800000, "exchange": "Coinbase", "type": "فروش"},
        {"symbol": "SOL", "amount": 250000, "value": 39175000, "exchange": "FTX", "type": "خرید"},
        {"symbol": "BNB", "amount": 8000, "value": 4656000, "exchange": "Binance", "type": "خرید"},
    ]
    
    text = "🐋 **ردیابی نهنگ‌های بازار** 🐋\n\n"
    text += "آخرین تراکنش‌های بزرگ:\n\n"
    for w in whales:
        emoji = "🟢" if w["type"] == "خرید" else "🔴"
        text += f"{emoji} **{w['symbol']}**: {w['amount']:,.0f} واحد (${w['value']:,.0f})\n"
        text += f"   📍 صرافی: {w['exchange']} | نوع: {w['type']}\n\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━\n"
    text += "📊 **تحلیل حرکت نهنگ‌ها:**\n"
    text += "• خرید نهنگ‌ها روی BTC نشانه صعود است\n"
    text += "• فروش ETH می‌تواند اصلاح ایجاد کند\n"
    text += "• ورود پول به SOL نشانه علاقه به آلت‌کوین‌هاست\n\n"
    text += "💡 **توصیه:** از حرکت نهنگ‌ها پیروی کن ولی با مدیریت ریسک"
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== آموزش ==========
async def education_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 مقدمات ترید", callback_data="edu_basics")],
        [InlineKeyboardButton("📈 تحلیل تکنیکال", callback_data="edu_technical")],
        [InlineKeyboardButton("🛡️ مدیریت ریسک", callback_data="edu_risk")],
        [InlineKeyboardButton("🧠 روانشناسی ترید", callback_data="edu_psychology")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back")],
    ]
    
    text = """
📚 **آکادمی ترید حرفه‌ای** 📚

━━━━━━━━━━━━━━━━━━━━
🎯 **دوره‌های آموزشی:**

1️⃣ **مقدمات ترید**
   • انواع معاملات (اسکالپ، روزانه، سوئینگ)
   • آشنایی با صرافی‌ها
   • نحوه ثبت سفارش

2️⃣ **تحلیل تکنیکال**
   • حمایت و مقاومت
   • اندیکاتورها (RSI, MACD, MA)
   • الگوهای کندل‌استیک

3️⃣ **مدیریت ریسک**
   • قانون ۲٪
   • حد ضرر و سود
   • سایز پوزیشن

4️⃣ **روانشناسی ترید**
   • کنترل احساسات
   • نظم و انضباط
   • اجتناب از انتقام‌جویی

━━━━━━━━━━━━━━━━━━━━
📌 **موضوع مورد نظر را انتخاب کن:**
"""
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== بقیه منوها (ساده شده برای فضا) ==========
async def personality_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for name, data in personalities.items():
        keyboard.append([InlineKeyboardButton(f"{data['emoji']} {name}", callback_data=f"set_personality_{name}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    
    current = context.user_data.get("personality", "تریدر حرفه‌ای")
    await update.callback_query.edit_message_text(
        f"🎭 **شخصیت‌های تریدینگ**\n\nشخصیت فعلی: {current}\n\nانتخاب کن:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def set_personality(update: Update, context: ContextTypes.DEFAULT_TYPE, personality: str):
    context.user_data["personality"] = personality
    context.user_data["system_prompt"] = personalities[personality]["prompt"]
    await update.callback_query.edit_message_text(f"✅ شخصیت به {personality} تغییر کرد!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def design_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("🎨 **بخش طراحی** - به زودی اضافه می‌شود", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def meditation_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("🧘 **بخش مدیتیشن** - به زودی اضافه می‌شود", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def ideas_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("💎 **بخش ایده‌پرداز** - به زودی اضافه می‌شود", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def show_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("📜 **تاریخچه** - به زودی اضافه می‌شود", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def clear_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("🗑 **حافظه پاک شد**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
❓ **راهنمای ربات تریدر حرفه‌ای** ❓

🎯 **قابلیت‌های اصلی:**
• 📊 قیمت لحظه‌ای و تحلیل
• 🎯 سیگنال خرید/فروش با قدرت
• 📈 تحلیل تکنیکال کامل
• 🧠 تحلیل هوشمند با AI
• 💰 مدیریت پرتفوی
• 🛡️ مدیریت ریسک
• 🐋 ردیابی نهنگ‌ها

📌 **نکات مهم:**
• هرگز بیش از ۲٪ سرمایه ریسک نکن
• همیشه از حد ضرر استفاده کن
• احساسات را از معامله جدا کن
• به برنامه معاملاتی پایبند باش

⚠️ **هشدار:** این ربات فقط جنبه آموزشی دارد
"""
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
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
    elif data == "whale":
        await whale_menu(update, context)
    elif data == "education":
        await education_menu(update, context)
    elif data == "personality":
        await personality_menu(update, context)
    elif data == "design":
        await design_menu(update, context)
    elif data == "meditation":
        await meditation_menu(update, context)
    elif data == "ideas":
        await ideas_menu(update, context)
    elif data == "history":
        await show_history(update, context)
    elif data == "clear_memory":
        await clear_memory(update, context)
    elif data == "help":
        await help_menu(update, context)
    elif data == "refresh_prices":
        await prices_menu(update, context)
    elif data == "refresh_signals":
        await signals_menu(update, context)
    elif data.startswith("price_"):
        symbol = data.split("_")[1]
        await price_detail(update, context, symbol)
    elif data.startswith("tech_"):
        symbol = data.split("_")[1]
        await technical_analysis(update, context, symbol)
    elif data.startswith("ai_"):
        symbol = data.split("_")[1]
        await ai_analysis(update, context, symbol)
    elif data.startswith("add_"):
        symbol = data.split("_")[1]
        await add_to_portfolio(update, context, symbol)
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
    print("🤖 ربات تریدر حرفه‌ای با مدیریت ریسک روشن شد...")
    app.run_polling()

if __name__ == "__main__":
    main()
