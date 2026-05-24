import logging
from telegram import Bot
from config.settings import TELEGRAM_BOT_TOKEN, CHANNEL_ID

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self):
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)

    async def send_message(self, chat_id, text, parse_mode='Markdown'):
        try:
            await self.bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
            logger.info(f"Message sent to {chat_id}")
        except Exception as e:
            logger.error(f"Failed to send message: {e}")

    async def send_signal(self, signal, signals_1h, signals_15m):
        """ارسال سیگنال به کانال"""
        action = signal['action']
        confidence = signal['confidence']
        strength = signal['strength']
        
        # نمایش قدرت با دایره‌های سبز/قرمز
        strength_bars = ""
        if action == "BUY":
            green = min(10, strength // 10)
            strength_bars = "🟢" * green + "⚪" * (10 - green)
        elif action == "SELL":
            red = min(10, strength // 10)
            strength_bars = "🔴" * red + "⚪" * (10 - red)
        
        msg = f"""
🌿 *سیگنال {action} – {signal.get('symbol', 'BTCUSDT')}* 🌿
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 **سیگنال:** {action} (اطمینان {confidence}%)
💪 **قدرت:** {strength_bars} ({strength}/100)
📊 **امتیاز اندیکاتورها:** {signal.get('timeframes', {})}
🛡️ **حد ضرر:** {signal.get('stop_loss', 0):.2f}
🎯 **هدف:** {signal.get('take_profit', 0):.2f}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ @CryptoPulse606
"""
        await self.send_message(CHANNEL_ID, msg)

    async def send_ai_content(self, content):
        """ارسال محتوای تولید شده توسط AI"""
        await self.send_message(CHANNEL_ID, f"🧠 *تحلیل هوشمند*\n\n{content}")
