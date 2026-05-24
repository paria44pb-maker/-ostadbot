import os
from dotenv import load_dotenv

load_dotenv()

# CoinEx
COINEX_API_KEY = os.getenv("COINEX_API_KEY", "")
COINEX_SECRET_KEY = os.getenv("COINEX_SECRET_KEY", "")
COINEX_PASSPHRASE = os.getenv("COINEX_PASSPHRASE", "")
COINEX_DEMO = os.getenv("COINEX_DEMO", "True").lower() == "true"

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = "@CryptoPulse606"
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/trading_bot")

# Trading
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
TIMEFRAMES = {"4h": 240, "1h": 60, "15m": 15}
MAX_POSITIONS = 3
RISK_PER_TRADE = 0.02  # 2%
ATR_MULTIPLIER_SL = 1.5
RR_RATIO = 2.0
MAX_CONSECUTIVE_LOSSES = 3
AUTO_TRADE_ENABLED = False
REAL_TRADE_ENABLED = False

# Backtest
BACKTEST_DAYS = 90
OPTIMIZE_PARAMS = True
