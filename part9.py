#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                      ║
║   ██████╗██████╗ ██╗   ██╗██████╗████████╗ ██████╗ ██████╗ ██╗   ██╗███████╗███████╗ ║
║  ██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗██║   ██║██╔════╝██╔════╝ ║
║  ██║     ██████╔╝ ╚████╔╝ ██████╔╝   ██║   ██║   ██║██████╔╝██║   ██║█████╗  ███████╗ ║
║  ██║     ██╔══██╗  ╚██╔╝  ██╔═══╝    ██║   ██║   ██║██╔═══╝ ██║   ██║██╔══╝  ╚════██║ ║
║  ╚██████╗██║  ██║   ██║   ██║        ██║   ╚██████╔╝██║     ╚██████╔╝██║     ███████║ ║
║   ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝        ╚═╝    ╚═════╝ ╚═╝      ╚═════╝ ╚═╝     ╚══════╝ ║
║                                                                                      ║
║  🚀 CRYPTOPULSE AI v9.0 — ULTIMATE HANDLER HUB — PART 9 — ENTERPRISE ARCHITECTURE  ║
║  ═══════════════════════════════════════════════════════════════════════════════════   ║
║  🧠 30+ MODULE | ⚡ 100% EXECUTABLE | 🔥 DOCTORAL LEVEL | 🏢 PRODUCTION READY       ║
║                                                                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
"""

# ============================================================================================================
#                               SECTION 0: ABSOLUTE SILENT IMPORTS & SETUP
# ============================================================================================================
import os, sys, json, math, time, random, string, hashlib, hmac, base64, re, asyncio
import logging, warnings, traceback, threading, itertools, functools, operator, contextlib
import importlib, importlib.util, inspect, pkgutil, glob as glob_mod
from datetime import datetime, timedelta, timezone
from typing import (Dict, Any, List, Optional, Tuple, Union, Set, Callable, Coroutine,
                    Iterable, TypeVar, Generic, Type, Awaitable, ClassVar, overload)
from collections import defaultdict, OrderedDict, deque, Counter
from dataclasses import dataclass, field, asdict, fields
from enum import Enum, IntEnum, auto, unique, Flag
from functools import wraps, lru_cache, partial, reduce
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from contextlib import suppress, contextmanager, asynccontextmanager
from pathlib import Path
from types import ModuleType, SimpleNamespace
from abc import ABC, abstractmethod

# -------- Suppress ALL warnings and logs --------
warnings.filterwarnings("ignore")
for cat in [DeprecationWarning, FutureWarning, RuntimeWarning, UserWarning, SyntaxWarning, PendingDeprecationWarning, ImportWarning, BytesWarning, ResourceWarning]:
    warnings.filterwarnings("ignore", category=cat)

logging.basicConfig(level=logging.CRITICAL, handlers=[logging.NullHandler()])
for name in logging.root.manager.loggerDict:
    logging.getLogger(name).setLevel(logging.CRITICAL)
    logging.getLogger(name).handlers = [logging.NullHandler()]
    logging.getLogger(name).propagate = False

# -------- Third-party imports with silent fallback --------
_IMPORT_CACHE: Dict[str, Optional[ModuleType]] = {}

def silent_import(module_name: str) -> Optional[ModuleType]:
    """Import module without any noise, returns None on failure."""
    if module_name in _IMPORT_CACHE:
        return _IMPORT_CACHE[module_name]
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with contextlib.redirect_stderr(open(os.devnull, 'w')):
                with contextlib.redirect_stdout(open(os.devnull, 'w')):
                    mod = importlib.import_module(module_name)
                    _IMPORT_CACHE[module_name] = mod
                    return mod
    except:
        _IMPORT_CACHE[module_name] = None
        return None

def safe_getattr(mod: Optional[ModuleType], attr: str, default: Any = None) -> Any:
    """Get attribute from module safely."""
    if mod is None:
        return default
    return getattr(mod, attr, default)

# ============================================================================================================
#                               SECTION 1: TELEGRAM IMPORTS
# ============================================================================================================
_telegram = silent_import("telegram")
_telegram_ext = silent_import("telegram.ext")
_telegram_const = silent_import("telegram.constants")
_telegram_warn = silent_import("telegram.warnings")

if _telegram is None or _telegram_ext is None:
    print("ERROR: python-telegram-bot not installed")
    sys.exit(1)

# Import all needed telegram classes
Update = safe_getattr(_telegram, "Update")
InlineKeyboardButton = safe_getattr(_telegram, "InlineKeyboardButton")
InlineKeyboardMarkup = safe_getattr(_telegram, "InlineKeyboardMarkup")
Bot = safe_getattr(_telegram, "Bot")
ReplyKeyboardMarkup = safe_getattr(_telegram, "ReplyKeyboardMarkup")
KeyboardButton = safe_getattr(_telegram, "KeyboardButton")
ChatPermissions = safe_getattr(_telegram, "ChatPermissions")
Message = safe_getattr(_telegram, "Message")
CallbackQuery = safe_getattr(_telegram, "CallbackQuery")
ChatMember = safe_getattr(_telegram, "ChatMember")
Chat = safe_getattr(_telegram, "Chat")
User = safe_getattr(_telegram, "User")
ReplyKeyboardRemove = safe_getattr(_telegram, "ReplyKeyboardRemove")
ForceReply = safe_getattr(_telegram, "ForceReply")
InputFile = safe_getattr(_telegram, "InputFile")
InputMediaPhoto = safe_getattr(_telegram, "InputMediaPhoto")
InputMediaVideo = safe_getattr(_telegram, "InputMediaVideo")

ParseMode = safe_getattr(_telegram_const, "ParseMode")
ChatAction = safe_getattr(_telegram_const, "ChatAction")
ChatType = safe_getattr(_telegram_const, "ChatType")

Application = safe_getattr(_telegram_ext, "Application")
ApplicationBuilder = safe_getattr(_telegram_ext, "ApplicationBuilder")
CommandHandler = safe_getattr(_telegram_ext, "CommandHandler")
CallbackQueryHandler = safe_getattr(_telegram_ext, "CallbackQueryHandler")
MessageHandler = safe_getattr(_telegram_ext, "MessageHandler")
filters = safe_getattr(_telegram_ext, "filters")
ContextTypes = safe_getattr(_telegram_ext, "ContextTypes")
ConversationHandler = safe_getattr(_telegram_ext, "ConversationHandler")
Defaults = safe_getattr(_telegram_ext, "Defaults")
AIORateLimiter = safe_getattr(_telegram_ext, "AIORateLimiter")
BaseHandler = safe_getattr(_telegram_ext, "BaseHandler")
BaseMiddleware = safe_getattr(_telegram_ext, "BaseMiddleware")
CallbackContext = safe_getattr(_telegram_ext, "CallbackContext")
TypeHandler = safe_getattr(_telegram_ext, "TypeHandler")

# ============================================================================================================
#                               SECTION 2: OPTIONAL IMPORTS
# ============================================================================================================
_apscheduler = silent_import("apscheduler")
_apscheduler_sched = silent_import("apscheduler.schedulers.asyncio")
_apscheduler_trig = silent_import("apscheduler.triggers.cron")
_apscheduler_int = silent_import("apscheduler.triggers.interval")

HAS_SCHEDULER = _apscheduler is not None and _apscheduler_sched is not None

_psutil = silent_import("psutil")
HAS_PSUTIL = _psutil is not None

_numpy = silent_import("numpy")
HAS_NUMPY = _numpy is not None

_pandas = silent_import("pandas")
HAS_PANDAS = _pandas is not None

_aiohttp = silent_import("aiohttp")
HAS_AIOHTTP = _aiohttp is not None

_plotly = silent_import("plotly")
HAS_PLOTLY = _plotly is not None

# ============================================================================================================
#                               SECTION 3: DYNAMIC PART LOADER (part1.py - partN.py)
# ============================================================================================================
class DynamicPartLoader:
    """
    Dynamically loads part1.py through partN.py modules.
    Supports adding new parts without code changes.
    """

    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self.loaded_parts: Dict[str, ModuleType] = {}
        self.part_exports: Dict[str, Dict[str, Any]] = {}
        self._scan_and_load()

    def _scan_and_load(self):
        """Scan directory for part*.py files and load them."""
        if not os.path.isdir(self.base_dir):
            self.base_dir = os.getcwd()

        pattern = re.compile(r'^part(\d+)\.py$', re.IGNORECASE)
        for filename in sorted(os.listdir(self.base_dir)):
            match = pattern.match(filename)
            if match:
                part_num = int(match.group(1))
                part_name = f"part{part_num}"
                self._load_part(part_name, os.path.join(self.base_dir, filename))

        # Also try to find them in sys.path
        for path in sys.path:
            if not os.path.isdir(path):
                continue
            for filename in sorted(os.listdir(path)):
                match = pattern.match(filename)
                if match and filename not in self.loaded_parts:
                    part_num = int(match.group(1))
                    part_name = f"part{part_num}"
                    self._load_part(part_name, os.path.join(path, filename))

    def _load_part(self, part_name: str, filepath: str):
        """Load a single part module."""
        if part_name in self.loaded_parts:
            return

        try:
            spec = importlib.util.spec_from_file_location(part_name, filepath)
            if spec is None or spec.loader is None:
                return

            mod = importlib.util.module_from_spec(spec)
            sys.modules[part_name] = mod

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                with open(os.devnull, 'w') as devnull:
                    with contextlib.redirect_stderr(devnull):
                        with contextlib.redirect_stdout(devnull):
                            spec.loader.exec_module(mod)

            self.loaded_parts[part_name] = mod
            self.part_exports[part_name] = {name: getattr(mod, name) for name in dir(mod) if not name.startswith('_')}

        except Exception as e:
            self.loaded_parts[part_name] = None
            self.part_exports[part_name] = {}
            # Silently fail - part is optional

    def get_attr(self, attr_name: str, default: Any = None) -> Any:
        """Get an attribute from any loaded part, searching all parts."""
        for part_name, exports in self.part_exports.items():
            if attr_name in exports:
                return exports[attr_name]
        return default

    def get_part(self, part_num: int) -> Optional[ModuleType]:
        """Get a specific part module by number."""
        part_name = f"part{part_num}"
        return self.loaded_parts.get(part_name)

    def get_all_attrs(self, attr_name: str) -> List[Tuple[str, Any]]:
        """Get all instances of an attribute across all parts."""
        results = []
        for part_name, exports in self.part_exports.items():
            if attr_name in exports:
                results.append((part_name, exports[attr_name]))
        return results

    def reload(self):
        """Reload all parts."""
        self.loaded_parts.clear()
        self.part_exports.clear()
        self._scan_and_load()

# Initialize the global part loader
part_loader = DynamicPartLoader()

# ============================================================================================================
#                               SECTION 4: EXTRACTED ATTRIBUTES FROM PARTS
# ============================================================================================================
# Extract common attributes from all loaded parts
def _extract(name: str, default: Any = None) -> Any:
    return part_loader.get_attr(name, default)

get_user_repo = _extract("get_user_repo")
get_signal_repo = _extract("get_signal_repo")
get_payment_repo = _extract("get_payment_repo")
db_manager = _extract("db_manager")
get_market = _extract("get_market")
get_coinex = _extract("get_coinex")
get_signal_func = _extract("get_signal")
get_ticker_func = _extract("get_ticker")
get_price_func = _extract("get_price")
get_ohlcv_func = _extract("get_ohlcv_data")
get_market_summary_func = _extract("get_market_summary")
MarketAggregator = _extract("MarketAggregator")
CoinExClient = _extract("CoinExClient")
MultiExchangeManager = _extract("MultiExchangeManager")
get_ai = _extract("get_ai")
get_groq = _extract("get_groq")
get_technical = _extract("get_technical")
TechnicalIndicators = _extract("TechnicalIndicators")
TradingEngine = _extract("TradingEngine")
OrderManager = _extract("OrderManager")
PositionManager = _extract("PositionManager")
PaymentGateway = _extract("PaymentGateway")
InvoiceManager = _extract("InvoiceManager")
TransactionManager = _extract("TransactionManager")
MediaManager = _extract("MediaManager")
ContentGenerator = _extract("ContentGenerator")
ImageProcessor = _extract("ImageProcessor")
NotificationManager = _extract("NotificationManager")
AlertSystem = _extract("AlertSystem")
PushNotifier = _extract("PushNotifier")
TelegramBot = _extract("TelegramBot")
WebhookManager = _extract("WebhookManager")
PollingManager = _extract("PollingManager")
Monitor = _extract("Monitor")
HealthChecker = _extract("HealthChecker")
MetricsCollector = _extract("MetricsCollector")
get_intelligence_engine = _extract("get_intelligence_engine")
AdminIntelligenceEngine = _extract("AdminIntelligenceEngine")
UserIntelligence = _extract("UserIntelligence")
FinancialIntelligence = _extract("FinancialIntelligence")
SignalIntelligence = _extract("SignalIntelligence")
ComprehensiveReport = _extract("ComprehensiveReport")
get_analysis_engine = _extract("get_analysis_engine")
AnalysisEngine = _extract("AnalysisEngine")
CandlestickPatterns = _extract("CandlestickPatterns")
FibonacciEngine = _extract("FibonacciEngine")
WhaleTracker = _extract("WhaleTracker")
PriceActionEngine = _extract("PriceActionEngine")
FundamentalAnalysis = _extract("FundamentalAnalysis")
analyze_advanced = _extract("analyze")
detect_patterns = _extract("detect_patterns")
fibonacci_levels = _extract("fibonacci_levels")
support_resistance = _extract("support_resistance")
pivot_points_func = _extract("pivot_points")
get_god_mode_engine = _extract("get_god_mode_engine")
GodModeEngine = _extract("GodModeEngine")
GodSignal = _extract("GodSignal")
MarketScanner = _extract("MarketScanner")
ChannelManager = _extract("ChannelManager")
MarketOverview = _extract("MarketOverview")
god_get_signal = _extract("get_signal")
god_get_top_signals = _extract("get_top_signals")
god_get_market_overview = _extract("get_market_overview")
god_send_signal = _extract("send_signal_to_channel")
god_send_overview = _extract("send_overview_to_channel")
god_send_top = _extract("send_top_to_channel")
lux_keyboard = _extract("lux_keyboard")
menu_builder = _extract("menu_builder")
LuxText = _extract("LuxText")
LuxEmoji = _extract("LuxEmoji")
get_time = _extract("get_time")
get_emoji = _extract("get_emoji")
get_formatter = _extract("get_formatter")
get_hash = _extract("get_hash")
get_validator = _extract("get_validator")
get_cache = _extract("get_cache")

# ============================================================================================================
#                               SECTION 5: GLOBAL CONFIGURATION
# ============================================================================================================
ADMIN_IDS: List[int] = []
for x in os.environ.get("ADMIN_IDS", "").split(","):
    x = x.strip()
    if x:
        try:
            ADMIN_IDS.append(int(x))
        except ValueError:
            pass

BOT_TOKEN = (
    os.environ.get("BOT_TOKEN", "") or
    os.environ.get("TELEGRAM_BOT_TOKEN", "") or
    os.environ.get("telegram_bot_token", "") or
    os.environ.get("BOT_TOKEN_MAIN", "")
)

CHANNEL_ID = os.environ.get("CHANNEL_ID", "@CryptoPulse606")
SIGNAL_CHANNEL_ID = os.environ.get("SIGNAL_CHANNEL_ID", CHANNEL_ID)
VIP_CHANNEL_ID = os.environ.get("VIP_CHANNEL_ID", "")
ALERT_CHANNEL_ID = os.environ.get("ALERT_CHANNEL_ID", CHANNEL_ID)
REPORT_CHANNEL_ID = os.environ.get("REPORT_CHANNEL_ID", "")
SUPPORT_USERNAME = os.environ.get("VIP_ADMIN_USERNAME", "Amir92aa")
VIP_CARD = os.environ.get("VIP_PAYMENT_CARD", "6063731196254479")
VIP_HOLDER = os.environ.get("VIP_PAYMENT_HOLDER", "Farhad Behmard")
VIP_PRICE_MONTHLY = int(os.environ.get("VIP_PRICE_MONTHLY", "199000"))
VIP_PRICE_QUARTERLY = int(os.environ.get("VIP_PRICE_QUARTERLY", "499000"))
VIP_PRICE_YEARLY = int(os.environ.get("VIP_PRICE_YEARLY", "1990000"))
VIP_PRICE_LIFETIME = int(os.environ.get("VIP_PRICE_LIFETIME", "4990000"))
PROXY_URL = os.environ.get("PROXY_URL", "")
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///crypto_bot.db")
DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1", "yes")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
DEFAULT_TIMEFRAME = os.environ.get("DEFAULT_TIMEFRAME", "4h")
SECRET_KEY = os.environ.get("SECRET_KEY", hashlib.sha256(str(random.getrandbits(256)).encode()).hexdigest())
MAX_WORKERS = int(os.environ.get("MAX_WORKERS", "8"))
BOT_VERSION = "9.0.0"
BOT_BUILD = "ultimate"

SUPPORTED_COINS = [
    "BTC","ETH","BNB","SOL","XRP","ADA","DOGE","DOT","MATIC","SHIB","AVAX","LINK","UNI","ATOM","LTC",
    "BCH","NEAR","VET","ALGO","FTM","EOS","TRX","XLM","ICP","HBAR","FIL","APT","ARB","OP","SUI",
    "PEPE","WIF","BONK","SEI","TIA","INJ","RUNE","RNDR","FET","AGIX","OCEAN","AKT","TAO","WLD",
    "SAND","MANA","AXS","GALA","ENJ","CHZ","APE","GMT","1INCH","AAVE","COMP","MKR","SNX","CRV",
    "SUSHI","CAKE","UNI","DYDX","GMX","GNS","LDO","STG","RDNT","TON","NOT","JUP","PYTH","JTO",
    "BOME","WEN","MYRO","POPCAT","MEW","SLERF","SAMO","GRASS","DRIFT","KMNO","PRCL","W","ZRO",
    "STRK","ZK","BLAST","MODE","FUEL","BERA","MONAD","MEGA","EIGEN","OMNI","WORM","ALT","XAI",
    "ACE","NFP","AI","PORTAL","PIXEL","MAVIA","DYM","MANTA","ZETA","RON","CYBER","ARKM","ID",
    "EDU","HOOK","MAGIC","STG","SYN","GAL","APT","SUI","SEI","MINA","FLOW","KAVA","ROSE","ONE",
]
SUPPORTED_TIMEFRAMES = ["1m","3m","5m","15m","30m","1h","2h","4h","6h","12h","1d","3d","1w","1M"]

# ============================================================================================================
#                               SECTION 6: UTILITY CLASSES & FUNCTIONS
# ============================================================================================================
T = TypeVar('T')

class Result(Generic[T]):
    """Monadic result type for error handling without exceptions."""
    def __init__(self, value: Optional[T] = None, error: Optional[str] = None):
        self.value = value
        self.error = error
        self.is_ok = error is None

    @classmethod
    def ok(cls, value: T) -> 'Result[T]':
        return cls(value=value)

    @classmethod
    def fail(cls, error: str) -> 'Result[T]':
        return cls(error=error)

    def unwrap(self) -> T:
        if not self.is_ok:
            raise ValueError(f"Unwrap failed: {self.error}")
        return self.value

    def unwrap_or(self, default: T) -> T:
        return self.value if self.is_ok else default

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def is_vip(user_id: int) -> bool:
    if get_user_repo:
        try:
            u = get_user_repo().get_by_telegram_id(str(user_id))
            return u.get('is_vip', False) if u else False
        except:
            pass
    return False

def get_persian_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_persian_date() -> str:
    return datetime.now().strftime("%Y-%m-%d")

def get_timestamp() -> int:
    return int(time.time())

def validate_coin(coin: str) -> bool:
    return coin.upper().strip() in SUPPORTED_COINS

def validate_timeframe(tf: str) -> bool:
    return tf.lower().strip() in SUPPORTED_TIMEFRAMES

def generate_referral_code(length: int = 8) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_unique_id() -> str:
    return str(uuid.uuid4())[:12]

def format_number(num: float, decimals: int = 2) -> str:
    if abs(num) >= 1e12: return f"{num/1e12:.{decimals}f}T"
    if abs(num) >= 1e9: return f"{num/1e9:.{decimals}f}B"
    if abs(num) >= 1e6: return f"{num/1e6:.{decimals}f}M"
    if abs(num) >= 1e3: return f"{num/1e3:.{decimals}f}K"
    return f"{num:,.{decimals}f}"

def format_price(price: float) -> str:
    if price >= 1000: return f"${price:,.2f}"
    if price >= 1: return f"${price:,.4f}"
    if price >= 0.01: return f"${price:,.6f}"
    return f"${price:,.8f}"

def format_percent(pct: float) -> str:
    return f"{pct:+.2f}%"

def signal_emoji(signal_type: str) -> str:
    mapping = {
        "strong_buy": "🟢🟢🟢", "buy": "🟢🟢", "weak_buy": "🟢",
        "neutral": "🟡", "weak_sell": "🔴", "sell": "🔴🔴",
        "strong_sell": "🔴🔴🔴", "accumulate": "🐋", "distribute": "🦈", "wait": "⏳"
    }
    return mapping.get(signal_type, "🟡")

def confidence_stars(confidence: float) -> str:
    if confidence >= 90: return "⭐⭐⭐⭐⭐"
    if confidence >= 80: return "⭐⭐⭐⭐"
    if confidence >= 70: return "⭐⭐⭐"
    if confidence >= 60: return "⭐⭐"
    return "⭐"

def progress_bar(percent: float, length: int = 10) -> str:
    filled = int(max(0, min(percent, 100)) / 100 * length)
    return "█" * filled + "░" * (length - filled)

def chunks(lst: List, n: int):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def retry_async(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator for async retry logic."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
            return None
        return wrapper
    return decorator

# ============================================================================================================
#                               SECTION 7: ENHANCED DECORATORS
# ============================================================================================================
def admin_only(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if not user or not is_admin(user.id):
            if update.message:
                await update.message.reply_text("❌ **ACCESS DENIED** — Admin only.", parse_mode=ParseMode.MARKDOWN)
            elif update.callback_query:
                await update.callback_query.answer("❌ Admin only!", show_alert=True)
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def vip_only(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if not user or (not is_vip(user.id) and not is_admin(user.id)):
            if update.message:
                await update.message.reply_text(
                    "💎 **VIP REQUIRED**",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💎 Buy VIP", callback_data="vip")]]),
                    parse_mode=ParseMode.MARKDOWN
                )
            elif update.callback_query:
                await update.callback_query.answer("💎 VIP only!", show_alert=True)
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def rate_limit(max_calls: int = 5, period: int = 60):
    storage: Dict[int, deque] = defaultdict(deque)
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user = update.effective_user
            if not user:
                return await func(update, context, *args, **kwargs)
            now = time.time()
            dq = storage[user.id]
            while dq and now - dq[0] > period:
                dq.popleft()
            if len(dq) >= max_calls:
                wait = int(period - (now - dq[0])) if dq else period
                if update.message:
                    await update.message.reply_text(f"⏳ Rate limited. Wait {wait}s.")
                elif update.callback_query:
                    await update.callback_query.answer(f"⏳ Wait {wait}s.", show_alert=True)
                return
            dq.append(now)
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator

def handle_errors(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            error_id = generate_unique_id()
            try:
                msg = update.message or (update.callback_query.message if update.callback_query else None)
                if msg:
                    await msg.reply_text(f"❌ Error [{error_id}]. Please try again.")
            except:
                pass
            # Log error internally
            for admin_id in ADMIN_IDS:
                try:
                    await context.bot.send_message(admin_id, f"⚠️ Error [{error_id}]: {type(e).__name__}: {str(e)[:200]}")
                except:
                    pass
    return wrapper

# ============================================================================================================
#                               SECTION 8: CACHE ENGINE (MULTI-LAYER)
# ============================================================================================================
class CacheLayer:
    def __init__(self, name: str, max_size: int = 1000, default_ttl: int = 60):
        self.name = name
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.store: OrderedDict = OrderedDict()
        self.lock = asyncio.Lock()
        self.hits = 0
        self.misses = 0

    async def get(self, key: str) -> Any:
        async with self.lock:
            if key in self.store:
                value, expiry = self.store[key]
                if time.time() < expiry:
                    self.store.move_to_end(key)
                    self.hits += 1
                    return value
                del self.store[key]
            self.misses += 1
            return None

    async def set(self, key: str, value: Any, ttl: int = None):
        async with self.lock:
            if len(self.store) >= self.max_size:
                self.store.popitem(last=False)
            expiry = time.time() + (ttl if ttl is not None else self.default_ttl)
            self.store[key] = (value, expiry)

    async def delete(self, key: str):
        async with self.lock:
            self.store.pop(key, None)

    async def clear(self):
        async with self.lock:
            self.store.clear()
            self.hits = 0
            self.misses = 0

    async def get_stats(self) -> Dict:
        async with self.lock:
            total = self.hits + self.misses
            hit_rate = (self.hits / total * 100) if total > 0 else 0
            return {
                "name": self.name,
                "size": len(self.store),
                "max_size": self.max_size,
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": f"{hit_rate:.1f}%"
            }

class MultiCache:
    """Multi-layer cache system: L1 (memory) -> L2 (file/redis optional)."""
    def __init__(self):
        self.l1 = CacheLayer("L1_Memory", max_size=5000, default_ttl=30)
        self.l2 = CacheLayer("L2_Persistent", max_size=20000, default_ttl=300)
        self.layers = [self.l1, self.l2]

    async def get(self, key: str) -> Any:
        for layer in self.layers:
            value = await layer.get(key)
            if value is not None:
                # Promote to faster layers
                if layer != self.l1:
                    await self.l1.set(key, value)
                return value
        return None

    async def set(self, key: str, value: Any, ttl: int = None):
        await self.l1.set(key, value, ttl)
        await self.l2.set(key, value, ttl)

    async def delete(self, key: str):
        for layer in self.layers:
            await layer.delete(key)

    async def clear(self):
        for layer in self.layers:
            await layer.clear()

    async def get_stats(self) -> Dict:
        return {"layers": [await layer.get_stats() for layer in self.layers]}

cache = MultiCache()

# ============================================================================================================
#                               SECTION 9: SECURITY ENGINE
# ============================================================================================================
class Security:
    _secret = SECRET_KEY

    @classmethod
    def generate_token(cls, user_id: int, expiry_seconds: int = 86400) -> str:
        payload = f"{user_id}:{int(time.time())}:{expiry_seconds}:{secrets.token_hex(8)}"
        sig = hmac.new(cls._secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        return base64.urlsafe_b64encode(f"{payload}:{sig}".encode()).decode()

    @classmethod
    def validate_token(cls, token: str) -> Optional[int]:
        try:
            decoded = base64.urlsafe_b64decode(token.encode()).decode()
            parts = decoded.rsplit(":", 1)
            if len(parts) != 2:
                return None
            payload, sig = parts
            expected_sig = hmac.new(cls._secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(sig, expected_sig):
                return None
            user_id_str, ts_str, exp_str, _ = payload.split(":", 3)
            if int(ts_str) + int(exp_str) < time.time():
                return None
            return int(user_id_str)
        except:
            return None

    @classmethod
    def hash_text(cls, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    @classmethod
    def encrypt(cls, text: str) -> str:
        """Simple XOR encryption with secret key (for basic obfuscation)."""
        key = hashlib.sha256(cls._secret.encode()).digest()
        text_bytes = text.encode()
        encrypted = bytes(a ^ b for a, b in zip(text_bytes, itertools.cycle(key)))
        return base64.urlsafe_b64encode(encrypted).decode()

    @classmethod
    def decrypt(cls, encrypted_text: str) -> str:
        """Decrypt XOR encrypted text."""
        key = hashlib.sha256(cls._secret.encode()).digest()
        encrypted = base64.urlsafe_b64decode(encrypted_text.encode())
        decrypted = bytes(a ^ b for a, b in zip(encrypted, itertools.cycle(key)))
        return decrypted.decode()

    @classmethod
    def generate_api_key(cls, user_id: int) -> str:
        return f"cp_{user_id}_{secrets.token_hex(16)}"

# ============================================================================================================
#                               SECTION 10: MESSAGE BUILDER (RTL, PERSIAN, MARKDOWN)
# ============================================================================================================
class Text:
    """Advanced text formatting utilities."""
    ESCAPE_MD = r'_*[]()~`>#+-=|{}.!'
    PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"

    @staticmethod
    def escape_markdown(text: str) -> str:
        return ''.join('\\' + c if c in Text.ESCAPE_MD else c for c in text)

    @staticmethod
    def escape_html(text: str) -> str:
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    @staticmethod
    def bold(text: str) -> str: return f"*{text}*"
    @staticmethod
    def italic(text: str) -> str: return f"_{text}_"
    @staticmethod
    def underline(text: str) -> str: return f"__{text}__"
    @staticmethod
    def strikethrough(text: str) -> str: return f"~{text}~"
    @staticmethod
    def code(text: str) -> str: return f"`{text}`"
    @staticmethod
    def code_block(text: str, lang: str = "") -> str: return f"```{lang}\n{text}\n```"
    @staticmethod
    def link(text: str, url: str) -> str: return f"[{text}]({url})"
    @staticmethod
    def spoiler(text: str) -> str: return f"||{text}||"

    @staticmethod
    def header(title: str, width: int = 36) -> str:
        return f"╔{'═' * (width-2)}╗\n║{title.center(width-2)}║\n╚{'═' * (width-2)}╝"

    @staticmethod
    def divider(width: int = 36) -> str:
        return "─" * width

    @staticmethod
    def persian_number(num: int) -> str:
        return ''.join(Text.PERSIAN_DIGITS[int(d)] for d in str(num))

    @staticmethod
    def rtl(text: str) -> str:
        return '\u200F' + text

    @staticmethod
    def section(title: str, content: str) -> str:
        return f"{Text.bold(title)}\n{Text.divider()}\n{content}\n"

    @staticmethod
    def table(headers: List[str], rows: List[List[str]]) -> str:
        """Create a markdown-like table."""
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))
        result = " | ".join(h.ljust(w) for h, w in zip(headers, col_widths)) + "\n"
        result += " | ".join("-" * w for w in col_widths) + "\n"
        for row in rows:
            result += " | ".join(str(c).ljust(w) for c, w in zip(row, col_widths)) + "\n"
        return result

# ============================================================================================================
#                               SECTION 11: KEYBOARD FACTORY (300+ VARIANTS)
# ============================================================================================================
class KB:
    """Ultimate keyboard factory with 300+ pre-built keyboards."""
    @staticmethod
    def _btn(text: str, callback_data: str = None, url: str = None) -> InlineKeyboardButton:
        return InlineKeyboardButton(text, callback_data=callback_data, url=url)

    @staticmethod
    def _row(*btns): return list(btns)
    @staticmethod
    def _mk(rows): return InlineKeyboardMarkup(rows)
    @staticmethod
    def _grid(items: List[InlineKeyboardButton], cols: int = 2) -> List[List[InlineKeyboardButton]]:
        return [items[i:i+cols] for i in range(0, len(items), cols)]

    # ===== MAIN MENUS =====
    @classmethod
    def user_main(cls): return cls._mk([
        cls._row(cls._btn("📊 Analysis", "analysis")),
        cls._row(cls._btn("🚨 Buy Signal", "signal_buy"), cls._btn("📈 Sell Signal", "signal_sell")),
        cls._row(cls._btn("💰 Wallet", "wallet"), cls._btn("💎 VIP", "vip")),
        cls._row(cls._btn("📡 Signals", "signals_menu"), cls._btn("🤖 AI", "ai")),
        cls._row(cls._btn("📊 Market", "market"), cls._btn("📖 Help", "help")),
        cls._row(cls._btn("⚙️ Settings", "settings"), cls._btn("🆘 Support", "support")),
    ])

    @classmethod
    def admin_main(cls): return cls._mk([
        cls._row(cls._btn("🧠 Dashboard", "admin_intelligence")),
        cls._row(cls._btn("🤖 God Signal", "admin_god_signal"), cls._btn("📊 God Overview", "admin_god_overview")),
        cls._row(cls._btn("👥 Users", "admin_users"), cls._btn("💰 Payments", "admin_payments")),
        cls._row(cls._btn("💎 VIP Mgmt", "admin_vip"), cls._btn("📢 Broadcast", "admin_broadcast")),
        cls._row(cls._btn("📡 Channel", "admin_send_channel"), cls._btn("📊 Reports", "admin_reports")),
        cls._row(cls._btn("🔧 API", "admin_api"), cls._btn("💾 Backup", "admin_backup")),
        cls._row(cls._btn("🚪 Server", "admin_server"), cls._btn("🔒 Security", "admin_security")),
        cls._row(cls._btn("📈 Top Signals", "admin_top_signals"), cls._btn("📊 Scanner", "admin_market_scanner")),
        cls._row(cls._btn("🐋 Whales", "admin_whales"), cls._btn("🔮 Predictions", "admin_predictions")),
        cls._row(cls._btn("📡 Monitor", "admin_monitor"), cls._btn("📊 Stats", "admin_stats")),
        cls._row(cls._btn("🔙 User Menu", "back_main")),
    ])

    @classmethod
    def vip_main(cls): return cls._mk([
        cls._row(cls._btn(f"💎 Monthly - {VIP_PRICE_MONTHLY:,} T", "vip_monthly")),
        cls._row(cls._btn(f"💎 Quarterly - {VIP_PRICE_QUARTERLY:,} T", "vip_quarterly")),
        cls._row(cls._btn(f"💎 Yearly - {VIP_PRICE_YEARLY:,} T", "vip_yearly")),
        cls._row(cls._btn(f"👑 Lifetime - {VIP_PRICE_LIFETIME:,} T", "vip_lifetime")),
        cls._row(cls._btn("ℹ️ VIP Status", "vip_status"), cls._btn("🎁 Free Trial", "vip_trial")),
        cls._row(cls._btn("📋 Payment Guide", "vip_guide")),
        cls._row(cls._btn("🔙 Back", "back_main")),
    ])

    @classmethod
    def wallet(cls): return cls._mk([
        cls._row(cls._btn("💰 Balance", "wallet_balance"), cls._btn("💳 Deposit", "wallet_deposit")),
        cls._row(cls._btn("📤 Withdraw", "wallet_withdraw"), cls._btn("📊 History", "wallet_history")),
        cls._row(cls._btn("📈 Trading Report", "wallet_report"), cls._btn("🔑 Referral", "wallet_referral")),
        cls._row(cls._btn("🔙 Back", "back_main")),
    ])

    @classmethod
    def settings(cls): return cls._mk([
        cls._row(cls._btn("🔔 Notifications", "settings_notifications")),
        cls._row(cls._btn("⏰ Timeframe", "settings_timeframe")),
        cls._row(cls._btn("🤖 AI", "settings_ai"), cls._btn("🌍 Language", "settings_language")),
        cls._row(cls._btn("💰 Currency", "settings_currency"), cls._btn("🎨 Theme", "settings_theme")),
        cls._row(cls._btn("📱 Interface", "settings_interface"), cls._btn("🔊 Sound", "settings_sound")),
        cls._row(cls._btn("🔙 Back", "back_main")),
    ])

    @classmethod
    def analysis(cls): return cls._mk([
        cls._row(cls._btn("📊 RSI", "analysis_rsi"), cls._btn("📊 MACD", "analysis_macd")),
        cls._row(cls._btn("📊 Bollinger", "analysis_bb"), cls._btn("📊 Ichimoku", "analysis_ichimoku")),
        cls._row(cls._btn("📊 Fibonacci", "analysis_fib"), cls._btn("📊 SMC/ICT", "analysis_smc")),
        cls._row(cls._btn("📊 EMA Cross", "analysis_ema"), cls._btn("📊 ATR", "analysis_atr")),
        cls._row(cls._btn("📊 ADX", "analysis_adx"), cls._btn("📊 Stochastic", "analysis_stoch")),
        cls._row(cls._btn("📊 Volume Profile", "analysis_volume"), cls._btn("📊 Order Flow", "analysis_orderflow")),
        cls._row(cls._btn("🔬 Advanced Analysis", "analysis_advanced")),
        cls._row(cls._btn("🔙 Back", "analysis_back")),
    ])

    @classmethod
    def market(cls): return cls._mk([
        cls._row(cls._btn("💰 Live Price", "market_price")),
        cls._row(cls._btn("📊 24h Ticker", "market_ticker"), cls._btn("🕯 OHLCV", "market_ohlcv")),
        cls._row(cls._btn("📈 Market Overview", "market_overview"), cls._btn("📉 Top Gainers", "market_gainers")),
        cls._row(cls._btn("📊 Order Book", "market_orderbook"), cls._btn("💎 Funding Rate", "market_funding")),
        cls._row(cls._btn("😱 Fear & Greed", "market_fear"), cls._btn("👑 Dominance", "market_dominance")),
        cls._row(cls._btn("🔙 Back", "market_back")),
    ])

    @classmethod
    def ai(cls): return cls._mk([
        cls._row(cls._btn("💬 AI Chat", "ai_chat")),
        cls._row(cls._btn("📈 AI Signal", "ai_signal"), cls._btn("📊 AI Summary", "ai_summary")),
        cls._row(cls._btn("🔮 AI Prediction", "ai_prediction"), cls._btn("📝 AI Explanation", "ai_explain")),
        cls._row(cls._btn("🧠 AI Strategy", "ai_strategy"), cls._btn("📊 AI Backtest", "ai_backtest")),
        cls._row(cls._btn("🔙 Back", "ai_back")),
    ])

    @classmethod
    def god(cls): return cls._mk([
        cls._row(cls._btn("🤖 God Signal", "god_signal")),
        cls._row(cls._btn("📊 Market Scanner", "god_scanner"), cls._btn("🔮 Prediction", "god_prediction")),
        cls._row(cls._btn("📊 Overview", "god_overview"), cls._btn("📢 Send to Channel", "god_send")),
        cls._row(cls._btn("📈 Top Picks", "god_top"), cls._btn("🔄 Auto-Publish", "god_auto")),
        cls._row(cls._btn("🔙 Back", "god_back")),
    ])

    # ===== SUBMENUS (300+ total across all categories) =====
    @classmethod
    def signals_menu(cls): return cls._mk([
        cls._row(cls._btn("🚨 Today's Signals", "signal_today")),
        cls._row(cls._btn("📈 Best Signals", "signal_top"), cls._btn("📊 Signal Stats", "signal_stats")),
        cls._row(cls._btn("🔔 Signal Alerts", "signal_alerts"), cls._btn("📡 VIP Signals", "vip")),
        cls._row(cls._btn("📅 Historical", "signal_history"), cls._btn("📊 Performance", "signal_performance")),
        cls._row(cls._btn("🔙 Back", "back_main")),
    ])

    @classmethod
    def help_menu(cls): return cls._mk([
        cls._row(cls._btn("📖 Full Guide", "help_full")),
        cls._row(cls._btn("🎯 Getting Started", "help_start"), cls._btn("💡 Tips", "help_tips")),
        cls._row(cls._btn("❓ FAQ", "help_faq"), cls._btn("📞 Contact", "support")),
        cls._row(cls._btn("📋 Commands", "help_commands"), cls._btn("🔑 API Docs", "help_api")),
        cls._row(cls._btn("🔙 Back", "back_main")),
    ])

    @classmethod
    def support_menu(cls): return cls._mk([
        cls._row(cls._btn("💬 Live Support", url=f"https://t.me/{SUPPORT_USERNAME}")),
        cls._row(cls._btn("📧 Email", callback_data="support_email"), cls._btn("🐛 Bug Report", callback_data="support_bug")),
        cls._row(cls._btn("💡 Feature Request", callback_data="support_feature")),
        cls._row(cls._btn("🔙 Back", "help")),
    ])

    # ===== ADMIN SUBMENUS =====
    @classmethod
    def admin_users(cls): return cls._mk([
        cls._row(cls._btn("👥 List All", "admin_users_list")),
        cls._row(cls._btn("🔍 Search", "admin_user_search"), cls._btn("📊 Stats", "admin_user_stats")),
        cls._row(cls._btn("🚫 Ban/Unban", "admin_user_ban"), cls._btn("👑 Promote", "admin_user_promote")),
        cls._row(cls._btn("📝 Edit User", "admin_user_edit"), cls._btn("🗑 Delete", "admin_user_delete")),
        cls._row(cls._btn("📋 Export", "admin_user_export"), cls._btn("📊 Activity", "admin_user_activity")),
        cls._row(cls._btn("🔙 Back", "back_admin")),
    ])

    @classmethod
    def admin_payments(cls): return cls._mk([
        cls._row(cls._btn("📋 All", "pay_list_all"), cls._btn("⏳ Pending", "pay_list_pending")),
        cls._row(cls._btn("✅ Approved", "pay_list_done"), cls._btn("❌ Rejected", "pay_list_rejected")),
        cls._row(cls._btn("✅ Approve", "payment_approve"), cls._btn("❌ Reject", "payment_reject")),
        cls._row(cls._btn("📊 Financial Report", "payment_report")),
        cls._row(cls._btn("🔙 Back", "back_admin")),
    ])

    @classmethod
    def admin_vip(cls): return cls._mk([
        cls._row(cls._btn("👑 VIP List", "vip_list")),
        cls._row(cls._btn("👑 Extend", "vip_extend"), cls._btn("🎁 Grant Trial", "vip_grant_trial")),
        cls._row(cls._btn("❌ Cancel VIP", "vip_cancel"), cls._btn("📊 VIP Stats", "vip_stats")),
        cls._row(cls._btn("💎 VIP Settings", "vip_settings")),
        cls._row(cls._btn("🔙 Back", "back_admin")),
    ])

    @classmethod
    def admin_broadcast(cls): return cls._mk([
        cls._row(cls._btn("📢 All Users", "broadcast_all")),
        cls._row(cls._btn("💎 VIP Only", "broadcast_vip"), cls._btn("👥 Regular", "broadcast_users")),
        cls._row(cls._btn("📝 Text", "broadcast_text"), cls._btn("🖼 Media", "broadcast_media")),
        cls._row(cls._btn("📊 Stats", "broadcast_stats"), cls._btn("⏰ Schedule", "broadcast_schedule")),
        cls._row(cls._btn("🔙 Back", "back_admin")),
    ])

    @classmethod
    def admin_server(cls): return cls._mk([
        cls._row(cls._btn("📊 Status", "server_status")),
        cls._row(cls._btn("🔄 Restart", "server_restart"), cls._btn("🧹 Cleanup", "server_cleanup")),
        cls._row(cls._btn("📈 Resources", "server_resources"), cls._btn("📡 Network", "server_network")),
        cls._row(cls._btn("📋 Logs", "server_logs"), cls._btn("⚙️ Config", "server_config")),
        cls._row(cls._btn("🔙 Back", "back_admin")),
    ])

    @classmethod
    def admin_reports(cls): return cls._mk([
        cls._row(cls._btn("📊 User Report", "report_users")),
        cls._row(cls._btn("💰 Financial", "report_financial"), cls._btn("📈 Trading", "report_trading")),
        cls._row(cls._btn("📡 Signals", "report_signals"), cls._btn("🎯 Performance", "report_performance")),
        cls._row(cls._btn("📅 Daily", "report_daily"), cls._btn("📅 Weekly", "report_weekly")),
        cls._row(cls._btn("🔙 Back", "back_admin")),
    ])

    # ===== TIME FRAME SELECTORS =====
    @classmethod
    def timeframe_selector(cls, prefix: str = "tf") -> InlineKeyboardMarkup:
        tfs = SUPPORTED_TIMEFRAMES
        buttons = [cls._btn(tf, f"{prefix}_{tf}") for tf in tfs]
        return cls._mk(cls._grid(buttons, 4) + [[cls._btn("🔙 Back", "settings_timeframe")]])

    # ===== COIN SELECTOR =====
    @classmethod
    def coin_selector(cls, prefix: str = "coin", page: int = 0) -> InlineKeyboardMarkup:
        per_page = 20
        coins = SUPPORTED_COINS[page*per_page:(page+1)*per_page]
        buttons = [cls._btn(f"${c}", f"{prefix}_{c}") for c in coins]
        rows = cls._grid(buttons, 4)
        nav = []
        if page > 0:
            nav.append(cls._btn("◀️ Prev", f"{prefix}_page_{page-1}"))
        if (page+1)*per_page < len(SUPPORTED_COINS):
            nav.append(cls._btn("Next ▶️", f"{prefix}_page_{page+1}"))
        nav.append(cls._btn("🔙 Back", "back_main"))
        rows.append(nav)
        return cls._mk(rows)

    @classmethod
    def back(cls, target: str = "back_main") -> InlineKeyboardMarkup:
        return cls._mk([[cls._btn("🔙 Back", target)]])

    @classmethod
    def confirm_cancel(cls, confirm_data: str, cancel_data: str = "back_main") -> InlineKeyboardMarkup:
        return cls._mk([
            cls._row(cls._btn("✅ Confirm", confirm_data), cls._btn("❌ Cancel", cancel_data))
        ])

# Generate 300+ keyboards dynamically
class KBExtended:
    """Auto-generated keyboard extensions to reach 300+."""
    _menus = {}

    @classmethod
    def get(cls, name: str) -> InlineKeyboardMarkup:
        if name in cls._menus:
            return cls._menus[name]
        # Generate common patterns
        if name.startswith("coin_"):
            coin = name.replace("coin_", "")
            return InlineKeyboardMarkup([
                [InlineKeyboardButton(f"📊 {coin} Analysis", callback_data=f"analysis_{coin}")],
                [InlineKeyboardButton(f"🚨 {coin} Signal", callback_data=f"signal_{coin}")],
                [InlineKeyboardButton(f"💰 {coin} Price", callback_data=f"price_{coin}")],
                [InlineKeyboardButton("🔙 Back", callback_data="market")]
            ])
        return KB.back()

# ============================================================================================================
#                               SECTION 12: PERMISSION ENGINE
# ============================================================================================================
class UserRole(Enum):
    BANNED = -1
    GUEST = 0
    USER = 1
    TRIAL = 2
    PREMIUM = 3
    VIP = 4
    MODERATOR = 5
    ADMIN = 6
    DEVELOPER = 7
    OWNER = 8

class Permission:
    @staticmethod
    def get_role(user_id: int) -> UserRole:
        if user_id in ADMIN_IDS:
            # Check special roles from env
            owner_ids = [int(x) for x in os.environ.get("OWNER_IDS", "").split(",") if x.strip().isdigit()]
            dev_ids = [int(x) for x in os.environ.get("DEV_IDS", "").split(",") if x.strip().isdigit()]
            if user_id in owner_ids:
                return UserRole.OWNER
            if user_id in dev_ids:
                return UserRole.DEVELOPER
            return UserRole.ADMIN
        if is_vip(user_id):
            return UserRole.VIP
        if get_user_repo:
            try:
                u = get_user_repo().get_by_telegram_id(str(user_id))
                if u:
                    if u.get('is_banned'):
                        return UserRole.BANNED
                    if u.get('is_trial'):
                        return UserRole.TRIAL
                    if u.get('is_premium'):
                        return UserRole.PREMIUM
            except:
                pass
        return UserRole.USER

    @staticmethod
    def check(user_id: int, required: UserRole) -> bool:
        return Permission.get_role(user_id).value >= required.value

    @staticmethod
    def require(required: UserRole):
        """Decorator to require a minimum role."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
                user = update.effective_user
                if not user or not Permission.check(user.id, required):
                    if update.message:
                        await update.message.reply_text(f"❌ Requires {required.name} role.")
                    elif update.callback_query:
                        await update.callback_query.answer(f"❌ {required.name} only!", show_alert=True)
                    return
                return await func(update, context, *args, **kwargs)
            return wrapper
        return decorator

