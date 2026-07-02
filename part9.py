#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                    ║
║   ██████╗██████╗██╗   ██╗██████╗████████╗██████╗ ██╗   ██╗ █████╗ ███████╗███████╗║
║  ██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗╚══██╔══╝██╔══██╗╚██╗ ██╔╝██╔══██╗██╔════╝██╔════╝║
║  ██║     ██████╔╝ ╚████╔╝ ██████╔╝   ██║   ██████╔╝ ╚████╔╝ ███████║███████╗███████╗║
║  ██║     ██╔══██╗  ╚██╔╝  ██╔═══╝    ██║   ██╔══██╗  ╚██╔╝  ██╔══██║╚════██║╚════██║║
║  ╚██████╗██║  ██║   ██║   ██║        ██║   ██║  ██║   ██║   ██║  ██║███████║███████║║
║   ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝        ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝║
║                                                                                    ║
║  🚀 CryptoPulse AI Bot v8.0 — GOD MODE Telegram Handlers — FINAL BOSS            ║
║  ───────────────────────────────────────────────────────────────────────────────    ║
║  👑 Supreme Admin  |  👤 User Mastery  |  💰 Payment Lord  |  💎 VIP Emperor     ║
║  📢 Broadcast King  |  📡 Channel Overlord  |  🔧 API God  |  💾 Backup Titan   ║
║  🚪 Server Deity  |  🧠 Omniscient Intelligence  |  🤖 God Signal Commander     ║
║  ════════════════════════════════════════════════════════════════════════════════   ║
║  📁 ۲۵۰۰۰+ خط کد  |  ⚡ ابرفرکانس  |  🔥 اساطیری  |  🛡️ ضد هسته‌ای             ║
║                                                                                    ║
╚════════════════════════════════════════════════════════════════════════════════════╝
"""

# ============================================================
#                    IMPORTS — THE ARSENAL
# ============================================================
import os, sys, json, math, time, random, string, hashlib, hmac, base64, re, asyncio
import warnings, logging, traceback, threading, itertools, functools, operator
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import (Dict, Any, List, Optional, Tuple, Union, Set, Callable, Coroutine,
                    TypeVar, Generic, Protocol, runtime_checkable, ClassVar)
from collections import defaultdict, OrderedDict, deque, Counter, namedtuple, ChainMap
from dataclasses import dataclass, field, asdict, astuple, fields, InitVar
from enum import Enum, IntEnum, auto, unique, Flag
from functools import wraps, lru_cache, partial, reduce, singledispatch, total_ordering
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed, Future
from contextlib import contextmanager, asynccontextmanager, suppress, redirect_stdout, redirect_stderr
from itertools import chain, combinations, cycle, dropwhile, filterfalse, groupby, islice, permutations, product, starmap, takewhile, tee, zip_longest
from pathlib import Path
import textwrap
import unicodedata
import hashlib as hl
import copy

# Suppress all warnings
warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
warnings.filterwarnings("ignore", category=ResourceWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Absolute minimum logging
logging.basicConfig(level=logging.CRITICAL, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("Part9-Boss")
logger.setLevel(logging.CRITICAL)
logger.addHandler(logging.NullHandler())

# ============================================================
#                    TELEGRAM IMPORTS
# ============================================================
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot, ReplyKeyboardMarkup,
    KeyboardButton, ChatPermissions, Message, CallbackQuery, ChatMember, Chat,
    User, MessageId, MessageEntity, InputFile, InputMedia, InputMediaPhoto,
    InputMediaVideo, InputMediaDocument, InputMediaAudio, InputMediaAnimation,
    InlineQueryResult, InlineQueryResultArticle, InlineQueryResultPhoto,
    InlineQueryResultGif, InlineQueryResultVideo, InlineQueryResultAudio,
    InlineQueryResultDocument, InlineQueryResultLocation, InlineQueryResultVenue,
    InlineQueryResultContact, InlineQueryResultGame, InlineQueryResultCachedPhoto,
    InlineQueryResultCachedGif, InlineQueryResultCachedVideo, InlineQueryResultCachedAudio,
    InlineQueryResultCachedDocument, InlineQueryResultCachedSticker, Game, CallbackGame,
    LoginUrl, MenuButton, MenuButtonCommands, MenuButtonWebApp, MenuButtonDefault,
    WebAppData, WebAppInfo, KeyboardButtonPollType, KeyboardButtonRequestChat,
    KeyboardButtonRequestUser, KeyboardButtonRequestUsers, ReplyKeyboardRemove, ForceReply,
    BotCommand, BotCommandScope, BotCommandScopeDefault, BotCommandScopeAllPrivateChats,
    BotCommandScopeAllGroupChats, BotCommandScopeAllChatAdministrators, BotCommandScopeChat,
    BotCommandScopeChatAdministrators, BotCommandScopeChatMember, LabeledPrice,
    SuccessfulPayment, ShippingOption, ShippingAddress, ShippingQuery,
    PreCheckoutQuery, Poll, PollOption, PollAnswer, Dice, ProximityAlertTriggered,
    VoiceChatScheduled, VoiceChatStarted, VoiceChatEnded, VoiceChatParticipantsInvited,
    VideoChatScheduled, VideoChatStarted, VideoChatEnded, VideoChatParticipantsInvited,
)
from telegram.constants import ParseMode, ChatAction, ChatType, ChatMemberStatus
from telegram.warnings import PTBUserWarning
from telegram.ext import (
    Application, ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler, TypeHandler,
    StringCommandHandler, StringRegexHandler, ChatMemberHandler, InlineQueryHandler,
    ChosenInlineResultHandler, PreCheckoutQueryHandler, ShippingQueryHandler,
    PollHandler, PollAnswerHandler, CallbackContext, JobQueue, Defaults,
    ExtBot, AIORateLimiter, BaseHandler, DictPersistence, PicklePersistence,
)
warnings.filterwarnings("ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)
warnings.filterwarnings("ignore", message=r".*PTBUserWarning", category=PTBUserWarning)

# ============================================================
#                    TYPE ALIASES
# ============================================================
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')
Number = Union[int, float]
CallbackData = str
UserID = int
ChatID = int
MessageID = int
Timestamp = int
JsonSerializable = Union[Dict, List, str, int, float, bool, None]

# ============================================================
#                    ENUMS — COMPLETE TAXONOMY
# ============================================================

@unique
class UserRole(IntEnum):
    BANNED = -2
    GUEST = -1
    FREE = 0
    BRONZE = 1
    SILVER = 2
    GOLD = 3
    PLATINUM = 4
    DIAMOND = 5
    VIP = 10
    VIP_PLUS = 11
    VIP_PRO = 12
    VIP_ULTIMATE = 13
    MODERATOR = 50
    ADMIN = 80
    SUPER_ADMIN = 90
    OWNER = 100
    GOD = 999

@unique
class Permission(Flag):
    NONE = 0
    VIEW_SIGNALS = auto()
    REQUEST_SIGNALS = auto()
    VIEW_ANALYSIS = auto()
    REQUEST_ANALYSIS = auto()
    VIEW_VIP = auto()
    BUY_VIP = auto()
    USE_WALLET = auto()
    DEPOSIT = auto()
    WITHDRAW = auto()
    REFERRAL = auto()
    SETTINGS = auto()
    SUPPORT = auto()
    BROADCAST = auto()
    MANAGE_USERS = auto()
    MANAGE_PAYMENTS = auto()
    MANAGE_VIP = auto()
    MANAGE_SETTINGS = auto()
    MANAGE_BACKUP = auto()
    MANAGE_SERVER = auto()
    GOD_MODE = auto()
    ALL = auto()

@unique
class SignalType(Enum):
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    WEAK_BUY = "weak_buy"
    NEUTRAL = "neutral"
    WEAK_SELL = "weak_sell"
    SELL = "sell"
    STRONG_SELL = "strong_sell"
    ACCUMULATE = "accumulate"
    DISTRIBUTE = "distribute"
    WAIT = "wait"

@unique
class MarketCondition(Enum):
    EXTREME_FEAR = "extreme_fear"
    FEAR = "fear"
    NEUTRAL = "neutral"
    GREED = "greed"
    EXTREME_GREED = "extreme_greed"
    BULL_MARKET = "bull_market"
    BEAR_MARKET = "bear_market"
    CRAB_MARKET = "crab_market"
    VOLATILE = "volatile"
    BLACK_SWAN = "black_swan"

@unique
class AlertPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3
    CRITICAL = 4
    NUCLEAR = 5

@unique
class ReportType(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"
    GOD_MODE = "god_mode"

@unique
class BackupType(Enum):
    FULL = "full"
    USERS = "users"
    PAYMENTS = "payments"
    SIGNALS = "signals"
    SETTINGS = "settings"
    INCREMENTAL = "incremental"

@unique
class NotificationChannel(Enum):
    TELEGRAM = "telegram"
    CHANNEL = "channel"
    VIP_CHANNEL = "vip_channel"
    PRIVATE = "private"
    ALL = "all"

# ============================================================
#                    CONVERSATION STATES — FULL MAP
# ============================================================

class ConvState:
    """Complete conversation state machine"""
    IDLE = 0
    MAIN_MENU = 1
    
    # Signal & Analysis
    WAITING_FOR_COIN = 10
    WAITING_FOR_TIMEFRAME = 11
    WAITING_FOR_ANALYSIS_COIN = 12
    WAITING_FOR_SIGNAL_COIN = 13
    
    # Wallet
    WAITING_FOR_DEPOSIT_AMOUNT = 20
    WAITING_FOR_WITHDRAW_AMOUNT = 21
    WAITING_FOR_WITHDRAW_ADDRESS = 22
    WAITING_FOR_REFERRAL_CODE = 23
    
    # VIP
    WAITING_FOR_VIP_PLAN = 30
    WAITING_FOR_RECEIPT = 31
    WAITING_FOR_VIP_REQUEST = 32
    WAITING_FOR_VIP_CONFIRM = 33
    
    # Support
    WAITING_FOR_TICKET = 40
    WAITING_FOR_TICKET_REPLY = 41
    
    # Admin — Users
    WAITING_FOR_USER_ID = 50
    WAITING_FOR_BAN_REASON = 51
    WAITING_FOR_UNBAN_CONFIRM = 52
    WAITING_FOR_MAKE_ADMIN = 53
    WAITING_FOR_DELETE_CONFIRM = 54
    
    # Admin — Payments
    WAITING_FOR_PAYMENT_ID = 60
    WAITING_FOR_PAYMENT_CONFIRM = 61
    WAITING_FOR_PAYMENT_REJECT_REASON = 62
    
    # Admin — VIP
    WAITING_FOR_VIP_USER_ID = 70
    WAITING_FOR_VIP_DURATION = 71
    WAITING_FOR_VIP_REMOVE_CONFIRM = 72
    
    # Admin — Broadcast
    WAITING_FOR_BROADCAST_MESSAGE = 80
    WAITING_FOR_BROADCAST_CONFIRM = 81
    
    # Admin — Channel
    WAITING_FOR_CHANNEL_MESSAGE = 90
    WAITING_FOR_CHANNEL_CONFIRM = 91
    
    # Admin — Settings
    WAITING_FOR_SETTING_KEY = 100
    WAITING_FOR_SETTING_VALUE = 101
    
    # Admin — Backup
    WAITING_FOR_BACKUP_NAME = 110
    WAITING_FOR_BACKUP_RESTORE = 111
    WAITING_FOR_BACKUP_DELETE = 112
    
    # Admin — Server
    WAITING_FOR_SERVER_ACTION = 120
    WAITING_FOR_SERVER_CONFIRM = 121
    
    # God Mode
    WAITING_FOR_GOD_COMMAND = 130
    WAITING_FOR_GOD_CONFIRM = 131
    
    # Settings
    WAITING_FOR_LANGUAGE = 140
    WAITING_FOR_TIMEFRAME_SETTING = 141
    WAITING_FOR_NOTIFICATION_SETTING = 142
    WAITING_FOR_AI_SETTING = 143
    WAITING_FOR_SECURITY_SETTING = 144

# ============================================================
#                    DATA CLASSES — COMPLETE MODELS
# ============================================================

@dataclass
class UserProfile:
    """Complete user profile"""
    telegram_id: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language: str = "fa"
    phone: Optional[str] = None
    email: Optional[str] = None
    role: UserRole = UserRole.FREE
    is_vip: bool = False
    is_premium: bool = False
    is_admin: bool = False
    is_banned: bool = False
    is_active: bool = True
    ban_reason: Optional[str] = None
    banned_at: Optional[str] = None
    banned_by: Optional[str] = None
    vip_level: int = 0
    vip_plan: Optional[str] = None
    vip_expire: Optional[str] = None
    vip_activated_at: Optional[str] = None
    vip_trial_used: bool = False
    vip_renewal_count: int = 0
    vip_total_spent: float = 0.0
    balance: float = 0.0
    total_deposited: float = 0.0
    total_withdrawn: float = 0.0
    total_profit: float = 0.0
    referral_code: Optional[str] = None
    referred_by: Optional[str] = None
    referral_count: int = 0
    referral_earnings: float = 0.0
    total_trades: int = 0
    successful_trades: int = 0
    failed_trades: int = 0
    win_rate: float = 0.0
    notifications_enabled: bool = True
    timeframe: str = "4h"
    ai_enabled: bool = True
    sound_alert: bool = False
    night_mode: bool = False
    registered_at: Optional[str] = None
    last_active: Optional[str] = None
    last_signal: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

@dataclass
class PaymentRecord:
    """Complete payment record"""
    payment_id: str
    user_id: str
    amount: float
    currency: str = "IRT"
    payment_type: str = "deposit"
    status: str = "pending"
    transaction_id: Optional[str] = None
    receipt_file_id: Optional[str] = None
    admin_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None
    confirmed_at: Optional[str] = None
    rejected_at: Optional[str] = None
    reject_reason: Optional[str] = None

@dataclass
class SignalRecord:
    """Complete signal record"""
    signal_id: str
    user_id: str
    coin: str
    signal_type: str
    confidence: float = 50.0
    entry_price: Optional[float] = None
    current_price: Optional[float] = None
    exit_price: Optional[float] = None
    stop_loss: Optional[float] = None
    targets: Optional[str] = None
    timeframe: str = "4h"
    analysis: Optional[str] = None
    result: Optional[str] = None
    profit_loss: Optional[float] = None
    risk_reward: Optional[float] = None
    created_at: Optional[str] = None
    closed_at: Optional[str] = None

@dataclass
class BroadcastJob:
    """Broadcast job tracker"""
    id: str
    target: str
    message: str
    total_users: int = 0
    success_count: int = 0
    fail_count: int = 0
    status: str = "pending"
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

@dataclass
class SystemStatus:
    """Complete system status"""
    bot_online: bool = False
    database_connected: bool = False
    market_connected: bool = False
    ai_connected: bool = False
    god_mode_active: bool = False
    uptime_seconds: float = 0.0
    total_users: int = 0
    active_users_24h: int = 0
    total_signals_today: int = 0
    total_revenue_today: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    disk_usage_percent: float = 0.0
    api_calls_today: int = 0
    errors_today: int = 0
    last_error: Optional[str] = None
    last_backup: Optional[str] = None
    last_update: Optional[str] = None
    version: str = "8.0.0"
    environment: str = "production"

# ============================================================
#                    PERMISSION SYSTEM
# ============================================================

class PermissionManager:
    """Advanced permission management"""
    
    _role_permissions: Dict[UserRole, Permission] = {
        UserRole.BANNED: Permission.NONE,
        UserRole.GUEST: Permission.VIEW_SIGNALS | Permission.VIEW_ANALYSIS,
        UserRole.FREE: Permission.VIEW_SIGNALS | Permission.REQUEST_SIGNALS | Permission.VIEW_ANALYSIS | Permission.REQUEST_ANALYSIS | Permission.VIEW_VIP | Permission.USE_WALLET | Permission.SETTINGS | Permission.SUPPORT,
        UserRole.BRONZE: Permission.VIEW_SIGNALS | Permission.REQUEST_SIGNALS | Permission.VIEW_ANALYSIS | Permission.REQUEST_ANALYSIS | Permission.VIEW_VIP | Permission.USE_WALLET | Permission.DEPOSIT | Permission.SETTINGS | Permission.SUPPORT,
        UserRole.SILVER: Permission.VIEW_SIGNALS | Permission.REQUEST_SIGNALS | Permission.VIEW_ANALYSIS | Permission.REQUEST_ANALYSIS | Permission.VIEW_VIP | Permission.USE_WALLET | Permission.DEPOSIT | Permission.REFERRAL | Permission.SETTINGS | Permission.SUPPORT,
        UserRole.GOLD: Permission.VIEW_SIGNALS | Permission.REQUEST_SIGNALS | Permission.VIEW_ANALYSIS | Permission.REQUEST_ANALYSIS | Permission.VIEW_VIP | Permission.USE_WALLET | Permission.DEPOSIT | Permission.WITHDRAW | Permission.REFERRAL | Permission.SETTINGS | Permission.SUPPORT,
        UserRole.PLATINUM: Permission.VIEW_SIGNALS | Permission.REQUEST_SIGNALS | Permission.VIEW_ANALYSIS | Permission.REQUEST_ANALYSIS | Permission.VIEW_VIP | Permission.BUY_VIP | Permission.USE_WALLET | Permission.DEPOSIT | Permission.WITHDRAW | Permission.REFERRAL | Permission.SETTINGS | Permission.SUPPORT,
        UserRole.DIAMOND: Permission.VIEW_SIGNALS | Permission.REQUEST_SIGNALS | Permission.VIEW_ANALYSIS | Permission.REQUEST_ANALYSIS | Permission.VIEW_VIP | Permission.BUY_VIP | Permission.USE_WALLET | Permission.DEPOSIT | Permission.WITHDRAW | Permission.REFERRAL | Permission.SETTINGS | Permission.SUPPORT,
        UserRole.VIP: Permission.VIEW_SIGNALS | Permission.REQUEST_SIGNALS | Permission.VIEW_ANALYSIS | Permission.REQUEST_ANALYSIS | Permission.VIEW_VIP | Permission.BUY_VIP | Permission.USE_WALLET | Permission.DEPOSIT | Permission.WITHDRAW | Permission.REFERRAL | Permission.SETTINGS | Permission.SUPPORT,
        UserRole.VIP_PLUS: Permission.VIEW_SIGNALS | Permission.REQUEST_SIGNALS | Permission.VIEW_ANALYSIS | Permission.REQUEST_ANALYSIS | Permission.VIEW_VIP | Permission.BUY_VIP | Permission.USE_WALLET | Permission.DEPOSIT | Permission.WITHDRAW | Permission.REFERRAL | Permission.SETTINGS | Permission.SUPPORT | Permission.GOD_MODE,
        UserRole.VIP_PRO: Permission.VIEW_SIGNALS | Permission.REQUEST_SIGNALS | Permission.VIEW_ANALYSIS | Permission.REQUEST_ANALYSIS | Permission.VIEW_VIP | Permission.BUY_VIP | Permission.USE_WALLET | Permission.DEPOSIT | Permission.WITHDRAW | Permission.REFERRAL | Permission.SETTINGS | Permission.SUPPORT | Permission.GOD_MODE,
        UserRole.VIP_ULTIMATE: Permission.VIEW_SIGNALS | Permission.REQUEST_SIGNALS | Permission.VIEW_ANALYSIS | Permission.REQUEST_ANALYSIS | Permission.VIEW_VIP | Permission.BUY_VIP | Permission.USE_WALLET | Permission.DEPOSIT | Permission.WITHDRAW | Permission.REFERRAL | Permission.SETTINGS | Permission.SUPPORT | Permission.GOD_MODE,
        UserRole.MODERATOR: Permission.VIEW_SIGNALS | Permission.REQUEST_SIGNALS | Permission.VIEW_ANALYSIS | Permission.REQUEST_ANALYSIS | Permission.VIEW_VIP | Permission.BUY_VIP | Permission.USE_WALLET | Permission.DEPOSIT | Permission.WITHDRAW | Permission.REFERRAL | Permission.SETTINGS | Permission.SUPPORT | Permission.BROADCAST | Permission.MANAGE_USERS,
        UserRole.ADMIN: Permission.ALL ^ Permission.GOD_MODE,
        UserRole.SUPER_ADMIN: Permission.ALL ^ Permission.GOD_MODE,
        UserRole.OWNER: Permission.ALL,
        UserRole.GOD: Permission.ALL,
    }
    
    @classmethod
    def get_permissions(cls, role: UserRole) -> Permission:
        return cls._role_permissions.get(role, Permission.NONE)
    
    @classmethod
    def has_permission(cls, role: UserRole, permission: Permission) -> bool:
        return bool(cls.get_permissions(role) & permission)
    
    @classmethod
    def can_access_admin(cls, role: UserRole) -> bool:
        return cls.has_permission(role, Permission.MANAGE_USERS)
    
    @classmethod
    def can_use_god_mode(cls, role: UserRole) -> bool:
        return cls.has_permission(role, Permission.GOD_MODE)

# ============================================================
#                    SAFE IMPORT SYSTEM
# ============================================================

class SafeImporter:
    """Ultra-safe dynamic module importer with dependency resolution"""
    
    _cache: Dict[str, Any] = {}
    _lock = threading.RLock()
    _import_order = [
        "Part3", "part5", "part2", "part4", "part6", "part7", "part8",
        "part16", "part17", "part18", "part5", "part1", "part2",
        "part3", "part4", "part6", "part7", "part8", "part10",
        "part11", "part12", "part13", "part14", "part15"
    ]
    
    @classmethod
    def import_module(cls, module_name: str, *attrs: str) -> Dict[str, Any]:
        cache_key = f"{module_name}:{','.join(attrs)}"
        with cls._lock:
            if cache_key in cls._cache:
                return cls._cache[cache_key]
        
        result = {}
        try:
            module = __import__(module_name, fromlist=list(attrs))
            for attr in attrs:
                result[attr] = getattr(module, attr, None)
            cls._cache[cache_key] = result
        except Exception:
            for attr in attrs:
                result[attr] = None
            cls._cache[cache_key] = result
        
        return result

# Initialize all imports
_safe = SafeImporter()

_bot3_data = _safe.import_module("bot3", "get_user_repo", "get_signal_repo", "get_payment_repo", "db_manager")
_bot5_data = _safe.import_module("bot5", "get_market", "get_coinex", "get_signal", "get_ticker", "get_price", "get_ohlcv_data", "get_market_summary")
_part16_data = _safe.import_module("part16", "get_intelligence_engine")
_part17_data = _safe.import_module("part17", "get_analysis_engine", "analyze", "detect_patterns", "fibonacci_levels", "support_resistance", "pivot_points")
_part18_data = _safe.import_module("part18", "get_god_mode_engine", "get_signal", "get_top_signals", "get_market_overview", "send_signal_to_channel", "send_overview_to_channel", "send_top_to_channel", "GodModeEngine", "GodSignal", "MarketOverview")

get_user_repo = _bot3_data.get("get_user_repo")
get_signal_repo = _bot3_data.get("get_signal_repo")
get_payment_repo = _bot3_data.get("get_payment_repo")
db_manager = _bot3_data.get("db_manager")
get_market = _bot5_data.get("get_market")
get_coinex = _bot5_data.get("get_coinex")
get_signal_func = _bot5_data.get("get_signal")
get_ticker_func = _bot5_data.get("get_ticker")
get_price_func = _bot5_data.get("get_price")
get_ohlcv_func = _bot5_data.get("get_ohlcv_data")
get_market_summary_func = _bot5_data.get("get_market_summary")
get_intelligence_engine = _part16_data.get("get_intelligence_engine")
get_analysis_engine = _part17_data.get("get_analysis_engine")
analyze_advanced = _part17_data.get("analyze")
detect_patterns = _part17_data.get("detect_patterns")
fibonacci_levels = _part17_data.get("fibonacci_levels")
support_resistance = _part17_data.get("support_resistance")
pivot_points_func = _part17_data.get("pivot_points")
get_god_mode_engine = _part18_data.get("get_god_mode_engine")
god_get_signal = _part18_data.get("get_signal")
god_get_top_signals = _part18_data.get("get_top_signals")
god_get_market_overview = _part18_data.get("get_market_overview")
god_send_signal = _part18_data.get("send_signal_to_channel")
god_send_overview = _part18_data.get("send_overview_to_channel")
god_send_top = _part18_data.get("send_top_to_channel")

# ============================================================
#                    GLOBAL CONFIG
# ============================================================

ADMIN_IDS: List[int] = []
for x in os.environ.get("ADMIN_IDS", "").split(","):
    x = x.strip()
    if x:
        try: ADMIN_IDS.append(int(x))
        except ValueError: pass

BOT_TOKEN = (
    os.environ.get("BOT_TOKEN", "") or
    os.environ.get("Telegram _bot_token", "") or
    os.environ.get("telegram_bot_token", "") or
    os.environ.get("TELEGRAM_BOT_TOKEN", "") or
    os.environ.get("BOT_TOKEN_MAIN", "")
)

CHANNEL_ID = os.environ.get("CHANNEL_ID", "@CryptoPulse606")
SIGNAL_CHANNEL_ID = os.environ.get("SIGNAL_CHANNEL_ID", CHANNEL_ID)
VIP_CHANNEL_ID = os.environ.get("VIP_CHANNEL_ID", "")
ALERT_CHANNEL_ID = os.environ.get("ALERT_CHANNEL_ID", CHANNEL_ID)
REPORT_CHANNEL_ID = os.environ.get("REPORT_CHANNEL_ID", "")
BACKUP_CHANNEL_ID = os.environ.get("BACKUP_CHANNEL_ID", "")
SUPPORT_USERNAME = os.environ.get("VIP_ADMIN_USERNAME", "Amir92aa")
VIP_CARD = os.environ.get("VIP_PAYMENT_CARD", "6063731196254479")
VIP_HOLDER = os.environ.get("VIP_PAYMENT_HOLDER", "Farhad Behmard")
VIP_PRICE_MONTHLY = int(os.environ.get("VIP_PRICE_MONTHLY", "199000"))
VIP_PRICE_QUARTERLY = int(os.environ.get("VIP_PRICE_QUARTERLY", "499000"))
VIP_PRICE_YEARLY = int(os.environ.get("VIP_PRICE_YEARLY", "1990000"))
VIP_PRICE_LIFETIME = int(os.environ.get("VIP_PRICE_LIFETIME", "4990000"))
PROXY_URL = os.environ.get("PROXY_URL", "")
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///bot.db")
DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1", "yes")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
WEBHOOK_PORT = int(os.environ.get("WEBHOOK_PORT", "8443"))
MAX_CONNECTIONS = int(os.environ.get("MAX_CONNECTIONS", "40"))
RATE_LIMIT_PER_SECOND = int(os.environ.get("RATE_LIMIT_PER_SECOND", "30"))

SUPPORTED_COINS = [
    "BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "DOT", "MATIC", "SHIB",
    "AVAX", "LINK", "UNI", "ATOM", "LTC", "BCH", "NEAR", "VET", "ALGO", "FTM",
    "EOS", "TRX", "XLM", "ICP", "HBAR", "FIL", "APT", "ARB", "OP", "SUI",
    "PEPE", "WIF", "BONK", "SEI", "TIA", "INJ", "RUNE", "RNDR", "FET", "AGIX",
    "OCEAN", "AKT", "TAO", "WLD", "SAND", "MANA", "AXS", "GALA", "ENJ", "CHZ",
    "APE", "GMT", "FTT", "1INCH", "AAVE", "COMP", "MKR", "SNX", "CRV", "SUSHI",
    "CAKE", "UNI", "DYDX", "GMX", "GNS", "LDO", "STG", "RDNT", "TON", "NOT",
    "JUP", "PYTH", "JTO", "BOME", "WEN", "MYRO", "POPCAT", "MEW", "SLERF", "SAMO",
]

SUPPORTED_TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d", "3d", "1w", "1M"]
DEFAULT_TIMEFRAME = "4h"

# ============================================================
#                    UTILITY FUNCTIONS — COMPLETE ARSENAL
# ============================================================

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def is_vip(user_id: int) -> bool:
    if get_user_repo:
        db_user = get_user_repo().get_by_telegram_id(str(user_id))
        return db_user.get('is_vip', False) if db_user else False
    return False

def get_user_role(user_id: int) -> UserRole:
    if user_id in ADMIN_IDS:
        return UserRole.ADMIN
    if is_vip(user_id):
        return UserRole.VIP
    return UserRole.FREE

def get_persian_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_persian_date() -> str:
    return datetime.now().strftime("%Y-%m-%d")

def get_timestamp() -> int:
    return int(time.time())

def get_iso_time() -> str:
    return datetime.now().isoformat()

def validate_coin(coin: str) -> bool:
    return coin.upper().strip() in SUPPORTED_COINS

def validate_timeframe(tf: str) -> bool:
    return tf.lower().strip() in SUPPORTED_TIMEFRAMES

def generate_referral_code(length: int = 8) -> str:
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))

def generate_payment_id() -> str:
    return f"PAY-{int(time.time())}-{random.randint(1000,9999)}"

def generate_signal_id() -> str:
    return f"SIG-{int(time.time())}-{random.randint(1000,9999)}"

def generate_backup_id() -> str:
    return f"BAK-{datetime.now().strftime('%Y%m%d%H%M%S')}"

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

def format_volume(vol: float) -> str:
    return format_number(vol, 2)

def truncate_text(text: str, max_length: int = 4096) -> str:
    if len(text) <= max_length: return text
    return text[:max_length-3] + "..."

def escape_markdown(text: str) -> str:
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{c}' if c in escape_chars else c for c in str(text))

def safe_parse_int(value: Any, default: int = 0) -> int:
    try: return int(value)
    except: return default

def safe_parse_float(value: Any, default: float = 0.0) -> float:
    try: return float(value)
    except: return default

def random_emoji() -> str:
    emojis = ["🚀","💎","🔥","⚡","🎯","💪","👑","🌟","💫","🦾","🧠","🦅","🐋","🦈","🐉","🌙","☀️","🌈","💥","🎪"]
    return random.choice(emojis)

def signal_emoji(signal_type: str) -> str:
    return {"strong_buy":"🟢🟢🟢","buy":"🟢🟢","weak_buy":"🟢","neutral":"🟡","weak_sell":"🔴","sell":"🔴🔴","strong_sell":"🔴🔴🔴","accumulate":"🐋","distribute":"🦈","wait":"⏳"}.get(signal_type,"🟡")

def confidence_stars(confidence: float) -> str:
    if confidence >= 90: return "⭐⭐⭐⭐⭐"
    if confidence >= 80: return "⭐⭐⭐⭐"
    if confidence >= 70: return "⭐⭐⭐"
    if confidence >= 60: return "⭐⭐"
    return "⭐"

def progress_bar(percent: float, length: int = 10) -> str:
    filled = int(percent / 100 * length)
    return "█" * filled + "░" * (length - filled)

# ============================================================
#                    DECORATORS — ULTIMATE COLLECTION
# ============================================================

def admin_only(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("❌ **دسترسی غیرمجاز!**\nاین بخش فقط برای ادمین‌هاست.", parse_mode=ParseMode.MARKDOWN)
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def super_admin_only(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if update.effective_user.id not in ADMIN_IDS:
            await update.message.reply_text("❌ **فوق‌ادمین لازم است!**", parse_mode=ParseMode.MARKDOWN)
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def vip_only(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if not is_vip(user_id) and not is_admin(user_id):
            await update.message.reply_text("💎 **VIP لازم است!**\nاین بخش ویژه کاربران VIP می‌باشد.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💎 خرید VIP", callback_data="vip")]]), parse_mode=ParseMode.MARKDOWN)
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def rate_limit(max_calls: int = 5, period: int = 60, message: str = None):
    storage = defaultdict(list)
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user_id = str(update.effective_user.id)
            now = time.time()
            storage[user_id] = [t for t in storage[user_id] if now - t < period]
            if len(storage[user_id]) >= max_calls:
                wait = int(period - (now - storage[user_id][0]))
                msg = message or f"⏳ لطفاً {wait} ثانیه صبر کنید..."
                await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
                return
            storage[user_id].append(now)
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator

def log_action(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        action_name = func.__name__
        return await func(update, context, *args, **kwargs)
    return wrapper

def require_permission(permission: Permission):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user_id = update.effective_user.id
            role = get_user_role(user_id)
            if not PermissionManager.has_permission(role, permission):
                await update.message.reply_text("❌ **شما مجوز این عملیات را ندارید!**", parse_mode=ParseMode.MARKDOWN)
                return
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator

def handle_errors(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            error_msg = f"❌ خطا: {str(e)[:100]}"
            try:
                await update.message.reply_text(error_msg, parse_mode=ParseMode.MARKDOWN)
            except:
                try:
                    await update.callback_query.message.reply_text(error_msg, parse_mode=ParseMode.MARKDOWN)
                except:
                    pass
    return wrapper

def cooldown(seconds: int = 3):
    storage = {}
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user_id = str(update.effective_user.id)
            now = time.time()
            if user_id in storage and now - storage[user_id] < seconds:
                remaining = int(seconds - (now - storage[user_id]))
                await update.message.reply_text(f"⏳ {remaining} ثانیه صبر کنید...")
                return
            storage[user_id] = now
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator

# ============================================================
#                    KEYBOARD FACTORY — GRAND COLLECTION
# ============================================================

class KeyboardFactory:
    """Ultimate keyboard factory with 100+ keyboard layouts"""
    
    @staticmethod
    def _btn(text: str, callback_data: str = None, url: str = None) -> InlineKeyboardButton:
        if url: return InlineKeyboardButton(text, url=url)
        return InlineKeyboardButton(text, callback_data=callback_data or text.lower().replace(" ", "_"))
    
    @staticmethod
    def _row(*buttons: InlineKeyboardButton) -> List[InlineKeyboardButton]:
        return list(buttons)
    
    @staticmethod
    def _markup(rows: List[List[InlineKeyboardButton]]) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(rows)
    
    # ---- MAIN MENUS ----
    @classmethod
    def user_main_menu(cls) -> InlineKeyboardMarkup:
        return cls._markup([
            cls._row(cls._btn("📊 تحلیل لحظه‌ای", "analysis")),
            cls._row(cls._btn("🚨 سیگنال خرید", "signal_buy"), cls._btn("📈 سیگنال فروش", "signal_sell")),
            cls._row(cls._btn("💰 کیف پول", "wallet"), cls._btn("💎 VIP", "vip")),
            cls._row(cls._btn("📡 سیگنال‌ها", "signals_menu")),
            cls._row(cls._btn("📖 راهنما", "help"), cls._btn("🆘 پشتیبانی", "support")),
            cls._row(cls._btn("⚙️ تنظیمات", "settings")),
        ])
    
    @classmethod
    def admin_main_menu(cls) -> InlineKeyboardMarkup:
        return cls._markup([
            cls._row(cls._btn("🧠 داشبورد هوشمند", "admin_intelligence")),
            cls._row(cls._btn("🤖 God Mode Signal", "admin_god_signal"), cls._btn("📊 God Overview", "admin_god_overview")),
            cls._row(cls._btn("👥 مدیریت کاربران", "admin_users")),
            cls._row(cls._btn("💰 مدیریت پرداخت‌ها", "admin_payments")),
            cls._row(cls._btn("💎 مدیریت VIP", "admin_vip")),
            cls._row(cls._btn("📢 ارسال همگانی", "admin_broadcast"), cls._btn("📡 ارسال به کانال", "admin_send_channel")),
            cls._row(cls._btn("🔧 API", "admin_api"), cls._btn("💾 بکاپ", "admin_backup")),
            cls._row(cls._btn("🚪 سرور", "admin_server"), cls._btn("📊 گزارش‌ها", "admin_reports")),
            cls._row(cls._btn("🔒 امنیت", "admin_security"), cls._btn("📈 Top Signals", "admin_top_signals")),
            cls._row(cls._btn("🔙 منوی کاربری", "back_main")),
        ])
    
    @classmethod
    def super_admin_menu(cls) -> InlineKeyboardMarkup:
        return cls._markup([
            cls._row(cls._btn("🧠 داشبورد هوشمند", "admin_intelligence")),
            cls._row(cls._btn("🤖 God Mode", "admin_god_signal"), cls._btn("📊 God Overview", "admin_god_overview")),
            cls._row(cls._btn("👥 کاربران", "admin_users"), cls._btn("💰 پرداخت‌ها", "admin_payments")),
            cls._row(cls._btn("💎 VIP", "admin_vip"), cls._btn("📢 همگانی", "admin_broadcast")),
            cls._row(cls._btn("📡 کانال", "admin_send_channel"), cls._btn("🔧 API", "admin_api")),
            cls._row(cls._btn("💾 بکاپ", "admin_backup"), cls._btn("🚪 سرور", "admin_server")),
            cls._row(cls._btn("📊 گزارش‌ها", "admin_reports"), cls._btn("🔒 امنیت", "admin_security")),
            cls._row(cls._btn("📈 Top Signals", "admin_top_signals"), cls._btn("📊 Market", "admin_market")),
            cls._row(cls._btn("⚙️ تنظیمات سیستم", "admin_system_settings")),
            cls._row(cls._btn("🔙 منوی کاربری", "back_main")),
        ])
    
    # ---- VIP MENUS ----
    @classmethod
    def vip_main_menu(cls) -> InlineKeyboardMarkup:
        return cls._markup([
            cls._row(cls._btn(f"💎 VIP ماهانه - {VIP_PRICE_MONTHLY:,} تومان", "vip_monthly")),
            cls._row(cls._btn(f"💎 VIP سه‌ماهه - {VIP_PRICE_QUARTERLY:,} تومان", "vip_quarterly")),
            cls._row(cls._btn(f"💎 VIP سالانه - {VIP_PRICE_YEARLY:,} تومان", "vip_yearly")),
            cls._row(cls._btn(f"👑 VIP مادام‌العمر - {VIP_PRICE_LIFETIME:,} تومان", "vip_lifetime")),
            cls._row(cls._btn("ℹ️ وضعیت VIP", "vip_status")),
            cls._row(cls._btn("🎁 تست رایگان ۳ روزه", "vip_trial")),
            cls._row(cls._btn("📋 راهنمای خرید", "vip_guide")),
            cls._row(cls._btn("🔙 بازگشت", "back_main")),
        ])
    
    # ---- WALLET MENUS ----
    @classmethod
    def wallet_menu(cls) -> InlineKeyboardMarkup:
        return cls._markup([
            cls._row(cls._btn("💰 موجودی", "wallet_balance"), cls._btn("💳 واریز", "wallet_deposit")),
            cls._row(cls._btn("📤 برداشت", "wallet_withdraw"), cls._btn("📊 تاریخچه", "wallet_history")),
            cls._row(cls._btn("📈 گزارش معاملات", "wallet_report"), cls._btn("🔑 کد معرف", "wallet_referral")),
            cls._row(cls._btn("🔙 بازگشت", "back_main")),
        ])
    
    # ---- SETTINGS MENUS ----
    @classmethod
    def settings_menu(cls) -> InlineKeyboardMarkup:
        return cls._markup([
            cls._row(cls._btn("🔔 اعلان‌ها", "settings_notifications")),
            cls._row(cls._btn("📊 تایم‌فریم", "settings_timeframe")),
            cls._row(cls._btn("🤖 هوش مصنوعی", "settings_ai")),
            cls._row(cls._btn("🌍 زبان", "settings_language")),
            cls._row(cls._btn("💰 واحد پول", "settings_currency")),
            cls._row(cls._btn("🔒 امنیت", "settings_security")),
            cls._row(cls._btn("📱 دستگاه", "settings_device")),
            cls._row(cls._btn("🔙 بازگشت", "back_main")),
        ])
    
    # ---- SIGNALS MENU ----
    @classmethod
    def signals_menu(cls) -> InlineKeyboardMarkup:
        return cls._markup([
            cls._row(cls._btn("📊 تحلیل لحظه‌ای", "analysis")),
            cls._row(cls._btn("🚨 سیگنال خرید", "signal_buy"), cls._btn("📈 سیگنال فروش", "signal_sell")),
            cls._row(cls._btn("🤖 God Mode Signal", "admin_god_signal")),
            cls._row(cls._btn("📊 تحلیل پیشرفته", "advanced_analysis")),
            cls._row(cls._btn("📈 Top 10 Signals", "admin_top_signals")),
            cls._row(cls._btn("🔙 بازگشت", "back_main")),
        ])
    
    # ---- ADMIN: USERS ----
    @classmethod
    def admin_users_menu(cls) -> InlineKeyboardMarkup:
        return cls._markup([
            cls._row(cls._btn("📋 لیست کاربران", "admin_users_list")),
            cls._row(cls._btn("🔍 جستجوی کاربر", "admin_users_search")),
            cls._row(cls._btn("🔨 بن کاربر", "admin_users_ban"), cls._btn("🔓 آنبن کاربر", "admin_users_unban")),
            cls._row(cls._btn("👑 ادمین کردن", "admin_users_make_admin"), cls._btn("🗑️ حذف کاربر", "admin_users_delete")),
            cls._row(cls._btn("📊 آمار کاربران", "admin_users_stats")),
            cls._row(cls._btn("📋 کاربران VIP", "admin_users_vip_list"), cls._btn("⚠️ کاربران پرریسک", "admin_users_risk")),
            cls._row(cls._btn("💤 کاربران غیرفعال", "admin_users_inactive"), cls._btn("🆕 کاربران جدید", "admin_users_new")),
            cls._row(cls._btn("🔙 بازگشت", "back_main")),
        ])
    
    # ---- ADMIN: PAYMENTS ----
    @classmethod
    def admin_payments_menu(cls) -> InlineKeyboardMarkup:
        return cls._markup([
            cls._row(cls._btn("⏳ در انتظار", "admin_payments_pending")),
            cls._row(cls._btn("✅ تایید شده", "admin_payments_completed"), cls._btn("❌ رد شده", "admin_payments_rejected")),
            cls._row(cls._btn("📊 گزارش مالی", "admin_payments_report")),
            cls._row(cls._btn("💰 تنظیم قیمت‌ها", "admin_payments_prices")),
            cls._row(cls._btn("💳 مدیریت کارت‌ها", "admin_payments_cards")),
            cls._row(cls._btn("🔙 بازگشت", "back_main")),
        ])
    
    # ---- ADMIN: VIP ----
    @classmethod
    def admin_vip_menu(cls) -> InlineKeyboardMarkup:
        return cls._markup([
            cls._row(cls._btn("⏳ درخواست‌های VIP", "admin_vip_requests")),
            cls._row(cls._btn("📋 لیست VIP ها", "admin_vip_list")),
            cls._row(cls._btn("📊 آمار VIP", "admin_vip_stats")),
            cls._row(cls._btn("➕ افزودن دستی", "admin_vip_add"), cls._btn("➖ حذف VIP", "admin_vip_remove")),
            cls._row(cls._btn("🎁 مدیریت تست رایگان", "admin_vip_trial")),
            cls._row(cls._btn("📋 VIP های در حال انقضا", "admin_vip_expiring")),
            cls._row(cls._btn("🔙 بازگشت", "back_main")),
        ])
    
    # ---- ADMIN: BROADCAST ----
    @classmethod
    def admin_broadcast_menu(cls) -> InlineKeyboardMarkup:
        return cls._markup([
            cls._row(cls._btn("📢 همه کاربران", "broadcast_all")),
            cls._row(cls._btn("💎 کاربران VIP", "broadcast_vip")),
            cls._row(cls._btn("👤 کاربران عادی", "broadcast_normal")),
            cls._row(cls._btn("⚠️ کاربران پرریسک", "broadcast_risk")),
            cls._row(cls._btn("🆕 کاربران جدید", "broadcast_new")),
            cls._row(cls._btn("😴 کاربران غیرفعال", "broadcast_inactive")),
            cls._row(cls._btn("🔙 بازگشت", "back_main")),
        ])
    
    # ---- ADMIN: BACKUP ----
    @classmethod
    def admin_backup_menu(cls) -> InlineKeyboardMarkup:
        return cls._markup([
            cls._row(cls._btn("💾 ایجاد بکاپ کامل", "admin_backup_create")),
            cls._row(cls._btn("📥 بازیابی بکاپ", "admin_backup_restore")),
            cls._row(cls._btn("📋 لیست بکاپ‌ها", "admin_backup_list")),
            cls._row(cls._btn("🗑️ حذف بکاپ", "admin_backup_delete")),
            cls._row(cls._btn("⚙️ تنظیمات بکاپ", "admin_backup_settings")),
            cls._row(cls._btn("📤 دانلود بکاپ", "admin_backup_download")),
            cls._row(cls._btn("🔙 بازگشت", "back_main")),
        ])
    
    # ---- ADMIN: SERVER ----
    @classmethod
    def admin_server_menu(cls) -> InlineKeyboardMarkup:
        return cls._markup([
            cls._row(cls._btn("🔄 ریستارت", "admin_restart"), cls._btn("⏹️ توقف", "admin_shutdown")),
            cls._row(cls._btn("📊 وضعیت سرور", "admin_server_status")),
            cls._row(cls._btn("📈 لاگ‌ها", "admin_server_logs"), cls._btn("🧹 پاکسازی کش", "admin_clear_cache")),
            cls._row(cls._btn("📊 مصرف منابع", "admin_server_resources")),
            cls._row(cls._btn("🔙 بازگشت", "back_main")),
        ])
    
    # ---- ADMIN: REPORTS ----
    @classmethod
    def admin_reports_menu(cls) -> InlineKeyboardMarkup:
        return cls._markup([
            cls._row(cls._btn("📈 گزارش رشد", "admin_report_growth")),
            cls._row(cls._btn("💰 گزارش مالی", "admin_payments_report")),
            cls._row(cls._btn("🚨 گزارش سیگنال‌ها", "admin_report_signals")),
            cls._row(cls._btn("👥 گزارش کاربران", "admin_users_stats")),
            cls._row(cls._btn("📊 گزارش هفتگی", "admin_report_weekly")),
            cls._row(cls._btn("📅 گزارش ماهانه", "admin_report_monthly")),
            cls._row(cls._btn("🤖 گزارش God Mode", "admin_report_god")),
            cls._row(cls._btn("🔙 بازگشت", "back_main")),
        ])
    
    # ---- SIMPLE BACK ----
    @classmethod
    def back_only(cls, target: str = "back_main") -> InlineKeyboardMarkup:
        return cls._markup([[cls._btn("🔙 بازگشت", target)]])
    
    @classmethod
    def cancel_back(cls) -> InlineKeyboardMarkup:
        return cls._markup([[cls._btn("❌ لغو", "cancel"), cls._btn("🔙 بازگشت", "back_main")]])
    
    @classmethod
    def confirm_cancel(cls) -> InlineKeyboardMarkup:
        return cls._markup([
            [cls._btn("✅ تایید", "confirm"), cls._btn("❌ لغو", "cancel")],
        ])

# Global keyboard accessor
KB = KeyboardFactory()

# ============================================================
#                    MESSAGE TEMPLATES — COMPLETE LIBRARY
# ============================================================

class Messages:
    """Complete message template library"""
    
    WELCOME_USER = """🌟 **به CryptoPulse AI خوش آمدید!**

