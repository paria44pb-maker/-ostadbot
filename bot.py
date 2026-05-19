import os
import logging
import hmac
import hashlib
from flask import Flask, request, jsonify
import threading
import numpy as np
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import httpx
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "your-secret-key-here")

# ========== Flask Webhook Server ==========
flask_app = Flask(__name__)
signal_queue = []
bot_instance = None

def verify_webhook_signature(data, signature):
    if not signature:
        return False
    expected = hmac.new(WEBHOOK_SECRET.encode(), data.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

@flask_app.route('/webhook/tradingview', methods=['POST'])
def tradingview_webhook():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data"}), 400
        
        logger.info(f"Signal received: {data}")
        
        signature = request.headers.get('X-Signature', '')
        if WEBHOOK_SECRET and WEBHOOK_SECRET != "your-secret-key-here":
            raw_data = request.get_data(as_text=True)
            if not verify_webhook_signature(raw_data, signature):
                logger.warning("Invalid signature")
                return jsonify({"error": "Invalid signature"}), 401
        
        signal = {
            "symbol": data.get("symbol", "BTCUSDT"),
            "action": data.get("action", data.get("side", "unknown")),
            "price": data.get("price", data.get("close", 0)),
            "quantity": data.get("quantity", 0.01),
            "stop_loss": data.get("stop_loss", 0),
            "take_profit": data.get("take_profit", 0),
            "strategy": data.get("strategy", "unknown"),
            "timeframe": data.get("timeframe", "1h"),
            "timestamp": datetime.now().isoformat(),
        }
        
        action_lower = str(signal["action"]).lower()
        if "buy" in action_lower or "long" in action_lower:
            signal["action"] = "BUY"
        elif "sell" in action_lower or "short" in action_lower:
            signal["action"] = "SELL"
        elif "close" in action_lower:
            signal["action"] = "CLOSE"
        else:
            signal["action"] = "HOLD"
        
        signal_queue.append(signal)
        
        if bot_instance:
            asyncio.create_task(send_signal_to_telegram(signal))
        
        return jsonify({"status": "ok", "signal": signal}), 200
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@flask_app.route('/webhook/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "signals_received": len(signal_queue), "timestamp": datetime.now().isoformat()})

async def send_signal_to_telegram(signal):
    if not bot_instance:
        return
    
    emoji = "🟢" if signal["action"] == "BUY" else "🔴" if signal["action"] == "SELL" else "⚪"
    text = f"{emoji} TradingView Signal {emoji}\n\n"
    text += f"Symbol: {signal['symbol']}\n"
    text += f"Action: {signal['action']}\n"
    if signal['price']:
        try:
            price_val = float(signal['price'])
            text += f"Price: ${price_val:,.0f}\n"
        except:
            text += f"Price: {signal['price']}\n"
    text += f"Strategy: {signal['strategy']}\n"
    text += f"Timeframe: {signal['timeframe']}\n"
    
    try:
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if chat_id:
            await bot_instance.application.bot.send_message(chat_id=chat_id, text=text)
    except Exception as e:
        logger.error(f"Send error: {e}")

def start_webhook_server():
    port = int(os.getenv("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

# ========== Main Bot ==========
class TradingBot:
    def __init__(self):
        self.application = None
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("📊 Prices", callback_data="prices")],
            [InlineKeyboardButton("🎯 Signals", callback_data="signals")],
            [InlineKeyboardButton("📈 Technical", callback_data="technical")],
            [InlineKeyboardButton("📡 TV Signals", callback_data="tv_signals")],
            [InlineKeyboardButton("⚙️ Webhook", callback_data="webhook_settings")],
            [InlineKeyboardButton("💰 Portfolio", callback_data="portfolio")],
            [InlineKeyboardButton("🛡️ Risk", callback_data="risk")],
            [InlineKeyboardButton("❓ Help", callback_data="help")],
        ]
        
        text = "🔥 Crypto Trading Bot + TradingView 🔥\n\n"
        text += "Features:\n"
        text += "- Live prices from Binance\n"
        text += "- TradingView webhook integration\n"
        text += "- Technical analysis (RSI)\n"
        text += "- Portfolio management\n\n"
        text += "Select an option:"
        
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def tv_signals_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not signal_queue:
            text = "📡 TradingView Signals\n\n"
            text += "No signals received yet.\n\n"
            text += "Setup in TradingView:\n"
            text += "1. Create Alert\n"
            text += "2. Webhook URL: https://your-app/webhook/tradingview\n"
            text += "3. Send JSON with symbol, action, price"
        else:
            text = "📡 TradingView Signals\n\n"
            for sig in signal_queue[-10:]:
                emoji = "🟢" if sig["action"] == "BUY" else "🔴" if sig["action"] == "SELL" else "⚪"
                text += f"{emoji} {sig['symbol']} - {sig['action']}"
                if sig['price']:
                    try:
                        price_val = float(sig['price'])
                        text += f" @ ${price_val:,.0f}\n"
                    except:
                        text += f" @ {sig['price']}\n"
                else:
                    text += "\n"
                text += f"   Strategy: {sig['strategy']} | {sig['timeframe']}\n"
                text += f"   Time: {sig['timestamp'][:19]}\n\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def webhook_settings_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "your-domain")
        text = "⚙️ Webhook Settings ⚙️\n\n"
        text += f"URL: https://{domain}/webhook/tradingview\n\n"
        text += f"Secret Key: {WEBHOOK_SECRET}\n\n"
        text += "JSON Format:\n"
        text += '{\n'
        text += '    "symbol": "BTCUSDT",\n'
        text += '    "action": "buy",\n'
        text += '    "price": 50000,\n'
        text += '    "strategy": "MyStrategy"\n'
        text += '}\n\n'
        text += "Variables: close, open, high, low, volume"
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def prices_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.callback_query.edit_message_text("🔄 Fetching prices...")
        
        symbols = ["BTC", "ETH", "SOL", "BNB"]
        text = "📊 Live Prices 📊\n\n"
        
        for symbol in symbols:
            data = await self.get_price(symbol)
            if data:
                emoji = "🟢" if data['change'] > 0 else "🔴" if data['change'] < 0 else "⚪"
                text += f"{emoji} {symbol}/USDT: ${data['price']:,.0f} ({data['change']:+.1f}%)\n\n"
            else:
                text += f"⚪ {symbol}: Error\n\n"
        
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_prices")],
            [InlineKeyboardButton("🔙 Back", callback_data="back")]
        ]
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def signals_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.callback_query.edit_message_text("🔄 Calculating signals...")
        
        text = "🎯 Trading Signals 🎯\n\n"
        text += "From TradingView:\n"
        
        if signal_queue:
            for sig in signal_queue[-3:]:
                emoji = "🟢" if sig["action"] == "BUY" else "🔴" if sig["action"] == "SELL" else "⚪"
                text += f"{emoji} {sig['symbol']}: {sig['action']}"
                if sig['price']:
                    try:
                        price_val = float(sig['price'])
                        text += f" @ ${price_val:,.0f}\n"
                    except:
                        text += f" @ {sig['price']}\n"
                else:
                    text += "\n"
        else:
            text += "No signals yet\n"
        
        text += "\nFrom API:\n"
        symbols = ["BTC", "ETH", "SOL"]
        for symbol in symbols:
            data = await self.get_price(symbol)
            if data:
                change = data['change']
                if change > 1:
                    text += f"🟢 {symbol}: BUY ({change:+.1f}%)\n"
                elif change < -1:
                    text += f"🔴 {symbol}: SELL ({change:+.1f}%)\n"
                else:
                    text += f"⚪ {symbol}: HOLD ({change:+.1f}%)\n"
        
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_signals")],
            [InlineKeyboardButton("🔙 Back", callback_data="back")]
        ]
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def technical_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = []
        for symbol in ["BTC", "ETH", "SOL", "BNB"]:
            keyboard.append([InlineKeyboardButton(f"📈 {symbol}", callback_data=f"tech_{symbol}")])
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back")])
        
        await update.callback_query.edit_message_text("📈 Technical Analysis\n\nSelect a symbol:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def technical_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
        await update.callback_query.edit_message_text(f"📊 Analyzing {symbol}...")
        
        data = await self.get_price(symbol)
        if not data:
            text = "❌ Error fetching data"
        else:
            rsi = self.calculate_rsi([data['price']] * 20)
            support = data['price'] * 0.95
            resistance = data['price'] * 1.05
            
            text = f"📈 Technical Analysis - {symbol} 📈\n\n"
            text += f"Price: ${data['price']:,.0f}\n"
            text += f"24h Change: {data['change']:+.1f}%\n\n"
            text += f"RSI(14): {rsi:.0f} - "
            if rsi < 30:
                text += "Oversold (Buy Zone)\n"
            elif rsi > 70:
                text += "Overbought (Sell Zone)\n"
            else:
                text += "Neutral\n"
            text += f"Support: ${support:,.0f}\n"
            text += f"Resistance: ${resistance:,.0f}\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="technical")]]
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def portfolio_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = "💰 Portfolio 💰\n\n"
        text += "Account Stats:\n"
        text += "- Balance: $10,000\n"
        text += "- Total P&L: $0 (0%)\n"
        text += "- Win Rate: 0%\n"
        text += "- Total Trades: 0\n\n"
        text += "Open Positions:\n"
        text += "No open positions"
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def risk_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = "🛡️ Risk Management 🛡️\n\n"
        text += "Golden Rules:\n"
        text += "1. Max risk per trade: 2%\n"
        text += "2. Risk/Reward ratio: 1:2 minimum\n"
        text += "3. Stop loss: Always required\n"
        text += "4. Max open positions: 3\n"
        text += "5. Max daily drawdown: 6%\n\n"
        text += "Position Size Formula:\n"
        text += "Size = (Capital * 2%) / (Entry - StopLoss)"
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def help_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = "❓ Help Guide ❓\n\n"
        text += "Features:\n"
        text += "- Live prices from Binance\n"
        text += "- TradingView webhook integration\n"
        text += "- Technical analysis with RSI\n"
        text += "- Portfolio tracking\n"
        text += "- Risk management rules\n\n"
        text += "TradingView Setup:\n"
        text += "1. Create an Alert\n"
        text += "2. Set Webhook URL from Settings\n"
        text += "3. Send JSON with symbol, action, price\n\n"
        text += "Disclaimer: Educational only. Trade at your own risk."
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def get_price(self, symbol="BTC"):
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}USDT")
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "price": float(data['lastPrice']),
                        "change": float(data['priceChangePercent']),
                    }
        except Exception as e:
            logger.error(f"Price error: {e}")
        return None
    
    def calculate_rsi(self, prices, period=14):
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
        return 100 - (100 / (1 + (avg_gain / avg_loss)))
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        data = query.data
        
        if data == "back":
            await self.start(update, context)
        elif data == "prices":
            await self.prices_menu(update, context)
        elif data == "signals":
            await self.signals_menu(update, context)
        elif data == "technical":
            await self.technical_menu(update, context)
        elif data == "tv_signals":
            await self.tv_signals_menu(update, context)
        elif data == "webhook_settings":
            await self.webhook_settings_menu(update, context)
        elif data == "portfolio":
            await self.portfolio_menu(update, context)
        elif data == "risk":
            await self.risk_menu(update, context)
        elif data == "help":
            await self.help_menu(update, context)
        elif data == "refresh_prices":
            await self.prices_menu(update, context)
        elif data == "refresh_signals":
            await self.signals_menu(update, context)
        elif data.startswith("tech_"):
            symbol = data.split("_")[1]
            await self.technical_analysis(update, context, symbol)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Please use the menu buttons or /start")
    
    async def run(self):
        global bot_instance
        bot_instance = self
        
        self.application = Application.builder().token(TOKEN).build()
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        webhook_thread = threading.Thread(target=start_webhook_server, daemon=True)
        webhook_thread.start()
        
        logger.info("Bot started with TradingView webhook support...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        await asyncio.Event().wait()

async def main():
    bot = TradingBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