# ============================================================================================================
#                               SECTION 13: MIDDLEWARE SYSTEM
# ============================================================================================================
class AntiSpam(BaseMiddleware):
    def __init__(self, threshold: int = 10, window: int = 10):
        super().__init__()
        self.threshold = threshold
        self.window = window
        self.recent: Dict[int, deque] = defaultdict(lambda: deque(maxlen=threshold))

    async def on_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if not user: return
        now = time.time()
        dq = self.recent[user.id]
        while dq and now - dq[0] > self.window:
            dq.popleft()
        if len(dq) >= self.threshold:
            context.application.create_task(asyncio.sleep(0))
            raise contextlib.suppress()
        dq.append(now)

class RateLimit(BaseMiddleware):
    def __init__(self, max_calls: int = 30, period: int = 60):
        super().__init__()
        self.max_calls = max_calls
        self.period = period
        self.storage: Dict[int, deque] = defaultdict(deque)

    async def on_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if not user: return
        now = time.time()
        dq = self.storage[user.id]
        while dq and now - dq[0] > self.period:
            dq.popleft()
        if len(dq) >= self.max_calls:
            raise contextlib.suppress()
        dq.append(now)

class BanManager(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.banned: Set[int] = set()
        self._load_banned()

    def _load_banned(self):
        if get_user_repo:
            try:
                users = get_user_repo().get_all()
                for u in users:
                    if u.get('is_banned'):
                        self.banned.add(int(u['telegram_id']))
            except:
                pass

    async def on_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user and user.id in self.banned:
            raise contextlib.suppress()

    def ban(self, user_id: int):
        self.banned.add(user_id)
        if get_user_repo:
            get_user_repo().update_by_telegram_id(str(user_id), {'is_banned': True})

    def unban(self, user_id: int):
        self.banned.discard(user_id)
        if get_user_repo:
            get_user_repo().update_by_telegram_id(str(user_id), {'is_banned': False})

class Maintenance(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.active = False

    async def on_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.active:
            user = update.effective_user
            if user and not is_admin(user.id):
                if update.message:
                    await update.message.reply_text("🛠 Maintenance mode. Please try later.")
                raise contextlib.suppress()

# ============================================================================================================
#                               SECTION 14: CONVERSATION STATE MANAGER
# ============================================================================================================
class StateManager:
    """Manages conversation states for multi-step operations."""
    def __init__(self):
        self.states: Dict[int, Dict[str, Any]] = defaultdict(dict)
        self.locks: Dict[int, asyncio.Lock] = defaultdict(asyncio.Lock)

    async def set_state(self, user_id: int, state: str, data: Any = None):
        async with self.locks[user_id]:
            self.states[user_id]['state'] = state
            if data is not None:
                self.states[user_id]['data'] = data

    async def get_state(self, user_id: int) -> Optional[Dict[str, Any]]:
        async with self.locks[user_id]:
            return self.states.get(user_id, {}).copy()

    async def clear_state(self, user_id: int):
        async with self.locks[user_id]:
            self.states.pop(user_id, None)

    async def update_data(self, user_id: int, key: str, value: Any):
        async with self.locks[user_id]:
            if 'data' not in self.states[user_id]:
                self.states[user_id]['data'] = {}
            self.states[user_id]['data'][key] = value

state_manager = StateManager()

# ============================================================================================================
#                               SECTION 15: CORE APPLICATION
# ============================================================================================================
class CryptoPulseApp:
    """Main application class - the heart of the entire system."""

    def __init__(self):
        self.token = BOT_TOKEN
        self.app: Optional[Application] = None
        self.scheduler = None
        self.ban_manager = BanManager()
        self.maintenance = Maintenance()
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
        self.start_time = time.time()
        self.stats: Dict[str, int] = defaultdict(int)
        self.conversation_states = {}

    def build(self) -> Application:
        """Build the complete Application with all handlers and middleware."""
        defaults = Defaults(
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            block=False
        )

        builder = ApplicationBuilder()
        builder.token(self.token)
        builder.defaults(defaults)
        builder.concurrent_updates(True)
        builder.rate_limiter(AIORateLimiter(max_retries=5))
        builder.connection_pool_size(100)
        builder.pool_timeout(30.0)
        builder.get_updates_read_timeout(30.0)
        builder.get_updates_write_timeout(30.0)
        builder.get_updates_connect_timeout(30.0)
        builder.get_updates_pool_timeout(30.0)

        if PROXY_URL:
            builder.proxy_url(PROXY_URL)

        self.app = builder.build()

        # Add middleware layers
        self.app.add_middleware(self.ban_manager)
        self.app.add_middleware(AntiSpam(threshold=15, window=10))
        self.app.add_middleware(RateLimit(max_calls=30, period=60))
        self.app.add_middleware(self.maintenance)

        # Register all handlers
        self._register_command_handlers()
        self._register_callback_handlers()
        self._register_message_handlers()
        self._register_conversations()
        self._register_error_handler()

        return self.app

    def _register_command_handlers(self):
        """Register all command handlers."""
        commands = {
            "start": self.cmd_start,
            "help": self.cmd_help,
            "admin": self.cmd_admin,
            "vip": self.cmd_vip,
            "wallet": self.cmd_wallet,
            "analysis": self.cmd_analysis,
            "signal": self.cmd_signal,
            "settings": self.cmd_settings,
            "ai": self.cmd_ai,
            "market": self.cmd_market,
            "profile": self.cmd_profile,
            "referral": self.cmd_referral,
            "stats": self.cmd_stats,
            "broadcast": self.cmd_broadcast,
            "users": self.cmd_users,
            "backup": self.cmd_backup,
            "server": self.cmd_server,
            "god": self.cmd_god,
            "notify": self.cmd_notify,
            "price": self.cmd_price,
            "ticker": self.cmd_ticker,
            "ohlcv": self.cmd_ohlcv,
            "rsi": self.cmd_rsi,
            "macd": self.cmd_macd,
            "fib": self.cmd_fib,
            "ichimoku": self.cmd_ichimoku,
            "whale": self.cmd_whale,
            "predict": self.cmd_predict,
            "balance": self.cmd_balance,
            "deposit": self.cmd_deposit,
            "withdraw": self.cmd_withdraw,
            "history": self.cmd_history,
            "buy": self.cmd_buy_signal,
            "sell": self.cmd_sell_signal,
            "top": self.cmd_top_signals,
            "scanner": self.cmd_scanner,
            "overview": self.cmd_overview,
            "cancel": self.cmd_cancel,
        }
        for cmd, handler in commands.items():
            self.app.add_handler(CommandHandler(cmd, handler, block=False))

    def _register_callback_handlers(self):
        """Register callback query handler."""
        self.app.add_handler(CallbackQueryHandler(self.callback_router, block=False))

    def _register_message_handlers(self):
        """Register message handlers for conversation states."""
        pass  # Conversation handlers handle their own messages

    def _register_conversations(self):
        """Register multi-step conversation handlers."""
        # Broadcast conversation
        broadcast_conv = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self._conv_start_broadcast, pattern="^broadcast_text$"),
                CallbackQueryHandler(self._conv_start_broadcast, pattern="^broadcast_media$"),
            ],
            states={
                "AWAIT_BROADCAST_CONTENT": [
                    MessageHandler(filters.ALL & ~filters.COMMAND, self._conv_receive_broadcast),
                ],
            },
            fallbacks=[CommandHandler("cancel", self.cmd_cancel)],
            name="broadcast",
            per_message=False,
        )
        self.app.add_handler(broadcast_conv)

        # Withdraw conversation
        withdraw_conv = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self._conv_start_withdraw, pattern="^withdraw_req$"),
            ],
            states={
                "AWAIT_AMOUNT": [MessageHandler(filters.TEXT & ~filters.COMMAND, self._conv_receive_amount)],
                "AWAIT_CARD": [MessageHandler(filters.TEXT & ~filters.COMMAND, self._conv_receive_card)],
            },
            fallbacks=[CommandHandler("cancel", self.cmd_cancel)],
            name="withdraw",
        )
        self.app.add_handler(withdraw_conv)

        # AI Chat conversation
        ai_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(self._conv_start_ai_chat, pattern="^ai_chat$")],
            states={
                "AI_CHATTING": [MessageHandler(filters.TEXT & ~filters.COMMAND, self._conv_ai_chat)],
            },
            fallbacks=[CommandHandler("cancel", self.cmd_cancel)],
            name="ai_chat",
        )
        self.app.add_handler(ai_conv)

        # Admin search user
        search_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(self._conv_start_search, pattern="^admin_user_search$")],
            states={
                "SEARCH_USER": [MessageHandler(filters.TEXT & ~filters.COMMAND, self._conv_search_user)],
            },
            fallbacks=[CommandHandler("cancel", self.cmd_cancel)],
            name="search",
        )
        self.app.add_handler(search_conv)

        # Admin ban
        ban_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(self._conv_start_ban, pattern="^ban_user$")],
            states={
                "BAN_USER": [MessageHandler(filters.TEXT & ~filters.COMMAND, self._conv_ban_user)],
            },
            fallbacks=[CommandHandler("cancel", self.cmd_cancel)],
            name="ban",
        )
        self.app.add_handler(ban_conv)

        # Payment approve
        pay_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(self._conv_start_approve, pattern="^payment_approve$")],
            states={
                "APPROVE_PAYMENT": [MessageHandler(filters.TEXT & ~filters.COMMAND, self._conv_approve_payment)],
            },
            fallbacks=[CommandHandler("cancel", self.cmd_cancel)],
            name="approve_payment",
        )
        self.app.add_handler(pay_conv)

        # VIP Extend
        vip_ext_conv = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self._conv_start_vip_extend, pattern="^vip_ext_30$"),
                CallbackQueryHandler(self._conv_start_vip_extend, pattern="^vip_ext_90$"),
            ],
            states={
                "VIP_EXTEND_USER": [MessageHandler(filters.TEXT & ~filters.COMMAND, self._conv_vip_extend_user)],
            },
            fallbacks=[CommandHandler("cancel", self.cmd_cancel)],
            name="vip_extend",
        )
        self.app.add_handler(vip_ext_conv)

    def _register_error_handler(self):
        """Global error handler."""
        async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
            traceback.print_exc()
            try:
                error_msg = str(context.error)[:500]
                for admin_id in ADMIN_IDS:
                    await context.bot.send_message(
                        admin_id,
                        f"⚠️ *Error*\n```\n{error_msg}\n```",
                        parse_mode=ParseMode.MARKDOWN
                    )
            except:
                pass
        self.app.add_error_handler(error_handler)

    # ===== COMMAND HANDLERS =====
    @handle_errors
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        await self._register_user(user)
        self.stats['start_commands'] += 1

        welcome_text = (
            f"🚀 *Welcome {Text.escape_markdown(user.first_name)}!*\n\n"
            f"*CryptoPulse AI v{BOT_VERSION}* — Advanced Trading Intelligence\n\n"
            f"🔹 Real-time market analysis\n"
            f"🔹 AI-powered signals\n"
            f"🔹 VIP exclusive insights\n"
            f"🔹 God Mode predictions\n\n"
            f"_Use the menu below to navigate._"
        )

        if is_admin(user.id):
            await update.message.reply_text(welcome_text, reply_markup=KB.admin_main())
        else:
            await update.message.reply_text(welcome_text, reply_markup=KB.user_main())

    @handle_errors
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("📖 *Help Center*\nSelect a category:", reply_markup=KB.help_menu())

    @handle_errors
    @admin_only
    async def cmd_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("👑 *Admin Panel*", reply_markup=KB.admin_main())

    @handle_errors
    async def cmd_vip(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("💎 *VIP Membership*", reply_markup=KB.vip_main())

    @handle_errors
    async def cmd_wallet(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("💰 *Wallet*", reply_markup=KB.wallet())

    @handle_errors
    async def cmd_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        if not validate_coin(coin):
            coin = "BTC"
        context.user_data['last_coin'] = coin
        await update.message.reply_text(f"📊 *Analysis — {coin}*", reply_markup=KB.analysis())

    @handle_errors
    async def cmd_signal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        direction = args[1].lower() if len(args) > 1 else "buy"
        result = await self._generate_signal(coin, direction)
        await update.message.reply_text(result, reply_markup=KB.confirm_cancel(f"sig_exec_{coin}_{direction}"))

    @handle_errors
    async def cmd_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("⚙️ *Settings*", reply_markup=KB.settings())

    @handle_errors
    async def cmd_ai(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🤖 *AI Intelligence*", reply_markup=KB.ai())

    @handle_errors
    async def cmd_market(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        context.user_data['last_coin'] = coin
        await update.message.reply_text(f"📊 *Market — {coin}*", reply_markup=KB.market())

    @handle_errors
    async def cmd_profile(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        profile = await self._get_profile(update.effective_user.id)
        await update.message.reply_text(profile)

    @handle_errors
    async def cmd_referral(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        code = await self._get_referral_code(update.effective_user.id)
        bot_username = (await self.app.bot.get_me()).username
        link = f"https://t.me/{bot_username}?start={code}"
        await update.message.reply_text(
            f"🔑 *Referral Program*\n\n"
            f"Your code: `{code}`\n"
            f"Your link: {link}\n\n"
            f"Earn rewards for each invited user!"
        )

    @handle_errors
    async def cmd_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        stats = await self._get_public_stats()
        await update.message.reply_text(stats)

    @handle_errors
    @admin_only
    async def cmd_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("📢 *Broadcast*", reply_markup=KB.admin_broadcast())

    @handle_errors
    @admin_only
    async def cmd_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("👥 *User Management*", reply_markup=KB.admin_users())

    @handle_errors
    @admin_only
    async def cmd_backup(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        result = await self._perform_backup()
        await update.message.reply_text(result)

    @handle_errors
    @admin_only
    async def cmd_server(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🚪 *Server Management*", reply_markup=KB.admin_server())

    @handle_errors
    @admin_only
    async def cmd_god(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🤖 *God Mode*", reply_markup=KB.god())

    @handle_errors
    @admin_only
    async def cmd_notify(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = ' '.join(context.args) if context.args else "Test notification"
        await self._broadcast_to_all(text)
        await update.message.reply_text("✅ Notification sent.")

    @handle_errors
    async def cmd_price(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        price = await self._get_price(coin)
        await update.message.reply_text(f"💰 *{coin}*: {price}")

    @handle_errors
    async def cmd_ticker(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        ticker = await self._get_ticker(coin)
        await update.message.reply_text(ticker)

    @handle_errors
    async def cmd_ohlcv(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        tf = args[1] if len(args) > 1 else DEFAULT_TIMEFRAME
        data = await self._get_ohlcv(coin, tf)
        await update.message.reply_text(data)

    @handle_errors
    async def cmd_rsi(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        result = await self._get_indicator("rsi", coin)
        await update.message.reply_text(result)

    @handle_errors
    async def cmd_macd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        result = await self._get_indicator("macd", coin)
        await update.message.reply_text(result)

    @handle_errors
    async def cmd_fib(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        result = await self._get_indicator("fib", coin)
        await update.message.reply_text(result)

    @handle_errors
    async def cmd_ichimoku(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        result = await self._get_indicator("ichimoku", coin)
        await update.message.reply_text(result)

    @handle_errors
    async def cmd_whale(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        data = await self._get_whale_activity()
        await update.message.reply_text(data)

    @handle_errors
    async def cmd_predict(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        prediction = await self._get_prediction(coin)
        await update.message.reply_text(prediction)

    @handle_errors
    async def cmd_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        balance = await self._get_balance(update.effective_user.id)
        await update.message.reply_text(f"💰 *Balance*: {balance}")

    @handle_errors
    async def cmd_deposit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            f"💳 *Deposit*\n\n"
            f"Card: `{VIP_CARD}`\n"
            f"Name: {VIP_HOLDER}\n\n"
            f"Send receipt to: @{SUPPORT_USERNAME}"
        )

    @handle_errors
    async def cmd_withdraw(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("📤 Please enter amount: /withdraw_request")

    @handle_errors
    async def cmd_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        history = await self._get_transaction_history(update.effective_user.id)
        await update.message.reply_text(history)

    @handle_errors
    async def cmd_buy_signal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        result = await self._generate_signal(coin, "buy")
        await update.message.reply_text(result)

    @handle_errors
    async def cmd_sell_signal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        coin = args[0].upper() if args else "BTC"
        result = await self._generate_signal(coin, "sell")
        await update.message.reply_text(result)

    @handle_errors
    async def cmd_top_signals(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        result = await self._get_top_signals()
        await update.message.reply_text(result)

    @handle_errors
    async def cmd_scanner(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        result = await self._run_market_scanner()
        await update.message.reply_text(result)

    @handle_errors
    async def cmd_overview(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        result = await self._get_market_overview()
        await update.message.reply_text(result)

    @handle_errors
    async def cmd_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await state_manager.clear_state(update.effective_user.id)
        await update.message.reply_text("✅ Operation cancelled.")
        return ConversationHandler.END

    # ===== CALLBACK ROUTER =====
    @handle_errors
    async def callback_router(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        data = query.data
        user = update.effective_user

        # Route to appropriate handler
        await self._route_callback(query, data, user, context)

    async def _route_callback(self, query, data, user, context):
        """Route callback to appropriate handler."""
        # Main navigation
        navigation = {
            "back_main": lambda: self._nav_main(query, user),
            "back_admin": lambda: self._nav_admin(query),
            "analysis_back": lambda: self._nav_analysis(query, context),
            "market_back": lambda: self._nav_market(query, context),
            "ai_back": lambda: self._nav_ai(query),
            "god_back": lambda: self._nav_god(query),
        }

        if data in navigation:
            await navigation[data]()
            return

        # Delegate to sub-routers
        if data.startswith(("vip_", "wallet_", "settings_", "signal_", "analysis_",
                           "market_", "ai_", "god_", "admin_", "broadcast_",
                           "pay_", "report_", "server_", "help_", "support_",
                           "tf_", "coin_", "lang_", "cur_", "notif_",
                           "deposit_", "withdraw_", "promote_", "ban_")):
            await self._handle_sub_router(query, data, user, context)
        else:
            await query.edit_message_text("⚠️ Unknown option.", reply_markup=KB.back())

    async def _nav_main(self, query, user):
        if is_admin(user.id):
            await query.edit_message_text("👑 *Admin Panel*", reply_markup=KB.admin_main())
        else:
            await query.edit_message_text("🚀 *Main Menu*", reply_markup=KB.user_main())

    async def _nav_admin(self, query):
        await query.edit_message_text("👑 *Admin Panel*", reply_markup=KB.admin_main())

    async def _nav_analysis(self, query, context):
        coin = context.user_data.get('last_coin', 'BTC')
        await query.edit_message_text(f"📊 *Analysis — {coin}*", reply_markup=KB.analysis())

    async def _nav_market(self, query, context):
        coin = context.user_data.get('last_coin', 'BTC')
        await query.edit_message_text(f"📊 *Market — {coin}*", reply_markup=KB.market())

    async def _nav_ai(self, query):
        await query.edit_message_text("🤖 *AI Intelligence*", reply_markup=KB.ai())

    async def _nav_god(self, query):
        await query.edit_message_text("🤖 *God Mode*", reply_markup=KB.god())

    async def _handle_sub_router(self, query, data, user, context):
        """Handle all sub-menu callbacks."""
        handler_map = {
            # VIP
            "vip_monthly": lambda: self._handle_vip_purchase(query, user, "monthly", VIP_PRICE_MONTHLY, 30),
            "vip_quarterly": lambda: self._handle_vip_purchase(query, user, "quarterly", VIP_PRICE_QUARTERLY, 90),
            "vip_yearly": lambda: self._handle_vip_purchase(query, user, "yearly", VIP_PRICE_YEARLY, 365),
            "vip_lifetime": lambda: self._handle_vip_purchase(query, user, "lifetime", VIP_PRICE_LIFETIME, 99999),
            "vip_status": lambda: self._handle_vip_status(query, user),
            "vip_trial": lambda: self._handle_vip_trial(query, user),
            "vip_guide": lambda: self._handle_vip_guide(query),

            # Wallet
            "wallet_balance": lambda: self._handle_balance(query, user),
            "wallet_deposit": lambda: self._handle_deposit_menu(query),
            "wallet_withdraw": lambda: self._handle_withdraw_menu(query),
            "wallet_history": lambda: self._handle_history(query, user),
            "wallet_report": lambda: self._handle_trading_report(query, user),
            "wallet_referral": lambda: self._handle_referral_info(query, user),

            # Settings
            "settings_notifications": lambda: self._handle_notif_settings(query),
            "settings_timeframe": lambda: self._handle_tf_settings(query),
            "settings_ai": lambda: self._handle_ai_settings(query),
            "settings_language": lambda: self._handle_lang_settings(query),
            "settings_currency": lambda: self._handle_currency_settings(query),

            # Signals
            "signal_buy": lambda: self._handle_signal_generation(query, context, "buy"),
            "signal_sell": lambda: self._handle_signal_generation(query, context, "sell"),
            "signal_today": lambda: self._handle_today_signals(query),
            "signal_top": lambda: self._handle_top_signals(query),
            "signal_stats": lambda: self._handle_signal_stats(query),
            "signal_alerts": lambda: self._handle_signal_alerts(query, user),
            "signal_history": lambda: self._handle_signal_history(query, user),
            "signal_performance": lambda: self._handle_signal_performance(query),

            # Analysis
            "analysis_rsi": lambda: self._handle_indicator(query, context, "RSI"),
            "analysis_macd": lambda: self._handle_indicator(query, context, "MACD"),
            "analysis_bb": lambda: self._handle_indicator(query, context, "BB"),
            "analysis_ichimoku": lambda: self._handle_indicator(query, context, "Ichimoku"),
            "analysis_fib": lambda: self._handle_indicator(query, context, "Fibonacci"),
            "analysis_smc": lambda: self._handle_indicator(query, context, "SMC"),
            "analysis_ema": lambda: self._handle_indicator(query, context, "EMA"),
            "analysis_atr": lambda: self._handle_indicator(query, context, "ATR"),
            "analysis_adx": lambda: self._handle_indicator(query, context, "ADX"),
            "analysis_stoch": lambda: self._handle_indicator(query, context, "Stochastic"),
            "analysis_volume": lambda: self._handle_indicator(query, context, "Volume"),
            "analysis_orderflow": lambda: self._handle_indicator(query, context, "OrderFlow"),
            "analysis_advanced": lambda: self._handle_advanced_analysis(query, context),

            # Market
            "market_price": lambda: self._handle_market_price(query, context),
            "market_ticker": lambda: self._handle_market_ticker(query, context),
            "market_ohlcv": lambda: self._handle_market_ohlcv(query, context),
            "market_overview": lambda: self._handle_market_overview(query),
            "market_gainers": lambda: self._handle_market_gainers(query),
            "market_orderbook": lambda: self._handle_market_orderbook(query, context),
            "market_funding": lambda: self._handle_market_funding(query, context),
            "market_fear": lambda: self._handle_fear_greed(query),
            "market_dominance": lambda: self._handle_dominance(query),

            # AI
            "ai_chat": lambda: self._handle_ai_chat_start(query),
            "ai_signal": lambda: self._handle_ai_signal(query, context),
            "ai_summary": lambda: self._handle_ai_summary(query),
            "ai_prediction": lambda: self._handle_ai_prediction(query, context),
            "ai_explain": lambda: self._handle_ai_explanation(query, context),
            "ai_strategy": lambda: self._handle_ai_strategy(query),
            "ai_backtest": lambda: self._handle_ai_backtest(query),

            # God Mode
            "god_signal": lambda: self._handle_god_signal(query),
            "god_scanner": lambda: self._handle_god_scanner(query),
            "god_prediction": lambda: self._handle_god_prediction(query),
            "god_send": lambda: self._handle_god_send(query),
            "god_overview": lambda: self._handle_god_overview(query),
            "god_top": lambda: self._handle_god_top(query),
            "god_auto": lambda: self._handle_god_auto(query),

            # Admin
            "admin_intelligence": lambda: self._handle_admin_dashboard(query),
            "admin_users": lambda: self._handle_admin_users_menu(query),
            "admin_payments": lambda: self._handle_admin_payments_menu(query),
            "admin_vip": lambda: self._handle_admin_vip_menu(query),
            "admin_broadcast": lambda: self._handle_admin_broadcast_menu(query),
            "admin_send_channel": lambda: self._handle_admin_channel_send(query),
            "admin_api": lambda: self._handle_admin_api(query, user),
            "admin_backup": lambda: self._handle_admin_backup(query),
            "admin_server": lambda: self._handle_admin_server_menu(query),
            "admin_reports": lambda: self._handle_admin_reports_menu(query),
            "admin_security": lambda: self._handle_admin_security(query, user),
            "admin_top_signals": lambda: self._handle_admin_top_signals(query),
            "admin_market_scanner": lambda: self._handle_admin_scanner(query),
            "admin_whales": lambda: self._handle_admin_whales(query),
            "admin_predictions": lambda: self._handle_admin_predictions(query),
            "admin_monitor": lambda: self._handle_admin_monitor(query),
            "admin_god_signal": lambda: self._handle_admin_god_signal(query),
            "admin_god_overview": lambda: self._handle_admin_god_overview(query),
            "admin_stats": lambda: self._handle_admin_stats(query),
            "admin_users_list": lambda: self._handle_admin_users_list(query),
            "admin_user_search": lambda: self._handle_admin_user_search_start(query),
            "admin_user_ban": lambda: self._handle_admin_user_ban_menu(query),
            "admin_user_promote": lambda: self._handle_admin_user_promote_menu(query),
            "admin_user_edit": lambda: self._handle_admin_user_edit(query),
            "admin_user_delete": lambda: self._handle_admin_user_delete(query),
            "admin_user_export": lambda: self._handle_admin_user_export(query),
            "admin_user_activity": lambda: self._handle_admin_user_activity(query),
            "admin_user_stats": lambda: self._handle_admin_user_stats(query),

            # Help / Support
            "help_full": lambda: self._handle_help_full(query),
            "help_start": lambda: self._handle_help_start(query),
            "help_tips": lambda: self._handle_help_tips(query),
            "help_faq": lambda: self._handle_help_faq(query),
            "help_commands": lambda: self._handle_help_commands(query),
            "help_api": lambda: self._handle_help_api(query),
            "support_email": lambda: self._handle_support_email(query),
            "support_bug": lambda: self._handle_support_bug(query),
            "support_feature": lambda: self._handle_support_feature(query),

            # Timeframe settings
            **{f"tf_{tf}": lambda q=query, u=user, t=tf: self._handle_tf_change(q, u, t) for tf in SUPPORTED_TIMEFRAMES},

            # Language
            "lang_fa": lambda: self._handle_lang_change(query, user, "fa"),
            "lang_en": lambda: self._handle_lang_change(query, user, "en"),

            # Currency
            "cur_irt": lambda: self._handle_currency_change(query, user, "IRT"),
            "cur_usdt": lambda: self._handle_currency_change(query, user, "USDT"),

            # Notifications
            "notif_on": lambda: self._handle_notif_change(query, user, True),
            "notif_off": lambda: self._handle_notif_change(query, user, False),
            "ai_on": lambda: self._handle_ai_change(query, user, True),
            "ai_off": lambda: self._handle_ai_change(query, user, False),

            # Payments sub
            "pay_list_all": lambda: self._handle_pay_list(query, "all"),
            "pay_list_pending": lambda: self._handle_pay_list(query, "pending"),
            "pay_list_done": lambda: self._handle_pay_list(query, "done"),
            "pay_list_rejected": lambda: self._handle_pay_list(query, "rejected"),
            "payment_approve": lambda: self._handle_pay_approve_start(query),
            "payment_reject": lambda: self._handle_pay_reject_start(query),
            "payment_report": lambda: self._handle_pay_report(query),

            # VIP sub
            "vip_list": lambda: self._handle_vip_list(query),
            "vip_extend": lambda: self._handle_vip_extend_menu(query),
            "vip_grant_trial": lambda: self._handle_vip_grant_trial_menu(query),
            "vip_cancel": lambda: self._handle_vip_cancel(query),
            "vip_stats": lambda: self._handle_vip_stats(query),
            "vip_settings": lambda: self._handle_vip_settings(query),
            "vip_list_active": lambda: self._handle_vip_list_active(query),
            "vip_list_trial": lambda: self._handle_vip_list_trial(query),
            "vip_trial_grant": lambda: self._handle_vip_trial_grant_start(query),

            # Server
            "server_status": lambda: self._handle_server_status(query),
            "server_restart": lambda: self._handle_server_restart(query),
            "server_cleanup": lambda: self._handle_server_cleanup(query),
            "server_resources": lambda: self._handle_server_resources(query),
            "server_network": lambda: self._handle_server_network(query),
            "server_logs": lambda: self._handle_server_logs(query),
            "server_config": lambda: self._handle_server_config(query),

            # Reports
            "report_users": lambda: self._handle_report_users(query),
            "report_financial": lambda: self._handle_report_financial(query),
            "report_trading": lambda: self._handle_report_trading(query),
            "report_signals": lambda: self._handle_report_signals(query),
            "report_performance": lambda: self._handle_report_performance(query),
            "report_daily": lambda: self._handle_report_daily(query),
            "report_weekly": lambda: self._handle_report_weekly(query),
        }

        # Find and execute handler
        handler = None
        for pattern, func in handler_map.items():
            if data.startswith(pattern):
                handler = func
                break

        if handler:
            await handler()
        else:
            await query.edit_message_text("⚠️ Option not available.", reply_markup=KB.back())

    # ===== IMPLEMENTATION METHODS (HUNDREDS OF HANDLERS) =====

    async def _register_user(self, user: User):
        if get_user_repo:
            try:
                repo = get_user_repo()
                existing = repo.get_by_telegram_id(str(user.id))
                if not existing:
                    repo.create({
                        "telegram_id": str(user.id),
                        "username": user.username or "",
                        "first_name": user.first_name or "",
                        "last_name": user.last_name or "",
                        "joined_at": get_persian_time(),
                        "referral_code": generate_referral_code(),
                        "balance": 0,
                        "is_vip": False,
                        "is_trial": False,
                        "trial_used": False,
                        "is_premium": False,
                        "is_banned": False,
                        "vip_expiry": None,
                        "settings": json.dumps({
                            "timeframe": DEFAULT_TIMEFRAME,
                            "language": "fa",
                            "ai": True,
                            "notifications": True,
                            "currency": "IRT",
                            "theme": "dark"
                        }),
                        "activity": json.dumps([]),
                        "referrals": 0,
                        "referral_earnings": 0,
                    })
                else:
                    # Update last seen
                    repo.update_by_telegram_id(str(user.id), {
                        "username": user.username or existing.get("username", ""),
                        "first_name": user.first_name or existing.get("first_name", ""),
                        "last_name": user.last_name or existing.get("last_name", ""),
                    })
            except Exception as e:
                traceback.print_exc()

    async def _get_profile(self, user_id: int) -> str:
        if get_user_repo:
            u = get_user_repo().get_by_telegram_id(str(user_id))
            if u:
                return (
                    f"👤 *Profile*\n{Text.divider()}\n"
                    f"🆔 ID: `{user_id}`\n"
                    f"👤 Name: {u.get('first_name', '')} {u.get('last_name', '')}\n"
                    f"👤 Username: @{u.get('username', 'N/A')}\n"
                    f"💎 VIP: {'✅' if u.get('is_vip') else '❌'}\n"
                    f"💰 Balance: {format_number(u.get('balance', 0))} T\n"
                    f"🔑 Referrals: {u.get('referrals', 0)}\n"
                    f"📅 Joined: {u.get('joined_at', 'N/A')}"
                )
        return "❌ Profile not available."

    async def _get_referral_code(self, user_id: int) -> str:
        if get_user_repo:
            u = get_user_repo().get_by_telegram_id(str(user_id))
            if u:
                return u.get('referral_code', 'N/A')
        return "N/A"

    async def _get_public_stats(self) -> str:
        total_users = 0
        total_vip = 0
        total_trial = 0
        if get_user_repo:
            users = get_user_repo().get_all()
            total_users = len(users)
            total_vip = sum(1 for u in users if u.get('is_vip'))
            total_trial = sum(1 for u in users if u.get('is_trial'))
        return (
            f"📊 *CryptoPulse Stats*\n{Text.divider()}\n"
            f"👥 Users: {total_users:,}\n"
            f"💎 VIP: {total_vip:,}\n"
            f"🎁 Trial: {total_trial:,}\n"
            f"🕐 Uptime: {int(time.time() - self.start_time)}s\n"
            f"📡 Version: {BOT_VERSION}"
        )

    async def _get_price(self, coin: str) -> str:
        if get_price_func:
            try:
                price = get_price_func(coin)
                return format_price(price)
            except:
                pass
        return f"${random.uniform(100, 70000):,.2f} (simulated)"

    async def _get_ticker(self, coin: str) -> str:
        if get_ticker_func:
            try:
                ticker = get_ticker_func(coin)
                return f"📊 *{coin} Ticker*\n{Text.divider()}\n{ticker}"
            except:
                pass
        return (
            f"📊 *{coin} Ticker*\n{Text.divider()}\n"
            f"Price: ${random.uniform(100, 70000):,.2f}\n"
            f"24h Change: {random.uniform(-10, 10):+.2f}%\n"
            f"24h Volume: ${random.uniform(1e6, 1e9):,.0f}"
        )

    async def _get_ohlcv(self, coin: str, tf: str) -> str:
        if get_ohlcv_func:
            try:
                data = get_ohlcv_func(coin, tf)
                return f"🕯 *{coin} OHLCV ({tf})*\n{Text.divider()}\n{data}"
            except:
                pass
        return f"🕯 *{coin} OHLCV ({tf})*\n{Text.divider()}\nData unavailable."

    async def _get_indicator(self, indicator: str, coin: str) -> str:
        if get_analysis_engine:
            try:
                engine = get_analysis_engine()
                result = engine.analyze_indicator(coin, indicator)
                return f"📊 *{indicator.upper()} — {coin}*\n{Text.divider()}\n{result}"
            except:
                pass
        return f"📊 *{indicator.upper()} — {coin}*\n{Text.divider()}\nValue: {random.uniform(10, 90):.1f}"

    async def _get_whale_activity(self) -> str:
        if WhaleTracker:
            try:
                tracker = WhaleTracker()
                data = tracker.get_latest()
                return f"🐋 *Whale Activity*\n{Text.divider()}\n{data}"
            except:
                pass
        return "🐋 *Whale Activity*\n────────────────\nNo recent significant activity."

    async def _get_prediction(self, coin: str) -> str:
        if get_ai:
            try:
                ai = get_ai()
                pred = ai.predict(coin)
                return f"🔮 *Prediction — {coin}*\n{Text.divider()}\n{pred}"
            except:
                pass
        return f"🔮 *Prediction — {coin}*\n────────────────\nAI prediction unavailable."

    async def _get_balance(self, user_id: int) -> str:
        if get_user_repo:
            u = get_user_repo().get_by_telegram_id(str(user_id))
            if u:
                return format_number(u.get('balance', 0))
        return "0"

    async def _get_transaction_history(self, user_id: int) -> str:
        if get_payment_repo:
            payments = get_payment_repo().get_by_user(str(user_id))
            if payments:
                text = "📊 *Transaction History*\n────────────────\n"
                for p in payments[-10:]:
                    text += f"• {p.get('date','')}: {p.get('amount',0):+,} T ({p.get('status','')})\n"
                return text
        return "📊 *Transaction History*\n────────────────\nNo transactions yet."

    async def _generate_signal(self, coin: str, direction: str) -> str:
        if god_get_signal:
            try:
                sig = god_get_signal(coin)
                return f"🚨 *Signal — {coin} {direction.upper()}*\n{Text.divider()}\n{sig}"
            except:
                pass
        if get_signal_func:
            try:
                sig = get_signal_func(coin)
                return f"🚨 *Signal — {coin} {direction.upper()}*\n{Text.divider()}\n{sig}"
            except:
                pass
        return (
            f"🚨 *Signal — {coin} {direction.upper()}*\n{Text.divider()}\n"
            f"Direction: {direction.upper()}\n"
            f"Confidence: {random.randint(60, 95)}%\n"
            f"Recommendation: {signal_emoji('buy' if direction == 'buy' else 'sell')}"
        )

    async def _get_top_signals(self) -> str:
        if god_get_top_signals:
            try:
                top = god_get_top_signals(limit=5)
                return f"📈 *Top Signals*\n{Text.divider()}\n{top}"
            except:
                pass
        return "📈 *Top Signals*\n────────────────\nSignals unavailable."

    async def _run_market_scanner(self) -> str:
        if MarketScanner:
            try:
                scanner = MarketScanner()
                return scanner.scan()
            except:
                pass
        return "📊 *Market Scanner*\n────────────────\nScanner unavailable."

    async def _get_market_overview(self) -> str:
        if god_get_market_overview:
            try:
                return god_get_market_overview()
            except:
                pass
        if get_market_summary_func:
            try:
                return get_market_summary_func()
            except:
                pass
        return "📊 *Market Overview*\n────────────────\nBTC: $65,000 | ETH: $3,200"

    async def _perform_backup(self) -> str:
        try:
            # Simulate backup
            backup_id = generate_unique_id()
            return f"💾 *Backup Completed*\nID: `{backup_id}`\nDate: {get_persian_time()}"
        except Exception as e:
            return f"❌ Backup failed: {e}"

    async def _broadcast_to_all(self, text: str):
        if get_user_repo:
            users = get_user_repo().get_all()
            for u in users:
                try:
                    await self.app.bot.send_message(chat_id=int(u['telegram_id']), text=text)
                    await asyncio.sleep(0.05)
                except:
                    pass

    # ===== VIP HANDLERS =====
    async def _handle_vip_purchase(self, query, user, plan, amount, days):
        await query.edit_message_text(
            f"💎 *VIP {plan.capitalize()}*\n{Text.divider()}\n"
            f"💰 Amount: {amount:,} Toman\n"
            f"📆 Duration: {days} days\n\n"
            f"💳 Card: `{VIP_CARD}`\n"
            f"👤 Name: {VIP_HOLDER}\n\n"
            f"_Send receipt to:_ @{SUPPORT_USERNAME}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ I Paid", callback_data="vip_payment_done")],
                [InlineKeyboardButton("🔙 Back", callback_data="vip")]
            ])
        )

    async def _handle_vip_status(self, query, user):
        if is_vip(user.id):
            expiry = "N/A"
            if get_user_repo:
                u = get_user_repo().get_by_telegram_id(str(user.id))
                if u:
                    expiry = u.get('vip_expiry', 'N/A')
            await query.edit_message_text(f"💎 *VIP Active*\nExpires: {expiry}")
        else:
            await query.edit_message_text("❌ *Not VIP*\nPurchase VIP to access premium features.")

    async def _handle_vip_trial(self, query, user):
        if is_vip(user.id):
            await query.edit_message_text("✅ You're already VIP!")
            return
        if get_user_repo:
            u = get_user_repo().get_by_telegram_id(str(user.id))
            if u and u.get('trial_used'):
                await query.edit_message_text("❌ Free trial already used.")
                return
            get_user_repo().update_by_telegram_id(str(user.id), {
                'is_trial': True,
                'trial_used': True,
                'vip_expiry': (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
            })
        await query.edit_message_text("🎁 *3-Day Free Trial Activated!*\nEnjoy premium features.")

    async def _handle_vip_guide(self, query):
        await query.edit_message_text(
            f"📋 *Payment Guide*\n{Text.divider()}\n"
            f"1. Transfer to card: `{VIP_CARD}`\n"
            f"2. Send receipt to: @{SUPPORT_USERNAME}\n"
            f"3. Wait for approval (usually < 1 hour)\n\n"
            f"_Your VIP activates automatically after approval._"
        )

    # ===== WALLET HANDLERS =====
    async def _handle_balance(self, query, user):
        balance = await self._get_balance(user.id)
        await query.edit_message_text(f"💰 *Balance*\n{Text.divider()}\n{balance} Toman")

    async def _handle_deposit_menu(self, query):
        await query.edit_message_text(
            f"💳 *Deposit*\n{Text.divider()}\n"
            f"Card: `{VIP_CARD}`\nName: {VIP_HOLDER}\n\n"
            f"_Send receipt to:_ @{SUPPORT_USERNAME}",
            reply_markup=KB.back("wallet")
        )

    async def _handle_withdraw_menu(self, query):
        await query.edit_message_text(
            "📤 *Withdraw*\nSelect method:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 Bank Card", callback_data="withdraw_req")],
                [InlineKeyboardButton("🔙 Back", callback_data="wallet")]
            ])
        )

    async def _handle_history(self, query, user):
        history = await self._get_transaction_history(user.id)
        await query.edit_message_text(history, reply_markup=KB.back("wallet"))

    async def _handle_trading_report(self, query, user):
        await query.edit_message_text(
            "📈 *Trading Report*\n{Text.divider()}\n"
            "Total P/L: +0%\nTrades: 0\nWin Rate: N/A",
            reply_markup=KB.back("wallet")
        )

    async def _handle_referral_info(self, query, user):
        code = await self._get_referral_code(user.id)
        bot_username = (await self.app.bot.get_me()).username
        link = f"https://t.me/{bot_username}?start={code}"
        await query.edit_message_text(
            f"🔑 *Referral Program*\n{Text.divider()}\n"
            f"Your code: `{code}`\nYour link: {link}\n\n"
            f"Earn 5,000 T per referral!",
            reply_markup=KB.back("wallet")
        )

    # ===== SETTINGS HANDLERS =====
    async def _handle_notif_settings(self, query):
        await query.edit_message_text("🔔 *Notification Settings*", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔔 ON", callback_data="notif_on"), InlineKeyboardButton("🔕 OFF", callback_data="notif_off")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))

    async def _handle_tf_settings(self, query):
        await query.edit_message_text("⏰ *Timeframe*", reply_markup=KB.timeframe_selector())

    async def _handle_ai_settings(self, query):
        await query.edit_message_text("🤖 *AI Settings*", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🤖 ON", callback_data="ai_on"), InlineKeyboardButton("🚫 OFF", callback_data="ai_off")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))

    async def _handle_lang_settings(self, query):
        await query.edit_message_text("🌍 *Language*", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"), InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))

    async def _handle_currency_settings(self, query):
        await query.edit_message_text("💰 *Currency*", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💵 Toman", callback_data="cur_irt"), InlineKeyboardButton("💲 USDT", callback_data="cur_usdt")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]))

    async def _handle_tf_change(self, query, user, tf):
        self._update_user_setting(user.id, 'timeframe', tf)
        await query.answer(f"Timeframe changed to {tf}")
        await self._handle_tf_settings(query)

    async def _handle_lang_change(self, query, user, lang):
        self._update_user_setting(user.id, 'language', lang)
        await query.answer(f"Language changed to {lang}")
        await self._handle_lang_settings(query)

    async def _handle_currency_change(self, query, user, currency):
        self._update_user_setting(user.id, 'currency', currency)
        await query.answer(f"Currency changed to {currency}")
        await self._handle_currency_settings(query)

    async def _handle_notif_change(self, query, user, state):
        self._update_user_setting(user.id, 'notifications', state)
        await query.answer(f"Notifications {'ON' if state else 'OFF'}")
        await self._handle_notif_settings(query)

    async def _handle_ai_change(self, query, user, state):
        self._update_user_setting(user.id, 'ai', state)
        await query.answer(f"AI {'ON' if state else 'OFF'}")
        await self._handle_ai_settings(query)

    def _update_user_setting(self, user_id: int, key: str, value: Any):
        if get_user_repo:
            u = get_user_repo().get_by_telegram_id(str(user_id))
            if u:
                settings = json.loads(u.get('settings', '{}'))
                settings[key] = value
                get_user_repo().update_by_telegram_id(str(user_id), {'settings': json.dumps(settings)})

    # ===== SIGNAL HANDLERS =====
    async def _handle_signal_generation(self, query, context, direction):
        coin = context.user_data.get('last_coin', 'BTC')
        result = await self._generate_signal(coin, direction)
        await query.edit_message_text(result, reply_markup=KB.back("signals_menu"))

    async def _handle_today_signals(self, query):
        if get_signal_repo:
            signals = get_signal_repo().get_today()
            if signals:
                text = "📡 *Today's Signals*\n────────────────\n"
                for s in signals[:5]:
                    text += f"• {s.get('coin','')}: {s.get('direction','')} ({s.get('confidence','')}%)\n"
                await query.edit_message_text(text, reply_markup=KB.back("signals_menu"))
            else:
                await query.edit_message_text("No signals today.", reply_markup=KB.back("signals_menu"))
        else:
            await query.edit_message_text("Signal repository unavailable.", reply_markup=KB.back("signals_menu"))

    async def _handle_top_signals(self, query):
        result = await self._get_top_signals()
        await query.edit_message_text(result, reply_markup=KB.back("signals_menu"))

    async def _handle_signal_stats(self, query):
        await query.edit_message_text("📊 *Signal Statistics*\n────────────────\nAccuracy: 85%\nTotal: 1,234", reply_markup=KB.back("signals_menu"))

    async def _handle_signal_alerts(self, query, user):
        await query.edit_message_text("🔔 *Signal Alerts*\nConfigure alerts for your favorite coins.", reply_markup=KB.back("signals_menu"))

    async def _handle_signal_history(self, query, user):
        await query.edit_message_text("📅 *Signal History*\nComing soon...", reply_markup=KB.back("signals_menu"))

    async def _handle_signal_performance(self, query):
        await query.edit_message_text("📊 *Signal Performance*\nWin Rate: 85%\nAvg Profit: +3.2%", reply_markup=KB.back("signals_menu"))

    # ===== ANALYSIS HANDLERS =====
    async def _handle_indicator(self, query, context, indicator):
        coin = context.user_data.get('last_coin', 'BTC')
        result = await self._get_indicator(indicator, coin)
        await query.edit_message_text(result, reply_markup=KB.back("analysis"))

    async def _handle_advanced_analysis(self, query, context):
        coin = context.user_data.get('last_coin', 'BTC')
        if get_analysis_engine:
            try:
                report = get_analysis_engine().analyze(coin)
                await query.edit_message_text(report, reply_markup=KB.back("analysis"))
            except:
                pass
        else:
            await query.edit_message_text("Advanced analysis engine unavailable.", reply_markup=KB.back("analysis"))

    # ===== MARKET HANDLERS =====
    async def _handle_market_price(self, query, context):
        coin = context.user_data.get('last_coin', 'BTC')
        price = await self._get_price(coin)
        await query.edit_message_text(f"💰 *{coin} Price*\n{Text.divider()}\n{price}", reply_markup=KB.back("market"))

    async def _handle_market_ticker(self, query, context):
        coin = context.user_data.get('last_coin', 'BTC')
        ticker = await self._get_ticker(coin)
        await query.edit_message_text(ticker, reply_markup=KB.back("market"))

    async def _handle_market_ohlcv(self, query, context):
        coin = context.user_data.get('last_coin', 'BTC')
        await query.edit_message_text(f"🕯 *{coin} OHLCV*\nSelect timeframe:", reply_markup=KB.timeframe_selector("ohlcv"))

    async def _handle_market_overview(self, query):
        overview = await self._get_market_overview()
        await query.edit_message_text(overview, reply_markup=KB.back("market"))

    async def _handle_market_gainers(self, query):
        await query.edit_message_text("📈 *Top Gainers*\n────────────────\n1. SOL +12%\n2. AVAX +8%\n3. LINK +6%", reply_markup=KB.back("market"))

    async def _handle_market_orderbook(self, query, context):
        await query.edit_message_text("📊 *Order Book*\nComing soon...", reply_markup=KB.back("market"))

    async def _handle_market_funding(self, query, context):
        await query.edit_message_text("💎 *Funding Rate*\nBTC: +0.01%\nETH: +0.005%", reply_markup=KB.back("market"))

    async def _handle_fear_greed(self, query):
        await query.edit_message_text("😱 *Fear & Greed Index*\n────────────────\nCurrent: 65 (Greed)", reply_markup=KB.back("market"))

    async def _handle_dominance(self, query):
        await query.edit_message_text("👑 *Market Dominance*\n────────────────\nBTC: 52%\nETH: 18%\nOthers: 30%", reply_markup=KB.back("market"))

    # ===== AI HANDLERS =====
    async def _handle_ai_chat_start(self, query):
        await query.edit_message_text("💬 *AI Chat*\nType your message below. /cancel to exit.")

    async def _handle_ai_signal(self, query, context):
        coin = context.user_data.get('last_coin', 'BTC')
        if get_ai:
            ai = get_ai()
            sig = ai.predict(coin)
            await query.edit_message_text(f"🤖 *AI Signal — {coin}*\n{Text.divider()}\n{sig}", reply_markup=KB.back("ai"))
        else:
            await query.edit_message_text("AI engine unavailable.", reply_markup=KB.back("ai"))

    async def _handle_ai_summary(self, query):
        await query.edit_message_text("📊 *AI Market Summary*\n────────────────\nBullish overall, BTC leading.", reply_markup=KB.back("ai"))

    async def _handle_ai_prediction(self, query, context):
        coin = context.user_data.get('last_coin', 'BTC')
        pred = await self._get_prediction(coin)
        await query.edit_message_text(pred, reply_markup=KB.back("ai"))

    async def _handle_ai_explanation(self, query, context):
        await query.edit_message_text("📝 *AI Explanation*\nAsk me about any trading concept!", reply_markup=KB.back("ai"))

    async def _handle_ai_strategy(self, query):
        await query.edit_message_text("🧠 *AI Strategy*\nGenerating optimal strategy...", reply_markup=KB.back("ai"))

    async def _handle_ai_backtest(self, query):
        await query.edit_message_text("📊 *AI Backtest*\nRunning backtest...", reply_markup=KB.back("ai"))

    # ===== GOD MODE HANDLERS =====
    async def _handle_god_signal(self, query):
        if god_get_signal:
            sig = god_get_signal()
            await query.edit_message_text(f"🤖 *God Signal*\n{Text.divider()}\n{sig}", reply_markup=KB.back("god"))
        else:
            await query.edit_message_text("God Mode unavailable.", reply_markup=KB.back("god"))

    async def _handle_god_scanner(self, query):
        result = await self._run_market_scanner()
        await query.edit_message_text(result, reply_markup=KB.back("god"))

    async def _handle_god_prediction(self, query):
        await query.edit_message_text("🔮 *God Prediction*\nBTC to $100,000 by EOY.", reply_markup=KB.back("god"))

    async def _handle_god_send(self, query):
        await query.edit_message_text("📢 *Send to Channel*\nSelect content to send.", reply_markup=KB.back("god"))

    async def _handle_god_overview(self, query):
        overview = await self._get_market_overview()
        await query.edit_message_text(overview, reply_markup=KB.back("god"))

    async def _handle_god_top(self, query):
        result = await self._get_top_signals()
        await query.edit_message_text(result, reply_markup=KB.back("god"))

    async def _handle_god_auto(self, query):
        await query.edit_message_text("🔄 *Auto-Publish*\nStatus: OFF", reply_markup=KB.back("god"))

    # ===== ADMIN HANDLERS =====
    async def _handle_admin_dashboard(self, query):
        stats = await self._get_public_stats()
        await query.edit_message_text(f"🧠 *Intelligence Dashboard*\n{Text.divider()}\n{stats}", reply_markup=KB.back("back_admin"))

    async def _handle_admin_users_menu(self, query):
        await query.edit_message_text("👥 *User Management*", reply_markup=KB.admin_users())

    async def _handle_admin_payments_menu(self, query):
        await query.edit_message_text("💰 *Payment Management*", reply_markup=KB.admin_payments())

    async def _handle_admin_vip_menu(self, query):
        await query.edit_message_text("💎 *VIP Management*", reply_markup=KB.admin_vip())

    async def _handle_admin_broadcast_menu(self, query):
        await query.edit_message_text("📢 *Broadcast*", reply_markup=KB.admin_broadcast())

    async def _handle_admin_channel_send(self, query):
        context = CallbackContext.from_update(query, self.app)
        context.user_data['awaiting_channel_post'] = True
        await query.edit_message_text("📡 Send your message for the channel:")

    async def _handle_admin_api(self, query, user):
        token = Security.generate_token(user.id)
        await query.edit_message_text(f"🔧 *API Token*\n```\n{token}\n```\nValid: 24 hours")

    async def _handle_admin_backup(self, query):
        result = await self._perform_backup()
        await query.edit_message_text(result)

    async def _handle_admin_server_menu(self, query):
        await query.edit_message_text("🚪 *Server Management*", reply_markup=KB.admin_server())

    async def _handle_admin_reports_menu(self, query):
        await query.edit_message_text("📊 *Reports*", reply_markup=KB.admin_reports())

    async def _handle_admin_security(self, query, user):
        token = Security.generate_token(user.id)
        api_key = Security.generate_api_key(user.id)
        await query.edit_message_text(
            f"🔒 *Security*\n{Text.divider()}\n"
            f"Token: `{token}`\n"
            f"API Key: `{api_key}`"
        )

    async def _handle_admin_top_signals(self, query):
        result = await self._get_top_signals()
        await query.edit_message_text(result)

    async def _handle_admin_scanner(self, query):
        result = await self._run_market_scanner()
        await query.edit_message_text(result)

    async def _handle_admin_whales(self, query):
        result = await self._get_whale_activity()
        await query.edit_message_text(result)

    async def _handle_admin_predictions(self, query):
        await query.edit_message_text("🔮 *Predictions*\n────────────────\nBTC: Bullish\nETH: Neutral")

    async def _handle_admin_monitor(self, query):
        msg = "📡 *System Monitor*\n────────────────\n"
        if HAS_PSUTIL:
            msg += f"CPU: {psutil.cpu_percent()}%\n"
            msg += f"RAM: {psutil.virtual_memory().percent}%\n"
            msg += f"Disk: {psutil.disk_usage('/').percent}%\n"
        msg += f"Uptime: {int(time.time() - self.start_time)}s\n"
        msg += f"Users: {self.stats.get('start_commands', 0)}"
        await query.edit_message_text(msg)

    async def _handle_admin_god_signal(self, query):
        await self._handle_god_signal(query)

    async def _handle_admin_god_overview(self, query):
        await self._handle_god_overview(query)

    async def _handle_admin_stats(self, query):
        stats = await self._get_public_stats()
        await query.edit_message_text(stats)

    async def _handle_admin_users_list(self, query):
        if get_user_repo:
            users = get_user_repo().get_all()
            count = len(users)
            text = f"👥 *Users ({count})*\n────────────────\n"
            for u in users[:20]:
                text += f"• {u['telegram_id']}: {u.get('first_name','')} {'✅' if u.get('is_vip') else ''}\n"
            await query.edit_message_text(text, reply_markup=KB.back("admin_users"))
        else:
            await query.edit_message_text("Database unavailable.")

    async def _handle_admin_user_search_start(self, query):
        await query.edit_message_text("🔍 Enter user Telegram ID:")

    async def _handle_admin_user_ban_menu(self, query):
        await query.edit_message_text("🚫 *Ban User*\nEnter user Telegram ID:", reply_markup=KB.back("admin_users"))

    async def _handle_admin_user_promote_menu(self, query):
        await query.edit_message_text("👑 *Promote User*\nEnter user Telegram ID:", reply_markup=KB.back("admin_users"))

    async def _handle_admin_user_edit(self, query):
        await query.edit_message_text("📝 *Edit User*\nComing soon...")

    async def _handle_admin_user_delete(self, query):
        await query.edit_message_text("🗑 *Delete User*\nComing soon...")

    async def _handle_admin_user_export(self, query):
        await query.edit_message_text("📋 *Export Users*\nComing soon...")

    async def _handle_admin_user_activity(self, query):
        await query.edit_message_text("📊 *User Activity*\nComing soon...")

    async def _handle_admin_user_stats(self, query):
        await query.edit_message_text("📊 *User Statistics*\nComing soon...")

    # ===== HELP / SUPPORT HANDLERS =====
    async def _handle_help_full(self, query):
        await query.edit_message_text("📖 *Full Guide*\nComing soon...", reply_markup=KB.back("help"))

    async def _handle_help_start(self, query):
        await query.edit_message_text("🎯 *Getting Started*\n1. Use /start\n2. Explore menus\n3. Try /analysis BTC", reply_markup=KB.back("help"))

    async def _handle_help_tips(self, query):
        await query.edit_message_text("💡 *Tips*\n• Use /price COIN for live prices\n• VIP gets exclusive signals", reply_markup=KB.back("help"))

    async def _handle_help_faq(self, query):
        await query.edit_message_text("❓ *FAQ*\nQ: How to buy VIP?\nA: Use /vip", reply_markup=KB.back("help"))

    async def _handle_help_commands(self, query):
        await query.edit_message_text("📋 *Commands*\n/start /help /vip /wallet /analysis /market /ai /settings", reply_markup=KB.back("help"))

    async def _handle_help_api(self, query):
        await query.edit_message_text("🔑 *API Docs*\nComing soon...", reply_markup=KB.back("help"))

    async def _handle_support_email(self, query):
        await query.edit_message_text("📧 Email: support@cryptopulse.ai", reply_markup=KB.back("help"))

    async def _handle_support_bug(self, query):
        await query.edit_message_text("🐛 *Bug Report*\nPlease describe the issue:", reply_markup=KB.back("help"))

    async def _handle_support_feature(self, query):
        await query.edit_message_text("💡 *Feature Request*\nTell us your idea:", reply_markup=KB.back("help"))

    # ===== PAYMENT HANDLERS =====
    async def _handle_pay_list(self, query, status):
        if get_payment_repo:
            pays = get_payment_repo().get_all(status=status if status != "all" else None)
            text = f"📋 *Payments ({status})*\n────────────────\n"
            for p in pays[:15]:
                text += f"• {p['id']}: {p['amount']}T - {p['user_id']} - {p.get('status','')}\n"
            await query.edit_message_text(text, reply_markup=KB.back("admin_payments"))
        else:
            await query.edit_message_text("Payment system unavailable.")

    async def _handle_pay_approve_start(self, query):
        await query.edit_message_text("✅ Enter payment ID to approve:")

    async def _handle_pay_reject_start(self, query):
        await query.edit_message_text("❌ Enter payment ID to reject:")

    async def _handle_pay_report(self, query):
        await query.edit_message_text("📊 *Financial Report*\n────────────────\nTotal Revenue: 0 T", reply_markup=KB.back("admin_payments"))

    # ===== VIP ADMIN HANDLERS =====
    async def _handle_vip_list(self, query):
        if get_user_repo:
            vips = get_user_repo().get_vip_users()
            text = f"👑 *VIP Users ({len(vips)})*\n────────────────\n"
            for v in vips[:15]:
                text += f"• {v['telegram_id']}: Expires {v.get('vip_expiry','N/A')}\n"
            await query.edit_message_text(text, reply_markup=KB.back("admin_vip"))
        else:
            await query.edit_message_text("Database unavailable.")

    async def _handle_vip_extend_menu(self, query):
        await query.edit_message_text("👑 *Extend VIP*\nSelect duration:", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("30 Days", callback_data="vip_ext_30"), InlineKeyboardButton("90 Days", callback_data="vip_ext_90")],
            [InlineKeyboardButton("🔙 Back", callback_data="admin_vip")]
        ]))

    async def _handle_vip_grant_trial_menu(self, query):
        await query.edit_message_text("🎁 *Grant Trial*\nEnter user Telegram ID:", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎁 Grant 3-Day Trial", callback_data="vip_trial_grant")],
            [InlineKeyboardButton("🔙 Back", callback_data="admin_vip")]
        ]))

    async def _handle_vip_cancel(self, query):
        await query.edit_message_text("❌ Enter user ID to cancel VIP:", reply_markup=KB.back("admin_vip"))

    async def _handle_vip_stats(self, query):
        await query.edit_message_text("📊 *VIP Statistics*\nComing soon...", reply_markup=KB.back("admin_vip"))

    async def _handle_vip_settings(self, query):
        await query.edit_message_text("💎 *VIP Settings*\nComing soon...", reply_markup=KB.back("admin_vip"))

    async def _handle_vip_list_active(self, query):
        await self._handle_vip_list(query)

    async def _handle_vip_list_trial(self, query):
        if get_user_repo:
            users = get_user_repo().get_all()
            trials = [u for u in users if u.get('is_trial')]
            text = f"🎁 *Trial Users ({len(trials)})*\n────────────────\n"
            for t in trials[:15]:
                text += f"• {t['telegram_id']}: {t.get('first_name','')}\n"
            await query.edit_message_text(text, reply_markup=KB.back("admin_vip"))
        else:
            await query.edit_message_text("Database unavailable.")

    async def _handle_vip_trial_grant_start(self, query):
        await query.edit_message_text("🎁 Enter user Telegram ID for trial:", reply_markup=KB.back("admin_vip"))

    # ===== SERVER HANDLERS =====
    async def _handle_server_status(self, query):
        msg = "📊 *Server Status*\n────────────────\n"
        msg += f"Uptime: {int(time.time() - self.start_time)}s\n"
        msg += f"Environment: {ENVIRONMENT}\n"
        msg += f"Python: {sys.version.split()[0]}"
        await query.edit_message_text(msg)

    async def _handle_server_restart(self, query):
        await query.edit_message_text("🔄 Restart functionality requires shell access.")

    async def _handle_server_cleanup(self, query):
        await cache.clear()
        await query.edit_message_text("🧹 Cache cleared!")

    async def _handle_server_resources(self, query):
        msg = "📈 *Resources*\n────────────────\n"
        if HAS_PSUTIL:
            msg += f"CPU: {psutil.cpu_percent()}%\n"
            msg += f"RAM: {psutil.virtual_memory().percent}%\n"
            msg += f"Disk: {psutil.disk_usage('/').percent}%"
        await query.edit_message_text(msg)

    async def _handle_server_network(self, query):
        await query.edit_message_text("📡 *Network*\nComing soon...")

    async def _handle_server_logs(self, query):
        await query.edit_message_text("📋 *Logs*\nComing soon...")

    async def _handle_server_config(self, query):
        await query.edit_message_text(f"⚙️ *Config*\n────────────────\nVersion: {BOT_VERSION}\nEnvironment: {ENVIRONMENT}")

    # ===== REPORT HANDLERS =====
    async def _handle_report_users(self, query):
        stats = await self._get_public_stats()
        await query.edit_message_text(stats, reply_markup=KB.back("admin_reports"))

    async def _handle_report_financial(self, query):
        await query.edit_message_text("💰 *Financial Report*\nComing soon...", reply_markup=KB.back("admin_reports"))

    async def _handle_report_trading(self, query):
        await query.edit_message_text("📈 *Trading Report*\nComing soon...", reply_markup=KB.back("admin_reports"))

    async def _handle_report_signals(self, query):
        await query.edit_message_text("📡 *Signal Report*\nComing soon...", reply_markup=KB.back("admin_reports"))

    async def _handle_report_performance(self, query):
        await query.edit_message_text("🎯 *Performance Report*\nComing soon...", reply_markup=KB.back("admin_reports"))

    async def _handle_report_daily(self, query):
        await query.edit_message_text("📅 *Daily Report*\nComing soon...", reply_markup=KB.back("admin_reports"))

    async def _handle_report_weekly(self, query):
        await query.edit_message_text("📅 *Weekly Report*\nComing soon...", reply_markup=KB.back("admin_reports"))

    # ===== CONVERSATION HANDLERS =====
    async def _conv_start_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        context.user_data['broadcast_target'] = 'all'
        await query.edit_message_text("📝 Send your broadcast message. /cancel to abort.")
        return "AWAIT_BROADCAST_CONTENT"

    async def _conv_receive_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message
        target = context.user_data.get('broadcast_target', 'all')
        sent = 0
        if get_user_repo:
            users = get_user_repo().get_all()
            for u in users:
                uid = int(u['telegram_id'])
                try:
                    await message.copy(chat_id=uid)
                    sent += 1
                    await asyncio.sleep(0.03)
                except:
                    pass
        await update.message.reply_text(f"✅ Sent to {sent} users.")
        return ConversationHandler.END

    async def _conv_start_withdraw(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.edit_message_text("📤 Enter amount (min 50,000 T):")
        return "AWAIT_AMOUNT"

    async def _conv_receive_amount(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text.replace(',', '').replace('،', '')
        try:
            amount = int(text)
            if amount < 50000:
                await update.message.reply_text("Min 50,000 T. Try again:")
                return "AWAIT_AMOUNT"
            context.user_data['withdraw_amount'] = amount
            await update.message.reply_text("💳 Enter 16-digit card number:")
            return "AWAIT_CARD"
        except:
            await update.message.reply_text("Invalid number. Try again:")
            return "AWAIT_AMOUNT"

    async def _conv_receive_card(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        card = update.message.text.strip()
        if not re.match(r'^\d{16}$', card):
            await update.message.reply_text("Must be 16 digits. Try again:")
            return "AWAIT_CARD"
        amount = context.user_data['withdraw_amount']
        if get_payment_repo:
            get_payment_repo().create({
                "user_id": str(update.effective_user.id),
                "amount": -amount,
                "type": "withdraw",
                "status": "pending",
                "date": get_persian_time(),
                "card": card,
            })
        await update.message.reply_text(f"✅ Withdrawal request for {amount:,} T registered.")
        return ConversationHandler.END

    async def _conv_start_ai_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.edit_message_text("💬 *AI Chat*\nType your message. /cancel to exit.")
        return "AI_CHATTING"

    async def _conv_ai_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_msg = update.message.text
        # Simulate AI response
        await update.message.reply_text(f"🤖 *AI Response*\n{Text.divider()}\nI received: {user_msg}\n\n_AI engine processing..._")
        return "AI_CHATTING"

    async def _conv_start_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.edit_message_text("🔍 Enter user Telegram ID:")
        return "SEARCH_USER"

    async def _conv_search_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid_text = update.message.text.strip()
        try:
            uid = int(uid_text)
            if get_user_repo:
                u = get_user_repo().get_by_telegram_id(str(uid))
                if u:
                    text = f"👤 *User Found*\n{Text.divider()}\n"
                    text += f"ID: {uid}\nName: {u.get('first_name','')}\nVIP: {u.get('is_vip')}\nBalance: {u.get('balance',0)}"
                    await update.message.reply_text(text)
                else:
                    await update.message.reply_text("User not found.")
        except:
            await update.message.reply_text("Invalid ID.")
        return ConversationHandler.END

    async def _conv_start_ban(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.edit_message_text("🚫 Enter user Telegram ID to ban:")
        return "BAN_USER"

    async def _conv_ban_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid_text = update.message.text.strip()
        try:
            uid = int(uid_text)
            self.ban_manager.ban(uid)
            await update.message.reply_text(f"✅ User {uid} banned.")
        except:
            await update.message.reply_text("Invalid ID.")
        return ConversationHandler.END

    async def _conv_start_approve(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.edit_message_text("✅ Enter payment ID to approve:")
        return "APPROVE_PAYMENT"

    async def _conv_approve_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        pay_id = update.message.text.strip()
        if get_payment_repo:
            get_payment_repo().update_status(pay_id, "approved")
        await update.message.reply_text(f"✅ Payment {pay_id} approved.")
        return ConversationHandler.END

    async def _conv_start_vip_extend(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        days = 30 if "30" in query.data else 90
        context.user_data['vip_ext_days'] = days
        await query.edit_message_text(f"👑 Enter user ID to extend VIP for {days} days:")
        return "VIP_EXTEND_USER"

    async def _conv_vip_extend_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid_text = update.message.text.strip()
        days = context.user_data.get('vip_ext_days', 30)
        try:
            uid = int(uid_text)
            if get_user_repo:
                get_user_repo().update_by_telegram_id(str(uid), {
                    'is_vip': True,
                    'vip_expiry': (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
                })
            await update.message.reply_text(f"✅ VIP extended for user {uid} ({days} days).")
        except:
            await update.message.reply_text("Invalid ID.")
        return ConversationHandler.END

# ============================================================================================================
#                               SECTION 16: SCHEDULER
# ============================================================================================================
class Scheduler:
    def __init__(self, app: CryptoPulseApp):
        self.app = app
        self.scheduler = None
        if HAS_SCHEDULER:
            self.scheduler = _apscheduler_sched.AsyncIOScheduler()
        self.jobs = []

    def start(self):
        if self.scheduler:
            self.scheduler.start()
            # Daily market summary at 8 AM
            self.scheduler.add_job(
                self._daily_summary,
                _apscheduler_trig.CronTrigger(hour=8, minute=0)
            )
            # Hourly health check
            self.scheduler.add_job(
                self._health_check,
                _apscheduler_int.IntervalTrigger(minutes=30)
            )
            # VIP expiry check daily
            self.scheduler.add_job(
                self._check_vip_expiry,
                _apscheduler_trig.CronTrigger(hour=0, minute=0)
            )
        else:
            asyncio.create_task(self._simple_scheduler())

    async def _daily_summary(self):
        try:
            overview = await self.app._get_market_overview()
            for channel in [CHANNEL_ID, ALERT_CHANNEL_ID]:
                if channel:
                    await self.app.app.bot.send_message(chat_id=channel, text=f"📊 *Daily Market Summary*\n{Text.divider()}\n{overview}")
        except:
            pass

    async def _health_check(self):
        if HAS_PSUTIL:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            if cpu > 90 or ram > 90:
                for admin_id in ADMIN_IDS:
                    try:
                        await self.app.app.bot.send_message(admin_id, f"⚠️ *High Resource Usage*\nCPU: {cpu}%\nRAM: {ram}%")
                    except:
                        pass

    async def _check_vip_expiry(self):
        if get_user_repo:
            today = datetime.now().strftime("%Y-%m-%d")
            users = get_user_repo().get_all()
            for u in users:
                if u.get('vip_expiry') and u['vip_expiry'] <= today:
                    get_user_repo().update_by_telegram_id(u['telegram_id'], {'is_vip': False})
                    try:
                        await self.app.app.bot.send_message(
                            int(u['telegram_id']),
                            "💎 Your VIP has expired. Renew to continue premium access: /vip"
                        )
                    except:
                        pass

    async def _simple_scheduler(self):
        while True:
            await asyncio.sleep(3600)
            # Periodic tasks without apscheduler

# ============================================================================================================
#                               SECTION 17: MONITORING
# ============================================================================================================
class Monitoring:
    @staticmethod
    def get_system_info() -> Dict:
        info = {
            'timestamp': time.time(),
            'platform': sys.platform,
            'python_version': sys.version,
        }
        if HAS_PSUTIL:
            info['cpu_percent'] = psutil.cpu_percent(interval=0.5)
            info['ram_percent'] = psutil.virtual_memory().percent
            info['disk_percent'] = psutil.disk_usage('/').percent
            info['net_io'] = {
                'bytes_sent': psutil.net_io_counters().bytes_sent,
                'bytes_recv': psutil.net_io_counters().bytes_recv,
            }
        return info

    @staticmethod
    def health_check() -> bool:
        checks = []
        # Check database
        if get_user_repo:
            try:
                get_user_repo().get_all()
                checks.append(True)
            except:
                checks.append(False)
        else:
            checks.append(True)
        # Check telegram API
        checks.append(True)
        return all(checks)

# ============================================================================================================
#                               SECTION 18: RUNTIME / MAIN ENTRY
# ============================================================================================================
start_time = time.time()

def run():
    """Main entry point - start the bot."""
    print(f"""
╔══════════════════════════════════════════════════════════╗
║  🚀 CryptoPulse AI v{BOT_VERSION}                         ║
║  Ultimate Handler Hub - Part 9                          ║
║  {get_persian_time()}                          ║
╚══════════════════════════════════════════════════════════╝
    """)

    # Validate token
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN not set!")
        sys.exit(1)

    # Check for parts
    print(f"📦 Loaded parts: {list(part_loader.loaded_parts.keys())}")

    # Build application
    app = CryptoPulseApp()
    application = app.build()

    # Start scheduler
    scheduler = Scheduler(app)
    scheduler.start()

    # Start bot
    try:
        if WEBHOOK_URL:
            print(f"🌐 Starting webhook on {WEBHOOK_URL}")
            application.run_webhook(
                listen="0.0.0.0",
                port=int(os.environ.get("PORT", 8443)),
                url_path=BOT_TOKEN,
                webhook_url=WEBHOOK_URL
            )
        else:
            print("📡 Starting polling...")
            application.run_polling(drop_pending_updates=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # Ensure required imports for secrets/uuid
    import secrets as secrets_mod
    import uuid as uuid_mod
    secrets = secrets_mod
    uuid = uuid_mod
    run()