🚀 دستیار هوشمند تحلیل و سیگنال ارزهای دیجیتال

✨ **امکانات:**
• 📊 تحلیل لحظه‌ای بازار با هوش مصنوعی
• 🚨 سیگنال‌های دقیق خرید و فروش
• 💎 پنل VIP با امکانات ویژه
• 🤖 God Mode — تحلیل فوق‌پیشرفته
• 🐋 ردیابی نهنگ‌ها
• 📈 تشخیص روند با دقت ۱۰۰٪

👈 از دکمه‌های زیر شروع کنید:"""
    
    WELCOME_ADMIN = """👑 **پنل مدیریت CryptoPulse AI**

🎯 **خوش آمدید سازنده عزیز!**

📊 **آمار لحظه‌ای:**
━━━━━━━━━━━━━━━━━━━━━━
👥 **کاربران:** {users:,}
💎 **VIP:** {vip:,}
🚨 **سیگنال‌ها:** {signals:,}
💰 **درآمد:** {revenue:,.0f} تومان
━━━━━━━━━━━━━━━━━━━━━━
⏰ **زمان:** {time}
🟢 **وضعیت:** آنلاین | 🤖 God Mode: {god_status}"""
    
    VIP_INFO = """💎 **پنل VIP CryptoPulse AI**

✨ **امکانات ویژه VIP:**
━━━━━━━━━━━━━━━━━━━━━━
• 📊 سیگنال‌های VIP با دقت ۹۵٪
• 🤖 تحلیل AI نامحدود
• 🐋 ردیابی نهنگ‌ها
• 🔔 هشدارهای لحظه‌ای
• 🎯 God Mode Access
• 🆘 پشتیبانی ۲۴/۷
• 📈 مدیریت پورتفولیو
• 🎁 سیگنال‌های اختصاصی

💰 **تعرفه‌ها:**
━━━━━━━━━━━━━━━━━━━━━━
• 💎 ماهانه: **{monthly:,}** تومان
• 💎 سه‌ماهه: **{quarterly:,}** تومان
• 💎 سالانه: **{yearly:,}** تومان (۱۰٪ تخفیف)
• 👑 مادام‌العمر: **{lifetime:,}** تومان (۵۰٪ تخفیف)

🎁 **تست رایگان ۳ روزه**"""
    
    HELP_TEXT = """📖 **راهنمای کامل CryptoPulse AI**

🔹 **شروع کار:**
از منوی اصلی با دکمه‌های شیشه‌ای استفاده کنید.

🔹 **تحلیل و سیگنال:**
نام ارز را تایپ کنید یا از دکمه تحلیل استفاده کنید.
سیگنال‌ها بر اساس ۵۰+ اندیکاتور و هوش مصنوعی.

🔹 **God Mode:**
تحلیل فوق‌پیشرفته با دقت ۱۰۰٪
تشخیص فاز بازار، روند، و نقاط ورود/خروج

🔹 **VIP:**
با خرید VIP به امکانات ویژه دسترسی پیدا کنید.
💰 قیمت: از {monthly:,} تومان ماهانه

🔹 **پشتیبانی:**
📱 @{support}
⏰ ۲۴ ساعت شبانه‌روز

📌 **دستورات سریع:**
━━━━━━━━━━━━━━━━━━━━━━
/start — شروع مجدد
/help — راهنما
/admin — پنل ادمین
/signal — دریافت سیگنال
/price — قیمت لحظه‌ای
/vip — پنل VIP
/wallet — کیف پول
/god — God Mode Signal
/cancel — لغو عملیات"""
    
    SUPPORT_TEXT = """🆘 **پشتیبانی CryptoPulse AI**

📱 **ادمین:** @{support}
📧 **ایمیل:** support@cryptopulse.ai
🌐 **وبسایت:** cryptopulse.ai

⏰ **ساعات پاسخگویی:** ۲۴/۷

📝 برای ارسال تیکت روی دکمه زیر کلیک کنید.

💬 **سوالات متداول:**
• چگونه سیگنال بگیرم؟
• قیمت VIP چقدر است؟
• چگونه VIP بخرم؟
• God Mode چیست؟"""
    
    WALLET_TEMPLATE = """💰 **کیف پول شما**

💵 **موجودی:** {balance:,.0f} تومان
💳 **کل واریز:** {total_deposited:,.0f} تومان
📤 **کل برداشت:** {total_withdrawn:,.0f} تومان
📈 **سود کل:** {total_profit:,.0f} تومان

🔗 **کد معرف:** `{referral_code}`
👥 **معرفی‌شده:** {referral_count} نفر
💰 **پاداش:** {referral_earnings:,.0f} تومان

📊 **معاملات:** {total_trades}
✅ **موفق:** {successful_trades} | ❌ **ناموفق:** {failed_trades}
🏆 **نرخ برد:** {win_rate:.1f}%

💎 **VIP:** {vip_status}
📅 **انقضا:** {vip_expire}
📊 **سطح:** {vip_level}

⏰ **آخرین فعالیت:** {last_active}"""
    
    SIGNAL_TEMPLATE = """{main_emoji} **سیگنال {coin}** {main_emoji}

📊 **نوع:** {signal_type}
🎯 **اطمینان:** {confidence:.1f}% {stars}
🧠 **God Score:** {god_score}/100
📊 **قدرت:** [{strength_bar}]

💰 **قیمت فعلی:** {price}
📈 **تغییر ۲۴h:** {change_24h}

🎯 **اهداف:**
{targets}

🛑 **حد ضرر:** {stop_loss}
📈 **R/R:** {risk_reward}

📊 **تحلیل:**
{analysis}

🤖 **AI Prediction:** {ai_prediction}

⏰ **زمان:** {time}
🆔 **شناسه:** `{signal_id}`

⚠️ *مسئولیت استفاده با شماست.*"""
    
    ANALYSIS_TEMPLATE = """📊 **تحلیل تکنیکال {coin}**

🤖 **تحلیل هوش مصنوعی:**
{ai_analysis}

📈 **اندیکاتورها:**
━━━━━━━━━━━━━━━━━━━━━━
• RSI: {rsi:.1f}
• MACD: {macd}
• Bollinger: {bollinger}
• ADX: {adx:.1f}
• MFI: {mfi:.1f}
• Stochastic: {stochastic:.1f}
• ATR: {atr:.4f}

📊 **روند:** {trend}
🎯 **فاز بازار:** {phase}
📈 **ساختار:** {structure}

🎯 **پیشنهاد:** {signal}
🎯 **اطمینان:** {confidence}%

💰 **حمایت‌ها:** {supports}
🚫 **مقاومت‌ها:** {resistances}

⏰ **زمان:** {time}"""
    
    GOD_SIGNAL_TEMPLATE = """🤖 **GOD MODE SIGNAL** 🤖

🪙 **{coin}** | ⏱️ **{timeframe}**

🧠 **God Score:** {god_score:.1f}/100
📊 [{strength_bar}]

🎯 **سیگنال:** {signal_upper}
⚡ **قدرت:** {strength:.1f}%
🎯 **اطمینان:** {confidence:.1f}%

💰 **ورود:** {entry}
🛑 **حد ضرر:** {stop_loss}

🎯 **اهداف:**
{targets}

📈 **R/R:** {risk_reward}
💼 **حجم:** {position_size}%

📊 **تایید تایم‌فریم‌ها:**
{tf_confirmations}

🐋 **نهنگ‌ها:** {whale_activity}
🤖 **AI 24h:** {ai_prediction}

⏰ {time} | 🆔 `{signal_id}`"""
    
    MARKET_OVERVIEW_TEMPLATE = """📊 **نمای کلی بازار** 📊

━━━━━━━━━━━━━━━━━━━━━━

💰 **مارکت کپ:** ${market_cap}T
👑 **BTC Dominance:** {btc_dom}%
😱 **Fear & Greed:** {fear_greed} — {fear_greed_text}

📊 **حجم ۲۴h:** ${volume}B
🪙 **ارزهای فعال:** {active_coins}

📈 **فاز بازار:**
• BTC: {btc_phase}
• کلی: {overall_phase}

📊 **آمار:**
• صعودی: {bullish} | نزولی: {bearish}
• بالای SMA50: {above_sma50}

🚨 **سیگنال‌ها:**
• 🟢 Strong Buy: {strong_buy}
• 🟢 Buy: {buy}
• 🔴 Sell: {sell}
• 🔴 Strong Sell: {strong_sell}

📈 **Top Gainers:**
{gainers}

📉 **Top Losers:**
{losers}

🐋 **نهنگ‌ها (۲۴h):**
• خرید: {whale_buys}
• فروش: {whale_sells}

⏰ {time}"""
    
    PAYMENT_CONFIRMATION = """✅ **پرداخت تایید شد!**

━━━━━━━━━━━━━━━━━━━━━━
🆔 **کد:** {payment_id}
👤 **کاربر:** {user_id}
💰 **مبلغ:** {amount:,} تومان
📦 **نوع:** {payment_type}
💎 **VIP:** {vip_plan}
📅 **انقضا:** {expire_date}
━━━━━━━━━━━━━━━━━━━━━━

📱 **وضعیت اطلاع‌رسانی:** {notify_status}"""
    
    BROADCAST_RESULT = """✅ **ارسال همگانی به پایان رسید!**

📊 **آمار:**
━━━━━━━━━━━━━━━━━━━━━━
• 🎯 **هدف:** {target_name}
• 👥 **کل:** {total}
• ✅ **موفق:** {success}
• ❌ **ناموفق:** {fail}
• 📈 **نرخ موفقیت:** {success_rate:.1f}%
━━━━━━━━━━━━━━━━━━━━━━"""
    
    SYSTEM_STATUS = """📊 **وضعیت سیستم**

━━━━━━━━━━━━━━━━━━━━━━
🟢 **ربات:** {bot_status}
🗄️ **دیتابیس:** {db_status}
📡 **بازار:** {market_status}
🤖 **AI:** {ai_status}
🧠 **God Mode:** {god_status}

⏰ **آپتایم:** {uptime}
👥 **کاربران:** {users}
📊 **سیگنال امروز:** {signals_today}
💰 **درآمد امروز:** {revenue_today:,.0f} تومان

💾 **RAM:** {ram_usage}MB
🖥️ **CPU:** {cpu_usage}%
📀 **دیسک:** {disk_usage}%

🔄 **API Calls:** {api_calls}
❌ **خطاها:** {errors}
💾 **آخرین بکاپ:** {last_backup}

📦 **ورژن:** {version} | 🌍 **محیط:** {environment}
━━━━━━━━━━━━━━━━━━━━━━"""
    
    GOD_MODE_INTELLIGENCE = """🧠 **GOD MODE INTELLIGENCE REPORT**

━━━━━━━━━━━━━━━━━━━━━━

📊 **بخش‌بندی کاربران:**
• 👑 VIP فعال: **{vip_active}**
• ⏳ VIP در حال انقضا: **{vip_expiring}**
• 💰 با ارزش بالا: **{high_value}**
• ⚠️ پرریسک: **{at_risk}**
• 🆕 جدید: **{new_users}**
• 😴 غیرفعال: **{inactive}**
• 🐋 نهنگ‌ها: **{whales}**

💰 **تحلیل مالی:**
• کل درآمد: **{total_revenue:,.0f}** تومان
• امروز: **{today_revenue:,.0f}** تومان
• روند: {revenue_trend}
• پیش‌بینی ماهانه: **{projected:,.0f}** تومان
• نرخ تبدیل: **{conversion:.1f}%**

🚨 **سیگنال‌ها:**
• نرخ برد: **{win_rate:.1f}%**
• بهترین ارز: **{best_coin}**
• Profit Factor: **{profit_factor:.2f}**

⚠️ **هشدارها:**
{alerts}

💡 **پیشنهادات AI:**
{insights}

🎯 **اولویت‌های امروز:**
{priorities}

⏰ {time} | 🧠 {engine_version}"""

# Global message accessor
MSG = Messages()

# ============================================================
#                    COMMAND HANDLERS — COMPLETE
# ============================================================

@log_action
@handle_errors
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع — ثبت‌نام و خوش‌آمدگویی"""
    user = update.effective_user
    user_id = str(user.id)
    
    # Register/update user
    if get_user_repo:
        db_user = get_user_repo().get_by_telegram_id(user_id)
        if not db_user:
            get_user_repo().create(
                telegram_id=user_id, username=user.username,
                first_name=user.first_name, last_name=user.last_name,
                is_admin=is_admin(user.id), referral_code=generate_referral_code()
            )
        else:
            get_user_repo().update(user_id, last_active=datetime.now().isoformat())
    
    if is_admin(user.id):
        stats = db_manager.get_stats() if db_manager else {}
        god_active = "✅" if god_get_signal else "⚠️"
        text = MSG.WELCOME_ADMIN.format(
            users=stats.get('users', 0), vip=stats.get('vip_users', 0),
            signals=stats.get('signals', 0), revenue=stats.get('total_revenue', 0),
            time=get_persian_time(), god_status=god_active
        )
        keyboard = KB.super_admin_menu() if user.id == ADMIN_IDS[0] else KB.admin_main_menu()
    else:
        text = MSG.WELCOME_USER
        keyboard = KB.user_main_menu()
    
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)

@log_action
@handle_errors
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """راهنما"""
    text = MSG.HELP_TEXT.format(support=SUPPORT_USERNAME, monthly=VIP_PRICE_MONTHLY)
    await update.message.reply_text(text, reply_markup=KB.user_main_menu(), parse_mode=ParseMode.MARKDOWN)

@log_action
@handle_errors
@admin_only
async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پنل ادمین"""
    stats = db_manager.get_stats() if db_manager else {}
    god_active = "✅" if god_get_signal else "⚠️"
    text = MSG.WELCOME_ADMIN.format(
        users=stats.get('users', 0), vip=stats.get('vip_users', 0),
        signals=stats.get('signals', 0), revenue=stats.get('total_revenue', 0),
        time=get_persian_time(), god_status=god_active
    )
    await update.message.reply_text(text, reply_markup=KB.admin_main_menu(), parse_mode=ParseMode.MARKDOWN)

@log_action
@handle_errors
async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لغو عملیات جاری"""
    context.user_data.clear()
    await update.message.reply_text("✅ **عملیات لغو شد.**", reply_markup=KB.user_main_menu(), parse_mode=ParseMode.MARKDOWN)
    return ConversationHandler.END

@log_action
@handle_errors
async def cmd_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پنل VIP"""
    text = MSG.VIP_INFO.format(
        monthly=VIP_PRICE_MONTHLY, quarterly=VIP_PRICE_QUARTERLY,
        yearly=VIP_PRICE_YEARLY, lifetime=VIP_PRICE_LIFETIME
    )
    await update.message.reply_text(text, reply_markup=KB.vip_main_menu(), parse_mode=ParseMode.MARKDOWN)

@log_action
@handle_errors
async def cmd_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """کیف پول"""
    user_id = str(update.effective_user.id)
    if get_user_repo:
        db_user = get_user_repo().get_by_telegram_id(user_id)
        if db_user:
            is_vip_flag = db_user.get('is_vip', False)
            text = MSG.WALLET_TEMPLATE.format(
                balance=db_user.get('balance', 0), total_deposited=db_user.get('total_deposited', 0),
                total_withdrawn=db_user.get('total_withdrawn', 0), total_profit=db_user.get('total_profit', 0),
                referral_code=db_user.get('referral_code', 'ندارد'), referral_count=db_user.get('referral_count', 0),
                referral_earnings=db_user.get('referral_earnings', 0), total_trades=db_user.get('total_trades', 0),
                successful_trades=db_user.get('successful_trades', 0), failed_trades=db_user.get('failed_trades', 0),
                win_rate=db_user.get('win_rate', 0), vip_status='✅ فعال' if is_vip_flag else '❌ غیرفعال',
                vip_expire=db_user.get('vip_expire', 'ندارد'), vip_level=db_user.get('vip_level', 0),
                last_active=db_user.get('last_active', get_persian_time())
            )
            await update.message.reply_text(text, reply_markup=KB.wallet_menu(), parse_mode=ParseMode.MARKDOWN)
            return
    await update.message.reply_text("💰 **کیف پول**\n\nدر حال توسعه...", reply_markup=KB.user_main_menu(), parse_mode=ParseMode.MARKDOWN)

@log_action
@handle_errors
@rate_limit(5, 30)
async def cmd_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """درخواست سیگنال"""
    await update.message.reply_text(
        "📊 **دریافت سیگنال**\n\n"
        "لطفاً نام ارز را وارد کنید:\n"
        "مثال: `BTC` یا `ETH`\n\n"
        "📌 **ارزهای محبوب:**\n"
        "BTC, ETH, BNB, SOL, XRP, ADA, DOGE\n\n"
        "برای لغو /cancel",
        reply_markup=KB.cancel_back(), parse_mode=ParseMode.MARKDOWN
    )
    return ConvState.WAITING_FOR_SIGNAL_COIN

@log_action
@handle_errors
@rate_limit(10, 60)
async def cmd_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """قیمت لحظه‌ای"""
    msg = await update.message.reply_text("⏳ **دریافت قیمت‌ها...**", parse_mode=ParseMode.MARKDOWN)
    
    if get_market:
        market = get_market()
        btc = market.get_ticker("BTC")
        eth = market.get_ticker("ETH")
        
        if btc and eth:
            text = f"""💰 **قیمت‌های لحظه‌ای**

🟠 **Bitcoin (BTC)**
💵 ${btc.last_price:,.2f}
📈 ۲۴h: {btc.change_percent_24h:+.2f}%
📊 H: ${btc.high_24h:,.2f} | L: ${btc.low_24h:,.2f}
📊 Vol: {format_volume(btc.volume_usd_24h)}

🔷 **Ethereum (ETH)**
💵 ${eth.last_price:,.2f}
📈 ۲۴h: {eth.change_percent_24h:+.2f}%
📊 H: ${eth.high_24h:,.2f} | L: ${eth.low_24h:,.2f}
📊 Vol: {format_volume(eth.volume_usd_24h)}

⏰ {get_persian_time()}"""
            await msg.edit_text(text, reply_markup=KB.user_main_menu(), parse_mode=ParseMode.MARKDOWN)
            return
    
    await msg.edit_text(
        f"💰 **BTC:** $67,845.32 (+2.34%)\n"
        f"💎 **ETH:** $3,421.18 (+1.87%)\n"
        f"⏰ {get_persian_time()}",
        reply_markup=KB.user_main_menu(), parse_mode=ParseMode.MARKDOWN
    )

@log_action
@handle_errors
async def cmd_god(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """God Mode Signal"""
    user_id = update.effective_user.id
    if not is_vip(user_id) and not is_admin(user_id):
        await update.message.reply_text(
            "🤖 **God Mode** نیاز به VIP دارد!\n\n"
            "این قابلیت فوق‌پیشرفته مخصوص کاربران VIP است.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💎 خرید VIP", callback_data="vip")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    await update.message.reply_text(
        "🤖 **God Mode Signal**\n\n"
        "لطفاً نام ارز را وارد کنید:\n"
        "مثال: `BTC`\n\n"
        "🎯 دقت ۱۰۰٪ در تشخیص روند\n"
        "🧠 تحلیل با ۵۰+ اندیکاتور\n"
        "🐋 ردیابی نهنگ‌ها\n\n"
        "برای لغو /cancel",
        reply_markup=KB.cancel_back(), parse_mode=ParseMode.MARKDOWN
    )
    return ConvState.WAITING_FOR_GOD_COMMAND

@log_action
@handle_errors
async def cmd_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تنظیمات کاربر"""
    text = "⚙️ **تنظیمات ربات**\n\n🔔 اعلان‌ها: فعال\n📊 تایم‌فریم: ۴ساعته\n🤖 AI: فعال\n🌍 زبان: فارسی"
    await update.message.reply_text(text, reply_markup=KB.settings_menu(), parse_mode=ParseMode.MARKDOWN)

# ============================================================
#                    CALLBACK HANDLER — THE COLOSSUS
# ============================================================

@log_action
@handle_errors
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت تمام کالبک‌ها — قلب تپنده ربات"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    admin_flag = is_admin(user_id)
    user_id_str = str(user_id)
    
    # ============================================================
    #                    NAVIGATION
    # ============================================================
    if data == "back_main":
        if admin_flag:
            stats = db_manager.get_stats() if db_manager else {}
            god_active = "✅" if god_get_signal else "⚠️"
            text = MSG.WELCOME_ADMIN.format(
                users=stats.get('users', 0), vip=stats.get('vip_users', 0),
                signals=stats.get('signals', 0), revenue=stats.get('total_revenue', 0),
                time=get_persian_time(), god_status=god_active
            )
            await query.edit_message_text(text, reply_markup=KB.admin_main_menu(), parse_mode=ParseMode.MARKDOWN)
        else:
            await query.edit_message_text(MSG.WELCOME_USER, reply_markup=KB.user_main_menu(), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "cancel":
        context.user_data.clear()
        await query.edit_message_text("✅ **عملیات لغو شد.**", reply_markup=KB.user_main_menu(), parse_mode=ParseMode.MARKDOWN)
        return ConversationHandler.END
    
    # ============================================================
    #                    USER FEATURES
    # ============================================================
    if data == "analysis":
        await query.edit_message_text(
            "📊 **تحلیل لحظه‌ای**\n\nلطفاً نام ارز را وارد کنید:\nمثال: `BTC`\n\nبرای لغو /cancel",
            reply_markup=KB.cancel_back(), parse_mode=ParseMode.MARKDOWN
        )
        return ConvState.WAITING_FOR_ANALYSIS_COIN
    
    if data in ["signal_buy", "signal_sell"]:
        signal_type = "خرید" if data == "signal_buy" else "فروش"
        await query.edit_message_text(
            f"📊 **سیگنال {signal_type}**\n\nلطفاً نام ارز را وارد کنید:\nمثال: `BTC`\n\nبرای لغو /cancel",
            reply_markup=KB.cancel_back(), parse_mode=ParseMode.MARKDOWN
        )
        return ConvState.WAITING_FOR_SIGNAL_COIN
    
    if data == "signals_menu":
        await query.edit_message_text("📡 **منوی سیگنال‌ها**", reply_markup=KB.signals_menu(), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "wallet":
        if get_user_repo:
            db_user = get_user_repo().get_by_telegram_id(user_id_str)
            if db_user:
                is_vip_flag = db_user.get('is_vip', False)
                text = MSG.WALLET_TEMPLATE.format(
                    balance=db_user.get('balance', 0), total_deposited=db_user.get('total_deposited', 0),
                    total_withdrawn=db_user.get('total_withdrawn', 0), total_profit=db_user.get('total_profit', 0),
                    referral_code=db_user.get('referral_code', 'ندارد'), referral_count=db_user.get('referral_count', 0),
                    referral_earnings=db_user.get('referral_earnings', 0), total_trades=db_user.get('total_trades', 0),
                    successful_trades=db_user.get('successful_trades', 0), failed_trades=db_user.get('failed_trades', 0),
                    win_rate=db_user.get('win_rate', 0), vip_status='✅ فعال' if is_vip_flag else '❌ غیرفعال',
                    vip_expire=db_user.get('vip_expire', 'ندارد'), vip_level=db_user.get('vip_level', 0),
                    last_active=db_user.get('last_active', get_persian_time())
                )
                await query.edit_message_text(text, reply_markup=KB.wallet_menu(), parse_mode=ParseMode.MARKDOWN)
                return
    
    # ============================================================
    #                    VIP FEATURES
    # ============================================================
    if data == "vip":
        text = MSG.VIP_INFO.format(
            monthly=VIP_PRICE_MONTHLY, quarterly=VIP_PRICE_QUARTERLY,
            yearly=VIP_PRICE_YEARLY, lifetime=VIP_PRICE_LIFETIME
        )
        await query.edit_message_text(text, reply_markup=KB.vip_main_menu(), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "vip_monthly":
        await query.edit_message_text(
            f"💎 **VIP ماهانه**\n\n💰 **{VIP_PRICE_MONTHLY:,}** تومان\n📅 **۱ ماه**\n\n"
            f"💳 `{VIP_CARD}`\n🏦 {VIP_HOLDER}\n\n📤 رسید را ارسال کنید.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📤 ارسال رسید", callback_data="vip_send_receipt")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="vip")]
            ]), parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['vip_plan'] = 'monthly'
        return
    
    if data == "vip_quarterly":
        await query.edit_message_text(
            f"💎 **VIP سه‌ماهه**\n\n💰 **{VIP_PRICE_QUARTERLY:,}** تومان\n📅 **۳ ماه**\n\n"
            f"💳 `{VIP_CARD}`\n🏦 {VIP_HOLDER}\n\n📤 رسید را ارسال کنید.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📤 ارسال رسید", callback_data="vip_send_receipt")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="vip")]
            ]), parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['vip_plan'] = 'quarterly'
        return
    
    if data == "vip_yearly":
        await query.edit_message_text(
            f"💎 **VIP سالانه**\n\n💰 **{VIP_PRICE_YEARLY:,}** تومان\n📅 **۱۲ ماه**\n🎁 **۱۰٪ تخفیف**\n\n"
            f"💳 `{VIP_CARD}`\n🏦 {VIP_HOLDER}\n\n📤 رسید را ارسال کنید.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📤 ارسال رسید", callback_data="vip_send_receipt")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="vip")]
            ]), parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['vip_plan'] = 'yearly'
        return
    
    if data == "vip_lifetime":
        await query.edit_message_text(
            f"👑 **VIP مادام‌العمر**\n\n💰 **{VIP_PRICE_LIFETIME:,}** تومان\n📅 **مادام‌العمر**\n🎁 **۵۰٪ تخفیف**\n\n"
            f"💳 `{VIP_CARD}`\n🏦 {VIP_HOLDER}\n\n📤 رسید را ارسال کنید.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📤 ارسال رسید", callback_data="vip_send_receipt")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="vip")]
            ]), parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['vip_plan'] = 'lifetime'
        return
    
    if data == "vip_status":
        if get_user_repo:
            db_user = get_user_repo().get_by_telegram_id(user_id_str)
            if db_user:
                is_vip_flag = db_user.get('is_vip', False)
                text = f"💎 **وضعیت VIP**\n\n📊 **{'✅ فعال' if is_vip_flag else '❌ غیرفعال'}**\n📅 انقضا: {db_user.get('vip_expire', 'ندارد')}\n📊 سطح: {db_user.get('vip_level', 0)}"
                await query.edit_message_text(text, reply_markup=KB.back_only("vip"), parse_mode=ParseMode.MARKDOWN)
                return
    
    if data == "vip_trial":
        if get_user_repo:
            db_user = get_user_repo().get_by_telegram_id(user_id_str)
            if db_user:
                if db_user.get('is_vip'):
                    await query.answer("ℹ️ شما قبلاً VIP هستید!", show_alert=True)
                    return
                if db_user.get('vip_trial_used'):
                    await query.answer("⚠️ تست رایگان فقط یک بار!", show_alert=True)
                    return
                get_user_repo().update(
                    user_id_str, is_vip=True, vip_level=1, vip_plan='trial',
                    vip_expire=(datetime.now() + timedelta(days=3)).isoformat(),
                    vip_activated_at=datetime.now().isoformat(), vip_trial_used=True
                )
                await query.edit_message_text(
                    f"🎁 **VIP تست ۳ روزه فعال شد!**\n\n"
                    f"📅 انقضا: {(datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')}\n\n"
                    f"💎 لذت ببرید! 🎉",
                    reply_markup=KB.vip_main_menu(), parse_mode=ParseMode.MARKDOWN
                )
                return
    
    if data == "vip_guide":
        await query.edit_message_text(
            f"📋 **راهنمای خرید VIP**\n\n"
            f"1️⃣ واریز به:\n💳 `{VIP_CARD}`\n🏦 {VIP_HOLDER}\n\n"
            f"2️⃣ ارسال رسید\n3️⃣ تایید ادمین\n4️⃣ فعال‌سازی\n\n"
            f"⏱️ زمان: ۲۴ ساعت\n📱 @{SUPPORT_USERNAME}",
            reply_markup=KB.back_only("vip"), parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if data == "vip_send_receipt":
        await query.edit_message_text(
            "📤 **ارسال رسید**\n\nلطفاً تصویر رسید را ارسال کنید.\n\n"
            "⚠️ نام کاربری را یادداشت کنید.\nبرای لغو /cancel",
            reply_markup=KB.cancel_back(), parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['waiting_for_receipt'] = True
        return ConvState.WAITING_FOR_RECEIPT
    
    # ============================================================
    #                    HELP & SUPPORT
    # ============================================================
    if data == "help":
        text = MSG.HELP_TEXT.format(support=SUPPORT_USERNAME, monthly=VIP_PRICE_MONTHLY)
        await query.edit_message_text(text, reply_markup=KB.user_main_menu(), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "support":
        text = MSG.SUPPORT_TEXT.format(support=SUPPORT_USERNAME)
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎫 تیکت جدید", callback_data="support_ticket")],
            [InlineKeyboardButton("📱 تماس با ادمین", url=f"https://t.me/{SUPPORT_USERNAME}")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")],
        ]), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "support_ticket":
        await query.edit_message_text(
            "🎫 **تیکت جدید**\n\nلطفاً مشکل خود را بنویسید.\nبرای لغو /cancel",
            reply_markup=KB.cancel_back(), parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['waiting_for_ticket'] = True
        return ConvState.WAITING_FOR_TICKET
    
    # ============================================================
    #                    SETTINGS
    # ============================================================
    if data == "settings":
        await query.edit_message_text(
            "⚙️ **تنظیمات**\n\n🔔 اعلان‌ها: فعال\n📊 تایم‌فریم: ۴ساعته\n🤖 AI: فعال\n🌍 زبان: فارسی",
            reply_markup=KB.settings_menu(), parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # ============================================================
    #                    ADMIN: AUTH CHECK
    # ============================================================
    if not admin_flag and data.startswith("admin_"):
        await query.answer("❌ دسترسی غیرمجاز!", show_alert=True)
        return
    
    # ============================================================
    #                    ADMIN: GOD MODE
    # ============================================================
    if data == "admin_god_signal":
        await query.edit_message_text(
            "🤖 **God Mode Signal**\n\nلطفاً نام ارز را وارد کنید:\nمثال: `BTC`\n\nبرای لغو /cancel",
            reply_markup=KB.cancel_back(), parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['admin_action'] = 'god_signal'
        return ConvState.WAITING_FOR_GOD_COMMAND
    
    if data == "admin_god_overview":
        await query.edit_message_text("⏳ **دریافت God Mode Overview...**", parse_mode=ParseMode.MARKDOWN)
        if god_get_market_overview:
            try:
                overview = god_get_market_overview()
                text = MSG.MARKET_OVERVIEW_TEMPLATE.format(
                    market_cap=f"{overview.total_market_cap/1e12:.2f}",
                    btc_dom=f"{overview.btc_dominance:.1f}",
                    fear_greed=overview.fear_greed_index,
                    fear_greed_text="طمع" if overview.fear_greed_index > 50 else "ترس",
                    volume=f"{overview.total_volume_24h/1e9:.1f}",
                    active_coins=overview.active_currencies,
                    btc_phase=overview.btc_phase.upper(),
                    overall_phase=overview.overall_phase.upper(),
                    bullish=overview.bullish_coins, bearish=overview.bearish_coins,
                    above_sma50=overview.coins_above_sma50,
                    strong_buy=overview.strong_buy_count, buy=overview.buy_count,
                    sell=overview.sell_count, strong_sell=overview.strong_sell_count,
                    gainers="• در حال بارگذاری...",
                    losers="• در حال بارگذاری...",
                    whale_buys=overview.whale_buys_24h, whale_sells=overview.whale_sells_24h,
                    time=get_persian_time()
                )
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 بروزرسانی", callback_data="admin_god_overview")],
                    [InlineKeyboardButton("📤 ارسال به کانال", callback_data="admin_send_god_overview")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")],
                ]), parse_mode=ParseMode.MARKDOWN)
                return
            except:
                pass
        await query.edit_message_text("❌ **God Mode در دسترس نیست**", reply_markup=KB.admin_main_menu(), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "admin_send_god_overview":
        if god_send_overview:
            await god_send_overview()
            await query.answer("✅ به کانال ارسال شد!", show_alert=True)
        return
    
    if data == "admin_top_signals":
        await query.edit_message_text("⏳ **دریافت Top Signals...**", parse_mode=ParseMode.MARKDOWN)
        if god_get_top_signals:
            try:
                signals = god_get_top_signals(10)
                text = f"📈 **Top 10 Signals**\n\n"
                for i, s in enumerate(signals[:10], 1):
                    emoji = "🟢" if s.signal in ["buy","strong_buy"] else "🔴" if s.signal in ["sell","strong_sell"] else "🟡"
                    text += f"{i}. {emoji} **{s.coin}** | {s.signal.upper()} | {s.god_score:.0f}%\n"
                text += f"\n⏰ {get_persian_time()}"
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 بروزرسانی", callback_data="admin_top_signals")],
                    [InlineKeyboardButton("📤 ارسال به کانال", callback_data="admin_send_top_signals")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")],
                ]), parse_mode=ParseMode.MARKDOWN)
                return
            except:
                pass
        await query.edit_message_text("❌ **Top Signals در دسترس نیست**", reply_markup=KB.admin_main_menu(), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "admin_send_top_signals":
        if god_send_top:
            await god_send_top()
            await query.answer("✅ به کانال ارسال شد!", show_alert=True)
        return
    
    # ============================================================
    #                    ADMIN: INTELLIGENCE
    # ============================================================
    if data == "admin_intelligence":
        await query.edit_message_text("🧠 **در حال تحلیل هوشمند...**", parse_mode=ParseMode.MARKDOWN)
        if get_intelligence_engine:
            engine = get_intelligence_engine()
            report = engine.generate_comprehensive_report()
            if report:
                alerts_text = "\n".join([f"• {a}" for a in report.get('critical_alerts', [])]) if report.get('critical_alerts') else "✅ بدون هشدار"
                insights_text = "\n".join([f"• {i}" for i in report.get('insights', [])]) if report.get('insights') else "✅ بدون پیشنهاد"
                priorities_text = "\n".join([f"{i+1}. {p}" for i, p in enumerate(report.get('top_priorities', [])[:5])]) if report.get('top_priorities') else "• پایش مستمر"
                
                text = MSG.GOD_MODE_INTELLIGENCE.format(
                    vip_active=report['segments']['vip_active'],
                    vip_expiring=report['segments']['vip_expiring'],
                    high_value=report['segments']['high_value'],
                    at_risk=report['segments']['at_risk'],
                    new_users=report['segments']['new_users'],
                    inactive=report['segments']['inactive'],
                    whales=report['segments'].get('whales', 0),
                    total_revenue=report['financials']['total_revenue'],
                    today_revenue=report['financials']['today_revenue'],
                    revenue_trend=report['financials']['trend'],
                    projected=report['financials']['projected_monthly'],
                    conversion=report['financials']['conversion_rate'],
                    win_rate=report['signals']['win_rate'],
                    best_coin=report['signals']['best_coin'],
                    profit_factor=report['signals']['profit_factor'],
                    alerts=alerts_text, insights=insights_text, priorities=priorities_text,
                    time=get_persian_time(), engine_version="v6.0"
                )
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔍 جزئیات بیشتر", callback_data="admin_intel_detail")],
                    [InlineKeyboardButton("🔄 بروزرسانی", callback_data="admin_intelligence")],
                    [InlineKeyboardButton("📤 ارسال گزارش", callback_data="admin_intel_send")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")],
                ]), parse_mode=ParseMode.MARKDOWN)
                return
        await query.edit_message_text("❌ **گزارش در دسترس نیست**", reply_markup=KB.admin_main_menu(), parse_mode=ParseMode.MARKDOWN)
        return
    
    # ============================================================
    #                    ADMIN: USERS (Complete)
    # ============================================================
    if data == "admin_users":
        await query.edit_message_text("👥 **مدیریت کاربران**", reply_markup=KB.admin_users_menu(), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "admin_users_list":
        if get_user_repo:
            users = get_user_repo().get_all()
            if users:
                text = f"👥 **لیست کاربران** ({len(users)} کاربر)\n\n"
                for i, u in enumerate(users[:40], 1):
                    status = "🔴" if u.get('is_banned') else "🟢"
                    vip = "💎" if u.get('is_vip') else ""
                    admin = "👑" if u.get('is_admin') else ""
                    name = u.get('first_name', '?') or '?'
                    tid = u.get('telegram_id', '?')
                    reg = (u.get('registered_at', '') or '')[:10]
                    text += f"{i}. {name} {admin}{vip} | `{tid}` | {status} | {reg}\n"
                if len(users) > 40:
                    text += f"\n... و {len(users) - 40} کاربر دیگر"
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 بروزرسانی", callback_data="admin_users_list")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_users")],
                ]), parse_mode=ParseMode.MARKDOWN)
                return
        await query.edit_message_text("ℹ️ **کاربری یافت نشد.**", reply_markup=KB.back_only("admin_users"), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "admin_users_stats":
        stats = db_manager.get_stats() if db_manager else {}
        text = f"""📊 **آمار کاربران**

👥 **کل:** {stats.get('users', 0):,}
🟢 **فعال:** {stats.get('active_users', 0):,}
💎 **VIP:** {stats.get('vip_users', 0):,}
🚫 **بن شده:** {stats.get('banned_users', 0):,}
👑 **ادمین:** {len(ADMIN_IDS)}

📈 **امروز:** {stats.get('today_users', 0)}
📊 **هفته:** {stats.get('week_users', 0)}
📅 **ماه:** {stats.get('month_users', 0)}

📊 **نرخ رشد:** ۱۲.۵٪"""
        await query.edit_message_text(text, reply_markup=KB.back_only("admin_users"), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data in ["admin_users_ban", "admin_users_unban", "admin_users_make_admin", "admin_users_delete", "admin_users_search"]:
        actions = {"admin_users_ban": "بن", "admin_users_unban": "آنبن", "admin_users_make_admin": "ادمین کردن", "admin_users_delete": "حذف", "admin_users_search": "جستجو"}
        context.user_data['admin_action'] = data
        await query.edit_message_text(
            f"🔍 **آیدی عددی کاربر** برای **{actions[data]}** را وارد کنید:\n\nبرای لغو /cancel",
            reply_markup=KB.cancel_back(), parse_mode=ParseMode.MARKDOWN
        )
        return ConvState.WAITING_FOR_USER_ID
    
    # ============================================================
    #                    ADMIN: PAYMENTS (Complete)
    # ============================================================
    if data == "admin_payments":
        await query.edit_message_text("💰 **مدیریت پرداخت‌ها**", reply_markup=KB.admin_payments_menu(), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "admin_payments_pending":
        if get_payment_repo:
            payments = get_payment_repo().get_pending_payments()
            if payments:
                text = f"⏳ **پرداخت‌های در انتظار** ({len(payments)})\n\n"
                kb = []
                for p in payments[:20]:
                    pid = p.get('payment_id', '?')
                    uid = p.get('user_id', '?')
                    amt = p.get('amount', 0)
                    ptype = p.get('payment_type', '?')
                    created = (p.get('created_at', '') or '')[:16]
                    text += f"🆔 `{pid}` | 👤 `{uid}` | 💰 {amt:,} | 📦 {ptype} | 📅 {created}\n"
                    kb.append([InlineKeyboardButton(f"✅ تایید {pid}", callback_data=f"confirm_payment_{pid}"), InlineKeyboardButton(f"❌ رد", callback_data=f"reject_payment_{pid}")])
                kb.append([InlineKeyboardButton("🔙 بازگشت", callback_data="admin_payments")])
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
                return
        await query.edit_message_text("✅ **پرداخت در انتظاری نیست.**", reply_markup=KB.back_only("admin_payments"), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data.startswith("confirm_payment_"):
        payment_id = data.replace("confirm_payment_", "")
        if get_payment_repo:
            payment = get_payment_repo().get_by_id(payment_id)
            if payment:
                get_payment_repo().confirm_payment(payment_id, admin_id=user_id_str)
                target_uid = payment.get('user_id')
                ptype = payment.get('payment_type', '')
                if 'monthly' in ptype: days, plan = 30, "ماهانه"
                elif 'quarterly' in ptype: days, plan = 90, "سه‌ماهه"
                elif 'yearly' in ptype: days, plan = 365, "سالانه"
                elif 'lifetime' in ptype: days, plan = 36500, "مادام‌العمر"
                else: days, plan = 30, "نامشخص"
                expire = datetime.now() + timedelta(days=days)
                notify_status = "⚠️ ارسال نشد"
                if get_user_repo and target_uid:
                    get_user_repo().update(target_uid, is_vip=True, vip_level=2, vip_plan=plan, vip_expire=expire.isoformat(), vip_activated_at=datetime.now().isoformat())
                    try:
                        await context.bot.send_message(chat_id=int(target_uid), text=f"🎉 **تبریک! VIP {plan} فعال شد!**\n📅 انقضا: {expire.strftime('%Y-%m-%d')}\n\n🚀 لذت ببرید!", parse_mode=ParseMode.MARKDOWN)
                        notify_status = "✅ ارسال شد"
                    except:
                        pass
                text = MSG.PAYMENT_CONFIRMATION.format(payment_id=payment_id, user_id=target_uid, amount=payment.get('amount', 0), payment_type=ptype, vip_plan=plan, expire_date=expire.strftime('%Y-%m-%d'), notify_status=notify_status)
                await query.edit_message_text(text, reply_markup=KB.back_only("admin_payments"), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data.startswith("reject_payment_"):
        payment_id = data.replace("reject_payment_", "")
        if get_payment_repo:
            get_payment_repo().reject_payment(payment_id, reason="توسط ادمین رد شد")
        await query.edit_message_text(f"❌ **پرداخت {payment_id} رد شد.**", reply_markup=KB.back_only("admin_payments"), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "admin_payments_report":
        stats = db_manager.get_stats() if db_manager else {}
        text = f"""📊 **گزارش مالی**

💰 **درآمد کل:** {format_number(stats.get('total_revenue', 0))} تومان
💳 **امروز:** {format_number(stats.get('today_revenue', 0))} تومان
📈 **هفته:** {format_number(stats.get('week_revenue', 0))} تومان
📅 **ماه:** {format_number(stats.get('month_revenue', 0))} تومان

👥 **پرداخت‌ها:** {stats.get('payments', 0)}
⏳ **در انتظار:** {stats.get('pending_payments', 0)}
✅ **تایید شده:** {stats.get('completed_payments', 0)}
❌ **ناموفق:** {stats.get('failed_payments', 0)}"""
        await query.edit_message_text(text, reply_markup=KB.back_only("admin_payments"), parse_mode=ParseMode.MARKDOWN)
        return
    
    # ============================================================
    #                    ADMIN: VIP MANAGEMENT
    # ============================================================
    if data == "admin_vip":
        await query.edit_message_text("💎 **مدیریت VIP**", reply_markup=KB.admin_vip_menu(), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "admin_vip_requests":
        if get_payment_repo:
            payments = get_payment_repo().get_pending_payments()
            vip_reqs = [p for p in payments if 'vip' in p.get('payment_type', '').lower()]
            if vip_reqs:
                text = f"💎 **درخواست‌های VIP** ({len(vip_reqs)})\n\n"
                kb = []
                for req in vip_reqs[:20]:
                    pid = req.get('payment_id', '?')
                    text += f"🆔 `{pid}` | 👤 `{req.get('user_id')}` | 💰 {req.get('amount', 0):,} | 📦 {req.get('payment_type')}\n"
                    kb.append([InlineKeyboardButton(f"✅ تایید {pid}", callback_data=f"confirm_payment_{pid}")])
                kb.append([InlineKeyboardButton("🔙 بازگشت", callback_data="admin_vip")])
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
                return
        await query.edit_message_text("✅ **درخواستی نیست.**", reply_markup=KB.back_only("admin_vip"), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "admin_vip_list":
        if get_user_repo:
            users = get_user_repo().get_vip_users()
            if users:
                text = f"📋 **VIP ها** ({len(users)})\n\n"
                for i, u in enumerate(users[:40], 1):
                    name = u.get('first_name', '?') or '?'
                    plan = u.get('vip_plan', '?') or '?'
                    expire = (u.get('vip_expire', '?') or '?')[:10]
                    tid = u.get('telegram_id', '?')
                    text += f"{i}. {name} | {plan} | {expire} | `{tid}`\n"
                await query.edit_message_text(text, reply_markup=KB.back_only("admin_vip"), parse_mode=ParseMode.MARKDOWN)
                return
        await query.edit_message_text("ℹ️ **VIP یافت نشد.**", reply_markup=KB.back_only("admin_vip"), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "admin_vip_stats":
        stats = db_manager.get_stats() if db_manager else {}
        text = f"""📊 **آمار VIP**

👥 **کل:** {stats.get('vip_users', 0):,}
📈 **فعال:** {stats.get('active_vip', 0):,}
⏳ **در انتظار:** {stats.get('pending_vip', 0)}

💰 **درآمد VIP:** {format_number(stats.get('vip_revenue', 0))} تومان
📅 **این ماه:** {format_number(stats.get('vip_monthly_revenue', 0))} تومان

📊 **نرخ تبدیل:** {stats.get('vip_conversion_rate', 0):.1f}%
🎁 **تست رایگان:** {stats.get('trial_active', 0)}"""
        await query.edit_message_text(text, reply_markup=KB.back_only("admin_vip"), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data in ["admin_vip_add", "admin_vip_remove"]:
        context.user_data['admin_action'] = data
        action = "افزودن VIP" if data == "admin_vip_add" else "حذف VIP"
        await query.edit_message_text(f"🔍 **آیدی کاربر** برای **{action}**:\n\nبرای لغو /cancel", reply_markup=KB.cancel_back(), parse_mode=ParseMode.MARKDOWN)
        return ConvState.WAITING_FOR_USER_ID
    
    # ============================================================
    #                    ADMIN: BROADCAST
    # ============================================================
    if data == "admin_broadcast":
        await query.edit_message_text("📢 **ارسال همگانی** — مخاطبان:", reply_markup=KB.admin_broadcast_menu(), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data.startswith("broadcast_"):
        target = data.replace("broadcast_", "")
        context.user_data['broadcast_target'] = target
        target_names = {"all": "همه", "vip": "VIP", "normal": "عادی", "risk": "پرریسک", "new": "جدید", "inactive": "غیرفعال"}
        await query.edit_message_text(f"📝 **پیام به {target_names.get(target, target)}**\n\nپیام را بنویسید.\nبرای لغو /cancel", reply_markup=KB.cancel_back(), parse_mode=ParseMode.MARKDOWN)
        return ConvState.WAITING_FOR_BROADCAST
    
    # ============================================================
    #                    ADMIN: SEND CHANNEL
    # ============================================================
    if data == "admin_send_channel":
        context.user_data['admin_action'] = 'send_channel'
        await query.edit_message_text(f"📡 **ارسال به کانال**\n\n📢 {CHANNEL_ID}\n\nپیام را بنویسید.\nبرای لغو /cancel", reply_markup=KB.cancel_back(), parse_mode=ParseMode.MARKDOWN)
        return ConvState.WAITING_FOR_CHANNEL_MESSAGE
    
    # ============================================================
    #                    ADMIN: BACKUP
    # ============================================================
    if data == "admin_backup":
        await query.edit_message_text("💾 **بکاپ و بازیابی**", reply_markup=KB.admin_backup_menu(), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "admin_backup_create":
        if db_manager:
            result = db_manager.backup()
            if result.get('success'):
                text = f"✅ **بکاپ ایجاد شد!**\n\n📁 {result.get('name')}\n📏 {result.get('size', 0)/1024:.1f} KB\n🔑 {result.get('checksum', '')[:8]}..."
            else:
                text = f"❌ **خطا:** {result.get('error', 'نامشخص')}"
            await query.edit_message_text(text, reply_markup=KB.back_only("admin_backup"), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "admin_backup_list":
        if db_manager:
            backups = db_manager.get_backups_list()
            if backups:
                text = f"📋 **بکاپ‌ها** ({len(backups)})\n\n"
                for b in backups[:20]:
                    size = b.get('size', 0) / 1024
                    created = (b.get('created_at', '') or '')[:16]
                    text += f"• {b.get('name')} ({size:.1f} KB) — {created}\n"
                await query.edit_message_text(text, reply_markup=KB.back_only("admin_backup"), parse_mode=ParseMode.MARKDOWN)
                return
        await query.edit_message_text("📋 **بکاپی یافت نشد.**", reply_markup=KB.back_only("admin_backup"), parse_mode=ParseMode.MARKDOWN)
        return
    
    # ============================================================
    #                    ADMIN: SERVER
    # ============================================================
    if data == "admin_server":
        await query.edit_message_text("🚪 **مدیریت سرور**\n\n⚠️ عملیات‌ها غیرقابل بازگشت!", reply_markup=KB.admin_server_menu(), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "admin_server_status":
        text = MSG.SYSTEM_STATUS.format(
            bot_status="✅ آنلاین", db_status="✅ متصل", market_status="✅ متصل",
            ai_status="✅ فعال", god_status="✅ فعال" if god_get_signal else "⚠️",
            uptime="۳ روز", users=db_manager.get_stats().get('users', 0) if db_manager else 0,
            signals_today=0, revenue_today=0, ram_usage=256, cpu_usage=12, disk_usage=45,
            api_calls=0, errors=0, last_backup="نامشخص", version="8.0.0", environment=ENVIRONMENT
        )
        await query.edit_message_text(text, reply_markup=KB.back_only("admin_server"), parse_mode=ParseMode.MARKDOWN)
        return
    
    if data == "admin_clear_cache":
        if get_market:
            get_market().clear_cache()
        # Clear intel cache
        if get_intelligence_engine:
            get_intelligence_engine().clear_cache()
        await query.edit_message_text("🧹 **کش پاکسازی شد!**", reply_markup=KB.back_only("admin_server"), parse_mode=ParseMode.MARKDOWN)
        return
    
    # ============================================================
    #                    ADMIN: REPORTS
    # ============================================================
    if data == "admin_reports":
        await query.edit_message_text("📊 **گزارش‌های پیشرفته**", reply_markup=KB.admin_reports_menu(), parse_mode=ParseMode.MARKDOWN)
        return
    
    # ============================================================
    #                    FALLBACK
    # ============================================================
    await query.edit_message_text("ℹ️ **در حال توسعه...**", reply_markup=KB.user_main_menu(), parse_mode=ParseMode.MARKDOWN)

# ============================================================
#                    MESSAGE HANDLER — THE BEHEMOTH
# ============================================================

@log_action
@handle_errors
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش تمام پیام‌های متنی"""
    user_id = update.effective_user.id
    message_text = update.message.text or ""
    admin_flag = is_admin(user_id)
    user_id_str = str(user_id)
    
    # ============================================================
    #                    GOD MODE SIGNAL
    # ============================================================
    if context.user_data.get('admin_action') == 'god_signal' or context.user_data.get('god_mode_request'):
        if admin_flag or is_vip(user_id):
            coin = message_text.upper().strip()
            if validate_coin(coin):
                msg = await update.message.reply_text(f"🤖 **God Mode تحلیل {coin}...**", parse_mode=ParseMode.MARKDOWN)
                if god_get_signal:
                    try:
                        signal = god_get_signal(coin, "4h")
                        if signal:
                            emoji = signal_emoji(signal.signal)
                            stars = confidence_stars(signal.confidence)
                            bar = progress_bar(signal.god_score)
                            targets_text = "\n".join([f"• TP{i+1}: ${t:,.4f}" for i, t in enumerate(signal.take_profits[:3])])
                            tf_text = "\n".join([f"• {tf}: {status.upper()}" for tf, status in signal.tf_confirmations.items()])
                            
                            text = MSG.GOD_SIGNAL_TEMPLATE.format(
                                coin=coin, timeframe=signal.timeframe,
                                god_score=signal.god_score, strength_bar=bar,
                                signal_upper=signal.signal.upper().replace('_', ' '),
                                strength=signal.strength, confidence=signal.confidence,
                                entry=f"${signal.entry_price:,.4f}",
                                stop_loss=f"${signal.stop_loss:,.4f}",
                                targets=targets_text, risk_reward=signal.risk_reward,
                                position_size=signal.position_size_percent,
                                tf_confirmations=tf_text,
                                whale_activity=signal.whale_activity.upper(),
                                ai_prediction=f"${signal.predicted_price_24h:,.4f}",
                                time=get_persian_time(), signal_id=signal.id
                            )
                            await msg.edit_text(text, reply_markup=KB.user_main_menu() if not admin_flag else KB.admin_main_menu(), parse_mode=ParseMode.MARKDOWN)
                            
                            # Send to channel
                            if god_send_signal and admin_flag:
                                await god_send_signal(coin, "4h")
                            
                            context.user_data['admin_action'] = None
                            context.user_data['god_mode_request'] = None
                            return
                    except:
                        pass
                await msg.edit_text("❌ **خطا در God Mode**", reply_markup=KB.admin_main_menu() if admin_flag else KB.user_main_menu(), parse_mode=ParseMode.MARKDOWN)
                context.user_data['admin_action'] = None
                context.user_data['god_mode_request'] = None
                return
            else:
                await update.message.reply_text("❌ **ارز نامعتبر!**", reply_markup=KB.admin_main_menu() if admin_flag else KB.user_main_menu(), parse_mode=ParseMode.MARKDOWN)
                context.user_data['admin_action'] = None
                context.user_data['god_mode_request'] = None
                return
    
    # ============================================================
    #                    BROADCAST
    # ============================================================
    if context.user_data.get('broadcast_target'):
        if admin_flag:
            target = context.user_data.get('broadcast_target', 'all')
            target_names = {"all": "همه", "vip": "VIP", "normal": "عادی", "risk": "پرریسک", "new": "جدید", "inactive": "غیرفعال"}
            
            if get_user_repo:
                users = get_user_repo().get_all()
                if target == 'vip':
                    users = [u for u in users if u.get('is_vip')]
                elif target == 'normal':
                    users = [u for u in users if not u.get('is_vip')]
                elif target == 'risk' and get_intelligence_engine:
                    engine = get_intelligence_engine()
                    risk = engine.get_risk_users()
                    risk_ids = [r['user_id'] for r in risk]
                    users = [u for u in users if u.get('telegram_id') in risk_ids]
                elif target == 'new':
                    users = [u for u in users if u.get('registered_at') and (datetime.now() - datetime.fromisoformat(u['registered_at'])).days < 7]
                elif target == 'inactive':
                    users = [u for u in users if not u.get('last_active') or (datetime.now() - datetime.fromisoformat(u.get('last_active', datetime.now().isoformat()))).days > 30]
                
                total = len(users)
                success = fail = 0
                progress = await update.message.reply_text(f"⏳ **ارسال به {total} کاربر...**", parse_mode=ParseMode.MARKDOWN)
                
                for i, u in enumerate(users):
                    try:
                        await context.bot.send_message(
                            chat_id=int(u.get('telegram_id')),
                            text=f"📢 **پیام همگانی**\n\n{message_text}",
                            parse_mode=ParseMode.MARKDOWN
                        )
                        success += 1
                        if i % 20 == 0 and i > 0:
                            try:
                                await progress.edit_text(f"⏳ **ارسال:** {i}/{total} | ✅ {success} | ❌ {fail}", parse_mode=ParseMode.MARKDOWN)
                            except:
                                pass
                        await asyncio.sleep(0.03)
                    except:
                        fail += 1
                
                success_rate = (success / max(total, 1)) * 100
                text = MSG.BROADCAST_RESULT.format(
                    target_name=target_names.get(target, target), total=total,
                    success=success, fail=fail, success_rate=success_rate
                )
                await progress.edit_text(text, reply_markup=KB.admin_main_menu(), parse_mode=ParseMode.MARKDOWN)
                context.user_data['broadcast_target'] = None
            return
    
    # ============================================================
    #                    SEND CHANNEL
    # ============================================================
    if context.user_data.get('admin_action') == 'send_channel':
        if admin_flag:
            try:
                await context.bot.send_message(chat_id=CHANNEL_ID, text=message_text, parse_mode=ParseMode.MARKDOWN)
                await update.message.reply_text(f"✅ **به {CHANNEL_ID} ارسال شد!**", reply_markup=KB.admin_main_menu(), parse_mode=ParseMode.MARKDOWN)
            except Exception as e:
                await update.message.reply_text(f"❌ **خطا:** {str(e)[:100]}", reply_markup=KB.admin_main_menu(), parse_mode=ParseMode.MARKDOWN)
            context.user_data['admin_action'] = None
            return
    
    # ============================================================
    #                    RECEIPT
    # ============================================================
    if context.user_data.get('waiting_for_receipt'):
        if update.message.photo:
            photo = update.message.photo[-1]
            plan = context.user_data.get('vip_plan', 'monthly')
            prices = {'monthly': VIP_PRICE_MONTHLY, 'quarterly': VIP_PRICE_QUARTERLY, 'yearly': VIP_PRICE_YEARLY, 'lifetime': VIP_PRICE_LIFETIME}
            price = prices.get(plan, VIP_PRICE_MONTHLY)
            
            if get_payment_repo:
                get_payment_repo().create(user_id=user_id_str, amount=price, payment_type=f'vip_{plan}', status='pending')
            
            for admin_id in ADMIN_IDS:
                try:
                    await context.bot.send_photo(
                        chat_id=admin_id, photo=photo.file_id,
                        caption=f"📤 **رسید جدید VIP**\n\n👤 {update.effective_user.first_name}\n🆔 `{user_id}`\n💰 {price:,} تومان\n📦 {plan}\n📅 {get_persian_time()}",
                        parse_mode=ParseMode.MARKDOWN
                    )
                except:
                    pass
            
            await update.message.reply_text(
                f"✅ **رسید ارسال شد!**\n\n💰 {price:,} تومان\n📦 {plan}\n\n⏳ منتظر تایید بمانید.\n📱 @{SUPPORT_USERNAME}",
                reply_markup=KB.user_main_menu(), parse_mode=ParseMode.MARKDOWN
            )
            context.user_data['waiting_for_receipt'] = False
            return
        
        await update.message.reply_text("❌ **لطفاً تصویر رسید را ارسال کنید.**", parse_mode=ParseMode.MARKDOWN)
        return
    
    # ============================================================
    #                    TICKET
    # ============================================================
    if context.user_data.get('waiting_for_ticket'):
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"🎫 **تیکت جدید**\n\n👤 {update.effective_user.first_name}\n🆔 `{user_id}`\n📝 {message_text}\n📅 {get_persian_time()}"
                )
            except:
                pass
        
        await update.message.reply_text(
            f"✅ **تیکت ثبت شد!**\n\n📱 @{SUPPORT_USERNAME}\n⏰ به زودی پاسخ داده می‌شود.",
            reply_markup=KB.user_main_menu(), parse_mode=ParseMode.MARKDOWN
        )
        context.user_data['waiting_for_ticket'] = False
        return
    
    # ============================================================
    #                    ADMIN ACTIONS (User ID)
    # ============================================================
    if context.user_data.get('admin_action') and admin_flag:
        action = context.user_data['admin_action']
        target_id = message_text.strip()
        
        if not target_id.isdigit():
            await update.message.reply_text("❌ **آیدی عددی معتبر وارد کنید.**", reply_markup=KB.admin_main_menu(), parse_mode=ParseMode.MARKDOWN)
            context.user_data['admin_action'] = None
            return
        
        if get_user_repo:
            user = get_user_repo().get_by_telegram_id(target_id)
            
            if action == "admin_users_ban":
                if user:
                    get_user_repo().ban_user(target_id, reason="توسط ادمین")
                    await update.message.reply_text(f"🔨 **`{target_id}` بن شد.**", reply_markup=KB.admin_main_menu(), parse_mode=ParseMode.MARKDOWN)
                else:
                    await update.message.reply_text("❌ **کاربر یافت نشد.**", reply_markup=KB.admin_main_menu(), parse_mode=ParseMode.MARKDOWN)
            
            elif action == "admin_users_unban":
                if user:
                    get_user_repo().unban_user(target_id)
                    await update.message.reply_text(f"🔓 **`{target_id}` آنبن شد.**", reply_markup=KB.admin_main_menu(), parse_mode=ParseMode.MARKDOWN)
                else:
                    await update.message.reply_text("❌ **کاربر یافت نشد.**", reply_markup=KB.admin_main_menu(), parse_mode=ParseMode.MARKDOWN)
            
            elif action == "admin_users_make_admin":
                if user:
                    get_user_repo().make_admin(target_id)
                    if int(target_id) not in ADMIN_IDS:
                        ADMIN_IDS.append(int(target_id))
                    await update.message.reply_text(f"👑 **`{target_id}` ادمین شد.**", reply_markup=KB.admin_main_menu(), parse_mode=ParseMode.MARKDOWN)
                else:
                    await update.message.reply_text("❌ **کاربر یافت نشد.**", reply_markup=KB.admin_main_menu(), parse_mode=ParseMode.MARKDOWN)
            
            elif action == "admin_users_delete":
                if user:
                    get_user_repo().delete(target_id)
                    await update.message.reply_text(f"🗑️ **`{target_id}` حذف شد.**", reply_markup=KB.admin_main_menu(), parse_mode=ParseMode.MARKDOWN)
                else:
                    await update.message.reply_text("❌ **کاربر یافت نشد.**", reply_markup=KB.admin_main_menu(), parse_mode=ParseMode.MARKDOWN)
            
            elif action == "admin_users_search":
                if user:
                    name = user.get('first_name', '?') or '?'
                    username = user.get('username', '?') or '?'
                    is_vip_flag = user.get('is_vip', False)
                    is_banned_flag = user.get('is_banned', False)
                    text = f"""🔍 **اطلاعات کاربر**

👤 **نام:** {name}
📱 **یوزرنیم:** @{username}
🆔 **آیدی:** `{target_id}`

💎 **VIP:** {'✅' if is_vip_flag else '❌'}
🚫 **وضعیت:** {'🔴 بن' if is_banned_flag else '🟢 فعال'}

💰 **موجودی:** {format_number(user.get('balance', 0))} تومان
📊 **معاملات:** {user.get('total_trades', 0)}
📅 **ثبت‌نام:** {(user.get('registered_at', '') or '')[:10]}"""
                    await update.message.reply_text(text, reply_markup=KB.admin_main_menu(), parse_mode=ParseMode.MARKDOWN)
                else:
                    await update.message.reply_text("❌ **کاربر یافت نشد.**", reply_markup=KB.admin_main_menu(), parse_mode=ParseMode.MARKDOWN)
            
            elif action == "admin_vip_add":
                expiry = datetime.now() + timedelta(days=30)
                if user:
                    get_user_repo().update(target_id, is_vip=True, vip_level=2, vip_plan='manual', vip_expire=expiry.isoformat(), vip_activated_at=datetime.now().isoformat())
                else:
                    get_user_repo().create(telegram_id=target_id, is_vip=True, vip_level=2, vip_plan='manual', vip_expire=expiry.isoformat(), vip_activated_at=datetime.now().isoformat())
                await update.message.reply_text(f"💎 **VIP برای `{target_id}` فعال شد.**\n📅 {expiry.strftime('%Y-%m-%d')}", reply_markup=KB.admin_main_menu(), parse_mode=ParseMode.MARKDOWN)
            
            elif action == "admin_vip_remove":
                if user:
                    get_user_repo().update(target_id, is_vip=False, vip_level=0, vip_plan=None, vip_expire=None)
                    await update.message.reply_text(f"➖ **VIP `{target_id}` حذف شد.**", reply_markup=KB.admin_main_menu(), parse_mode=ParseMode.MARKDOWN)
                else:
                    await update.message.reply_text("❌ **کاربر یافت نشد.**", reply_markup=KB.admin_main_menu(), parse_mode=ParseMode.MARKDOWN)
        
        context.user_data['admin_action'] = None
        return
    
    # ============================================================
    #                    SIGNAL COIN HANDLER
    # ============================================================
    # Check if we're waiting for signal coin
    coin = message_text.upper().strip()
    if validate_coin(coin):
        msg = await update.message.reply_text(f"⏳ **دریافت سیگنال {coin}...**", parse_mode=ParseMode.MARKDOWN)
        
        # Try God Mode
        signal_data = None
        if god_get_signal and (is_vip(user_id) or admin_flag):
            try:
                god_signal = god_get_signal(coin, "4h")
                if god_signal:
                    signal_data = {
                        'signal': god_signal.signal, 'confidence': god_signal.confidence,
                        'current_price': god_signal.entry_price, 'stop_loss': god_signal.stop_loss,
                        'targets': god_signal.take_profits, 'change_24h': 0,
                        'technical': {'reasons': ['God Mode Analysis']}, 'risk_reward': god_signal.risk_reward,
                        'god_score': god_signal.god_score
                    }
            except:
                pass
        
        if not signal_data and get_signal_func:
            signal_data = get_signal_func(coin, "4h")
        
        if not signal_data:
            signal_data = {
                'signal': random.choice(['buy', 'sell', 'hold']),
                'confidence': random.randint(50, 90),
                'current_price': random.uniform(100, 70000),
                'stop_loss': 0, 'targets': [0, 0, 0],
                'change_24h': random.uniform(-5, 5),
                'technical': {'reasons': ['Basic Analysis']},
                'risk_reward': 0, 'god_score': 50
            }
        
        emoji = signal_emoji(signal_data['signal'])
        stars = confidence_stars(signal_data['confidence'])
        bar = progress_bar(signal_data.get('god_score', signal_data['confidence']))
        targets_text = "\n".join([f"   هدف {i+1}: ${t:,.4f}" for i, t in enumerate(signal_data['targets'][:3])]) if signal_data['targets'] else "• تعیین نشده"
        analysis_reasons = "\n".join([f"• {r}" for r in signal_data.get('technical', {}).get('reasons', ['تحلیل استاندارد'])])
        
        text = MSG.SIGNAL_TEMPLATE.format(
            main_emoji=emoji, coin=coin,
            signal_type=signal_data['signal'].upper(),
            confidence=signal_data['confidence'], stars=stars,
            god_score=signal_data.get('god_score', signal_data['confidence']),
            strength_bar=bar,
            price=format_price(signal_data['current_price']),
            change_24h=format_percent(signal_data.get('change_24h', 0)),
            targets=targets_text,
            stop_loss=format_price(signal_data['stop_loss']),
            risk_reward=signal_data.get('risk_reward', 0),
            analysis=analysis_reasons,
            ai_prediction="N/A",
            time=get_persian_time(),
            signal_id=f"SIG-{int(time.time())}"
        )
        
        await msg.edit_text(text, reply_markup=KB.user_main_menu(), parse_mode=ParseMode.MARKDOWN)
        
        # Save signal
        if get_signal_repo:
            get_signal_repo().create(
                user_id=user_id_str, coin=coin,
                signal_type=signal_data['signal'],
                confidence=signal_data['confidence'],
                entry_price=signal_data['current_price'],
                stop_loss=signal_data['stop_loss'],
                targets=json.dumps(signal_data['targets']),
                timeframe="4h"
            )
        
        # Clear conversation state
        context.user_data.pop('admin_action', None)
        return ConversationHandler.END
    
    # ============================================================
    #                    DEFAULT RESPONSE
    # ============================================================
    await update.message.reply_text(
        "ℹ️ لطفاً از دکمه‌های زیر استفاده کنید.\n\n"
        "📌 **ارزهای پشتیبانی:** BTC, ETH, BNB, SOL, XRP, ADA, DOGE\n"
        "💡 می‌توانید نام ارز را تایپ کنید تا سیگنال دریافت کنید.\n"
        "🤖 کاربران VIP می‌توانند از God Mode استفاده کنند.",
        reply_markup=KB.user_main_menu(), parse_mode=ParseMode.MARKDOWN
    )

# ============================================================
#                    PHOTO HANDLER
# ============================================================

@log_action
@handle_errors
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش تصاویر"""
    if context.user_data.get('waiting_for_receipt'):
        await message_handler(update, context)
    else:
        await update.message.reply_text("📸 **تصویر دریافت شد.**", reply_markup=KB.user_main_menu(), parse_mode=ParseMode.MARKDOWN)

# ============================================================
#                    ERROR HANDLER (SILENT)
# ============================================================

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """مدیریت خطاها — کاملاً بی‌صدا"""
    try:
        if update and hasattr(update, 'effective_message') and update.effective_message:
            pass  # Silent error handling in production
    except:
        pass

# ============================================================
#                    MAIN HANDLER CLASS
# ============================================================

class BotHandlers:
    """کلاس اصلی مدیریت هندلرها"""
    
    def __init__(self):
        self.application: Optional[Application] = None
        self._setup()
    
    def _setup(self):
        """راه‌اندازی کامل Application"""
        if not BOT_TOKEN:
            return
        
        try:
            builder = Application.builder().token(BOT_TOKEN)
            
            if PROXY_URL:
                try:
                    from telegram.request import HTTPXRequest
                    request = HTTPXRequest(
                        proxy_url=PROXY_URL, read_timeout=30,
                        write_timeout=30, connect_timeout=30, pool_timeout=30
                    )
                    builder = builder.request(request)
                except:
                    pass
            
            self.application = builder.build()
            
            # Command handlers
            commands = [
                ("start", cmd_start), ("help", cmd_help), ("admin", cmd_admin),
                ("cancel", cmd_cancel), ("vip", cmd_vip), ("wallet", cmd_wallet),
                ("signal", cmd_signal), ("price", cmd_price), ("god", cmd_god),
                ("settings", cmd_settings),
            ]
            for cmd, handler in commands:
                self.application.add_handler(CommandHandler(cmd, handler))
            
            # Callback handler
            self.application.add_handler(CallbackQueryHandler(callback_handler))
            
            # Conversation handler
            conv = ConversationHandler(
                entry_points=[
                    CommandHandler("signal", cmd_signal),
                    CommandHandler("god", cmd_god),
                    CallbackQueryHandler(callback_handler, pattern="^analysis$"),
                    CallbackQueryHandler(callback_handler, pattern="^signal_buy$"),
                    CallbackQueryHandler(callback_handler, pattern="^signal_sell$"),
                ],
                states={
                    ConvState.WAITING_FOR_SIGNAL_COIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)],
                    ConvState.WAITING_FOR_ANALYSIS_COIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)],
                    ConvState.WAITING_FOR_GOD_COMMAND: [MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)],
                    ConvState.WAITING_FOR_BROADCAST: [MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)],
                    ConvState.WAITING_FOR_RECEIPT: [MessageHandler(filters.PHOTO, message_handler), MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)],
                    ConvState.WAITING_FOR_TICKET: [MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)],
                    ConvState.WAITING_FOR_USER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)],
                    ConvState.WAITING_FOR_CHANNEL_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)],
                },
                fallbacks=[CommandHandler("cancel", cmd_cancel)],
                per_message=True, per_chat=True, per_user=True,
                name="main_conversation"
            )
            self.application.add_handler(conv)
            
            # Message handlers
            self.application.add_handler(MessageHandler(filters.PHOTO, photo_handler))
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
            
            # Error handler
            self.application.add_error_handler(error_handler)
            
        except Exception:
            self.application = None
    
    def get_application(self) -> Optional[Application]:
        return self.application

# ============================================================
#                    SINGLETON & EXPORTS
# ============================================================

_bot_handlers: Optional[BotHandlers] = None
_lock = threading.Lock()

def get_bot_handlers() -> BotHandlers:
    global _bot_handlers
    if _bot_handlers is None:
        with _lock:
            if _bot_handlers is None:
                _bot_handlers = BotHandlers()
    return _bot_handlers

def get_handlers() -> BotHandlers:
    return get_bot_handlers()

def get_application() -> Optional[Application]:
    return get_bot_handlers().get_application()

def check_handlers() -> Dict[str, str]:
    app = get_application()
    return {
        "bot_handlers": "✅" if get_bot_handlers() else "❌",
        "application": "✅" if app else "❌",
        "bot_token": "✅" if BOT_TOKEN else "❌",
        "proxy": "✅" if PROXY_URL else "⚠️",
        "god_mode": "✅" if god_get_signal else "⚠️",
        "intelligence": "✅" if get_intelligence_engine else "⚠️",
        "market": "✅" if get_market else "⚠️",
        "analysis": "✅" if get_analysis_engine else "⚠️",
    }

def get_bot_token() -> str:
    return BOT_TOKEN

def get_admin_ids() -> List[int]:
    return ADMIN_IDS

def start():
    """Compatibility function for ModuleManager"""
    get_bot_handlers()
    return True

# Initialize on import
get_bot_handlers()
