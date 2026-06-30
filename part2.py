
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - Configuration Module
ماژول کانفیگ و تنظیمات محیطی با پشتیبانی کامل از تمام تنظیمات
"""

import os
import sys
import json
import re
import base64
import hashlib
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

# ==================== کلاس‌های تنظیمات ====================

class Environment(Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    RAILWAY = "railway"

class LogLevel(Enum):
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"

@dataclass
class APIConfig:
    base_url: str = ""
    api_key: str = ""
    secret_key: str = ""
    timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 1
    backoff_factor: float = 2.0
    rate_limit_requests: int = 100
    rate_limit_period: int = 60
    test_mode: bool = False
    sandbox: bool = False

@dataclass
class DatabaseConfig:
    url: str = "sqlite:///bot.db"
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    auto_migrate: bool = True
    backup_interval: int = 86400
    backup_retention: int = 7

@dataclass
class SecurityConfig:
    encryption_key: str = ""
    jwt_secret: str = ""
    jwt_expiry: int = 3600
    password_salt: str = ""
    rate_limit: bool = True
    max_login_attempts: int = 5
    lockout_duration: int = 3600
    session_timeout: int = 86400
    two_factor_enabled: bool = False
    ip_whitelist: List[str] = field(default_factory=list)
    api_key_rotation: int = 2592000

@dataclass
class TelegramConfig:
    bot_token: str = ""
    api_id: str = ""
    api_hash: str = ""
    webhook_url: str = ""
    webhook_port: int = 8080
    webhook_path: str = "/webhook"
    allowed_updates: List[str] = field(default_factory=lambda: ["message", "callback_query"])
    timeout: int = 30
    connect_timeout: int = 10
    pool_timeout: int = 30
    max_connections: int = 100

@dataclass
class MarketConfig:
    default_exchange: str = "coinex"
    default_timeframe: str = "4h"
    default_coin: str = "BTC"
    max_coins_per_user: int = 10
    min_volume_24h: float = 1000000
    min_market_cap: float = 10000000
    update_interval: int = 60
    signal_interval: int = 14400
    price_cache_ttl: int = 30
    order_book_depth: int = 10
    max_history_days: int = 30

@dataclass
class AIConfig:
    provider: str = "groq"
    model: str = "llama-3.2-90b-vision-preview"
    temperature: float = 0.3
    max_tokens: int = 800
    top_p: float = 0.95
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 60
    cache_ttl: int = 300
    vip_temperature: float = 0.2
    vip_max_tokens: int = 1200
    analysis_depth: str = "advanced"

@dataclass
class VIPConfig:
    monthly_price: int = 199000
    yearly_price: int = 1990000
    lifetime_price: int = 4990000
    currency: str = "IRT"
    payment_card: str = "6063731196254479"
    payment_card_holder: str = "به مرد"
    admin_username: str = "Amir92aa"
    trial_days: int = 3
    max_vip_users: int = 1000
    features: List[str] = field(default_factory=lambda: [
        "📊 سیگنال‌های اختصاصی VIP",
        "🤖 تحلیل پیشرفته با AI",
        "🆘 پشتیبانی اولویت‌دار",
        "💎 دسترسی به ارزهای ویژه",
        "🔔 هشدارهای لحظه‌ای",
        "📈 مدیریت پورتفولیو",
        "🎯 سیگنال‌های دقیق تر",
        "📊 اندیکاتورهای پیشرفته"
    ])

@dataclass
class ChannelConfig:
    channel_id: str = "@CryptoPulse606"
    channel_username: str = "CryptoPulse606"
    send_signals: bool = True
    send_analysis: bool = True
    send_alerts: bool = True
    send_updates: bool = True
    send_daily_report: bool = True
    send_weekly_report: bool = True
    send_market_updates: bool = True
    send_vip_signals: bool = False
    send_price_alerts: bool = True
    send_news: bool = True
    send_tips: bool = True
    send_motivation: bool = True
    signal_interval: int = 14400
    daily_report_time: str = "20:00"
    weekly_report_day: int = 6
    weekly_report_time: str = "18:00"
    price_alert_interval: int = 3600
    news_interval: int = 7200
    tip_interval: int = 21600

@dataclass
class MediaConfig:
    welcome_image: str = "assets/welcome_image.jpg"
    logo_image: str = "assets/logo.png"
    banner_image: str = "assets/banner.png"
    signal_image: str = "assets/signal_image.jpg"
    analysis_image: str = "assets/analysis_image.jpg"
    vip_image: str = "assets/vip_image.jpg"
    wallet_image: str = "assets/wallet_image.jpg"
    admin_image: str = "assets/admin_image.jpg"
    default_image: str = "assets/default_image.jpg"
    image_width: int = 1080
    image_height: int = 500
    image_format: str = "jpg"
    image_quality: int = 90
    use_url: bool = False
    image_url_base: str = "https://cryptopulse.ai/images/"

@dataclass
class NotificationConfig:
    enabled: bool = True
    channel_id: str = "@CryptoPulse606"
    signal_channel: str = "@CryptoPulse606"
    admin_channel: str = ""
    include_ai: bool = True
    include_technical: bool = True
    include_targets: bool = True
    max_messages_per_minute: int = 20
    quiet_hours_start: int = 23
    quiet_hours_end: int = 7

@dataclass
class BackupConfig:
    enabled: bool = True
    interval: int = 86400
    retention_days: int = 7
    compression: bool = True
    encryption: bool = True
    path: str = "./backups"
    auto_restore_on_failure: bool = True
    include_payments: bool = True
    include_users: bool = True
    include_settings: bool = True

@dataclass
class FeatureConfig:
    enable_signals: bool = True
    enable_ai_analysis: bool = True
    enable_vip: bool = True
    enable_payments: bool = True
    enable_referrals: bool = True
    enable_channel: bool = True
    enable_webhook: bool = True
    enable_auto_signals: bool = True
    enable_price_alerts: bool = True
    enable_portfolio: bool = True
    enable_news: bool = True
    enable_social: bool = True
    enable_api: bool = True
    enable_images: bool = True

# ==================== کلاس اصلی کانفیگ ====================

class ConfigManager:
    """مدیریت تنظیمات پیشرفته با کش"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._load_from_env()
        self._load_from_file()
        self._load_from_database()
        self._set_defaults()
        self._validate()
        self._normalize()
        self._encrypt_sensitive()
        self._cache = {}
    
    def _load_from_env(self):
        """بارگذاری از متغیرهای محیطی"""
        self.env = os.environ
        
        # تنظیمات پایه
        self.bot_token = self.env.get("BOT_TOKEN", "")
        self.groq_api_key = self.env.get("GROQ_API_KEY", "")
        self.coinex_api_key = self.env.get("COINEX_API_KEY", "")
        self.coinex_secret_key = self.env.get("COINEX_SECRET_KEY", "")
        
        # تنظیمات ادمین
        admin_ids = self.env.get("ADMIN_IDS", "")
        self.admin_ids = [int(x.strip()) for x in admin_ids.split(",") if x.strip()]
        
        # تنظیمات کانال
        self.channel_id = self.env.get("CHANNEL_ID", "@CryptoPulse606")
        self.signal_channel = self.env.get("SIGNAL_CHANNEL", self.channel_id)
        
        # تنظیمات دیتابیس
        self.database_url = self.env.get("DATABASE_URL", "sqlite:///bot.db")
        
        # تنظیمات وب‌هوک
        self.webhook_url = self.env.get("WEBHOOK_URL", "")
        self.port = int(self.env.get("PORT", 8080))
        
        # تنظیمات پیشرفته
        self.debug = self.env.get("DEBUG", "False").lower() == "true"
        self.test_mode = self.env.get("TEST_MODE", "False").lower() == "true"
        
        # تنظیمات زمان
        self.timezone = self.env.get("TIMEZONE", "Asia/Tehran")
        
        # تنظیمات ریت‌لیمیت
        self.rate_limit_requests = int(self.env.get("RATE_LIMIT_REQUESTS", 100))
        self.rate_limit_period = int(self.env.get("RATE_LIMIT_PERIOD", 60))
        
        # تنظیمات ارز
        self.default_coin = self.env.get("DEFAULT_COIN", "BTC")
        self.default_timeframe = self.env.get("DEFAULT_TIMEFRAME", "4h")
        
        # تنظیمات VIP
        self.vip_price_monthly = int(self.env.get("VIP_PRICE_MONTHLY", 199000))
        self.vip_price_yearly = int(self.env.get("VIP_PRICE_YEARLY", 1990000))
        self.vip_price_lifetime = int(self.env.get("VIP_PRICE_LIFETIME", 4990000))
        self.vip_currency = self.env.get("VIP_CURRENCY", "IRT")
        self.vip_payment_card = self.env.get("VIP_PAYMENT_CARD", "6063731196254479")
        self.vip_payment_holder = self.env.get("VIP_PAYMENT_HOLDER", "به مرد")
        self.vip_admin_username = self.env.get("VIP_ADMIN_USERNAME", "Amir92aa")
        self.vip_trial_days = int(self.env.get("VIP_TRIAL_DAYS", 3))
        
        # تنظیمات سیگنال
        self.signal_interval = int(self.env.get("SIGNAL_INTERVAL", 14400))
        
        # تنظیمات امنیتی
        self.encryption_key = self.env.get("ENCRYPTION_KEY", self._generate_key())
        self.jwt_secret = self.env.get("JWT_SECRET", self._generate_key())
        
        # تنظیمات بکاپ
        self.backup_interval = int(self.env.get("BACKUP_INTERVAL", 86400))
        self.backup_retention = int(self.env.get("BACKUP_RETENTION", 7))
        
        # تنظیمات صرافی
        self.coinex_base_url = self.env.get("COINEX_BASE_URL", "https://api.coinex.com/v1")
        self.coinex_timeout = int(self.env.get("COINEX_TIMEOUT", 30))
        
        # تنظیمات AI
        self.ai_model = self.env.get("AI_MODEL", "llama-3.2-90b-vision-preview")
        self.ai_temperature = float(self.env.get("AI_TEMPERATURE", 0.3))
        self.ai_max_tokens = int(self.env.get("AI_MAX_TOKENS", 800))
        
        # تنظیمات تصاویر
        self.image_path = self.env.get("IMAGE_PATH", "assets/")
        self.image_url_base = self.env.get("IMAGE_URL_BASE", "https://cryptopulse.ai/images/")
        self.use_image_url = self.env.get("USE_IMAGE_URL", "False").lower() == "true"
        
        # لیست ارزهای فعال
        self.active_coins = self.env.get("ACTIVE_COINS", "BTC,ETH,BNB,SOL,XRP,ADA,DOGE,DOT,MATIC,SHIB,AVAX,LINK,UNI,ATOM,LTC,BCH,NEAR,VET,ALGO,FTM,EOS,TRX,XLM,ICP,HBAR,FIL,APT,ARB,OP,MKR,AAVE,MNT,INJ,TON,SUI,PEPE,BONK,FLOKI,WIF,JUP,JASMY,KAS,RNDR,THETA,FET,AGIX,OCEAN")
        self.active_coins_list = [x.strip() for x in self.active_coins.split(",") if x.strip()]
        
        # تنظیمات پشتیبانی
        self.support_email = self.env.get("SUPPORT_EMAIL", "support@cryptopulse.ai")
        self.support_chat = self.env.get("SUPPORT_CHAT", "")
        self.support_phone = self.env.get("SUPPORT_PHONE", "")
    
    def _load_from_file(self):
        """بارگذاری از فایل کانفیگ"""
        config_file = Path("config.json")
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    for key, value in file_config.items():
                        if hasattr(self, key):
                            setattr(self, key, value)
            except:
                pass
        
        env_file = Path(".env.local")
        if env_file.exists():
            self._load_env_file(env_file)
    
    def _load_env_file(self, file_path: Path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        if key in os.environ:
                            continue
                        os.environ[key] = value
                        if hasattr(self, key.lower()):
                            setattr(self, key.lower(), self._parse_value(value))
        except:
            pass
    
    def _parse_value(self, value: str) -> Any:
        if value.lower() == 'true':
            return True
        if value.lower() == 'false':
            return False
        if value.lower() == 'null' or value.lower() == 'none':
            return None
        if value.isdigit():
            return int(value)
        try:
            return float(value)
        except ValueError:
            return value
    
    def _load_from_database(self):
        try:
            from sqlalchemy import create_engine, text
            engine = create_engine(self.database_url)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT key, value FROM settings"))
                for row in result:
                    key, value = row
                    if hasattr(self, key):
                        setattr(self, key, self._parse_value(value))
        except:
            pass
    
    def _set_defaults(self):
        if not hasattr(self, 'max_retries'):
            self.max_retries = 3
        if not hasattr(self, 'timeout_seconds'):
            self.timeout_seconds = 30
        if not hasattr(self, 'max_connections'):
            self.max_connections = 100
        if not hasattr(self, 'pool_size'):
            self.pool_size = 10
        if not hasattr(self, 'pool_timeout'):
            self.pool_timeout = 30
        
        if not hasattr(self, 'allowed_currencies'):
            self.allowed_currencies = ["USD", "USDT", "BTC", "ETH", "BNB", "IRT"]
        if not hasattr(self, 'excluded_coins'):
            self.excluded_coins = []
        if not hasattr(self, 'featured_coins'):
            self.featured_coins = ["BTC", "ETH", "BNB", "SOL", "XRP"]
        
        if not hasattr(self, 'notification_enabled'):
            self.notification_enabled = True
        if not hasattr(self, 'send_welcome_message'):
            self.send_welcome_message = True
        if not hasattr(self, 'send_goodbye_message'):
            self.send_goodbye_message = True
        
        if not hasattr(self, 'analysis_interval'):
            self.analysis_interval = 300
        if not hasattr(self, 'min_confidence'):
            self.min_confidence = 60
        if not hasattr(self, 'max_confidence'):
            self.max_confidence = 100
        
        if not hasattr(self, 'min_trade_amount'):
            self.min_trade_amount = 10.0
        if not hasattr(self, 'max_trade_amount'):
            self.max_trade_amount = 10000.0
        if not hasattr(self, 'risk_per_trade'):
            self.risk_per_trade = 2.0
        if not hasattr(self, 'max_open_trades'):
            self.max_open_trades = 5
        
        if not hasattr(self, 'emoji_style'):
            self.emoji_style = "modern"
        if not hasattr(self, 'language'):
            self.language = "fa"
        
        if not hasattr(self, 'admin_commands'):
            self.admin_commands = [
                "stats", "users", "broadcast", "ban", "unban",
                "vip", "payment", "backup", "restore", "settings",
                "logs", "clear", "restart", "shutdown"
            ]
        
        if not hasattr(self, 'channel_commands'):
            self.channel_commands = [
                "send", "pin", "unpin", "delete", "edit"
            ]
        
        if not hasattr(self, 'image_formats'):
            self.image_formats = ["jpg", "png", "gif", "webp"]
    
    def _validate(self):
        if not self.bot_token or len(self.bot_token) < 40:
            raise ValueError("BOT_TOKEN is required and must be valid")
        
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY is required")
        
        if not self.coinex_api_key or not self.coinex_secret_key:
            raise ValueError("COINEX_API_KEY and COINEX_SECRET_KEY are required")
        
        if not self.admin_ids:
            raise ValueError("At least one ADMIN_ID is required")
        
        if not 1024 <= self.port <= 65535:
            raise ValueError("PORT must be between 1024 and 65535")
        
        if self.signal_interval < 60:
            raise ValueError("SIGNAL_INTERVAL must be at least 60 seconds")
        
        if self.vip_price_monthly <= 0:
            raise ValueError("VIP_PRICE_MONTHLY must be greater than 0")
        if self.vip_price_yearly <= 0:
            raise ValueError("VIP_PRICE_YEARLY must be greater than 0")
        
        if not self.channel_id:
            raise ValueError("CHANNEL_ID is required")
    
    def _normalize(self):
        if hasattr(self, 'admin_ids') and isinstance(self.admin_ids, str):
            self.admin_ids = [int(x.strip()) for x in self.admin_ids.split(',') if x.strip()]
        
        if hasattr(self, 'active_coins') and isinstance(self.active_coins, str):
            self.active_coins_list = [x.strip().upper() for x in self.active_coins.split(',') if x.strip()]
        
        if self.webhook_url and not self.webhook_url.endswith('/'):
            self.webhook_url += '/'
        
        if hasattr(self, 'signal_interval'):
            self.signal_interval = max(60, min(86400, self.signal_interval))
    
    def _encrypt_sensitive(self):
        self._sensitive_keys = ['bot_token', 'groq_api_key', 'coinex_api_key', 'coinex_secret_key', 'encryption_key', 'jwt_secret']
        self._key_hashes = {}
        for key in self._sensitive_keys:
            if hasattr(self, key):
                value = getattr(self, key)
                if value:
                    self._key_hashes[key] = hashlib.sha256(str(value).encode()).hexdigest()[:8]
    
    def _generate_key(self) -> str:
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))
    
    def get(self, key: str, default: Any = None) -> Any:
        if key in self._cache:
            value, timestamp = self._cache[key]
            if (datetime.now() - timestamp).seconds < 300:
                return value
        
        if hasattr(self, key):
            value = getattr(self, key)
            self._cache[key] = (value, datetime.now())
            return value
        return default
    
    def set(self, key: str, value: Any):
        if hasattr(self, key):
            setattr(self, key, value)
            self._save_to_database(key, value)
            self._cache[key] = (value, datetime.now())
    
    def _save_to_database(self, key: str, value: Any):
        try:
            from sqlalchemy import create_engine, text
            engine = create_engine(self.database_url)
            with engine.connect() as conn:
                conn.execute(
                    text("INSERT OR REPLACE INTO settings (key, value) VALUES (:key, :value)"),
                    {"key": key, "value": str(value)}
                )
                conn.commit()
        except:
            pass
    
    def update(self, config_dict: Dict[str, Any]):
        for key, value in config_dict.items():
            self.set(key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        for key in dir(self):
            if not key.startswith('_') and not callable(getattr(self, key)):
                value = getattr(self, key)
                if not isinstance(value, (type, classmethod, staticmethod)):
                    result[key] = value
        return result
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)
    
    def reload(self):
        self._initialized = False
        self.__init__()
    
    @lru_cache(maxsize=100)
    def get_admin_ids(self) -> List[int]:
        return self.admin_ids
    
    @lru_cache(maxsize=100)
    def get_active_coins(self) -> List[str]:
        return self.active_coins_list
    
    @lru_cache(maxsize=100)
    def get_featured_coins(self) -> List[str]:
        return getattr(self, 'featured_coins', ["BTC", "ETH", "BNB", "SOL", "XRP"])
    
    @lru_cache(maxsize=100)
    def get_currency_symbol(self, currency: str) -> str:
        symbols = {
            "USD": "$", "USDT": "$", "BTC": "₿", "ETH": "Ξ",
            "BNB": "BNB", "SOL": "◎", "XRP": "XRP", "ADA": "₳",
            "DOGE": "Ð", "DOT": "DOT", "MATIC": "MATIC",
            "IRT": "تومان", "IRR": "ریال"
        }
        return symbols.get(currency, currency)
    
    @lru_cache(maxsize=100)
    def get_timeframe_seconds(self, timeframe: str) -> int:
        timeframes = {
            "1m": 60, "5m": 300, "15m": 900, "30m": 1800,
            "1h": 3600, "4h": 14400, "1d": 86400, "1w": 604800
        }
        return timeframes.get(timeframe, 3600)
    
    @lru_cache(maxsize=100)
    def is_admin(self, user_id: int) -> bool:
        return user_id in self.get_admin_ids()
    
    @lru_cache(maxsize=100)
    def is_coin_active(self, coin: str) -> bool:
        return coin.upper() in self.get_active_coins()
    
    @lru_cache(maxsize=100)
    def get_vip_price(self, plan: str = "monthly") -> int:
        prices = {
            'monthly': self.vip_price_monthly,
            'yearly': self.vip_price_yearly,
            'lifetime': self.vip_price_lifetime
        }
        return prices.get(plan, self.vip_price_monthly)
    
    @lru_cache(maxsize=100)
    def get_image_path(self, image_type: str = "welcome") -> str:
        images = {
            'welcome': self.image_path + "welcome_image.jpg",
            'logo': self.image_path + "logo.png",
            'banner': self.image_path + "banner.png",
            'signal': self.image_path + "signal_image.jpg",
            'analysis': self.image_path + "analysis_image.jpg",
            'vip': self.image_path + "vip_image.jpg",
            'wallet': self.image_path + "wallet_image.jpg",
            'admin': self.image_path + "admin_image.jpg"
        }
        return images.get(image_type, images['welcome'])
    
    @lru_cache(maxsize=100)
    def get_image_url(self, image_type: str = "welcome") -> str:
        images = {
            'welcome': "welcome_image.jpg",
            'logo': "logo.png",
            'banner': "banner.png",
            'signal': "signal_image.jpg",
            'analysis': "analysis_image.jpg",
            'vip': "vip_image.jpg",
            'wallet': "wallet_image.jpg",
            'admin': "admin_image.jpg"
        }
        return self.image_url_base + images.get(image_type, "welcome_image.jpg")
    
    def clear_cache(self):
        self.get_admin_ids.cache_clear()
        self.get_active_coins.cache_clear()
        self.get_featured_coins.cache_clear()
        self.get_currency_symbol.cache_clear()
        self.get_timeframe_seconds.cache_clear()
        self.is_admin.cache_clear()
        self.is_coin_active.cache_clear()
        self.get_vip_price.cache_clear()
        self.get_image_path.cache_clear()
        self.get_image_url.cache_clear()
        self._cache.clear()

# ==================== تنظیمات سطوح دسترسی ====================

class PermissionManager:
    def __init__(self, config: ConfigManager):
        self.config = config
        self._permissions = {
            'admin': ['*'],
            'vip': ['signals', 'analysis', 'portfolio', 'alerts', 'vip_signals'],
            'premium': ['signals', 'analysis', 'alerts'],
            'free': ['signals', 'analysis'],
            'guest': ['signals']
        }
    
    def has_permission(self, user_level: str, permission: str) -> bool:
        if user_level not in self._permissions:
            return False
        perms = self._permissions[user_level]
        return '*' in perms or permission in perms
    
    def get_level_permissions(self, level: str) -> List[str]:
        return self._permissions.get(level, [])

# ==================== تنظیمات ارزها ====================

class CurrencyManager:
    def __init__(self, config: ConfigManager):
        self.config = config
        self._currencies = self._load_currencies()
    
    def _load_currencies(self) -> Dict:
        return {
            "BTC": {"name": "Bitcoin", "symbol": "₿", "decimals": 8, "min_amount": 0.0001},
            "ETH": {"name": "Ethereum", "symbol": "Ξ", "decimals": 8, "min_amount": 0.001},
            "BNB": {"name": "Binance Coin", "symbol": "BNB", "decimals": 8, "min_amount": 0.01},
            "SOL": {"name": "Solana", "symbol": "◎", "decimals": 9, "min_amount": 0.01},
            "XRP": {"name": "Ripple", "symbol": "XRP", "decimals": 6, "min_amount": 1},
            "ADA": {"name": "Cardano", "symbol": "₳", "decimals": 6, "min_amount": 1},
            "DOGE": {"name": "Dogecoin", "symbol": "Ð", "decimals": 8, "min_amount": 1},
            "DOT": {"name": "Polkadot", "symbol": "DOT", "decimals": 10, "min_amount": 0.1},
            "MATIC": {"name": "Polygon", "symbol": "MATIC", "decimals": 8, "min_amount": 1},
            "SHIB": {"name": "Shiba Inu", "symbol": "SHIB", "decimals": 8, "min_amount": 1000},
            "AVAX": {"name": "Avalanche", "symbol": "AVAX", "decimals": 9, "min_amount": 0.1},
            "LINK": {"name": "Chainlink", "symbol": "LINK", "decimals": 8, "min_amount": 0.1},
            "UNI": {"name": "Uniswap", "symbol": "UNI", "decimals": 8, "min_amount": 0.1},
            "ATOM": {"name": "Cosmos", "symbol": "ATOM", "decimals": 6, "min_amount": 0.1},
            "LTC": {"name": "Litecoin", "symbol": "Ł", "decimals": 8, "min_amount": 0.01},
            "BCH": {"name": "Bitcoin Cash", "symbol": "BCH", "decimals": 8, "min_amount": 0.001},
            "NEAR": {"name": "Near Protocol", "symbol": "NEAR", "decimals": 24, "min_amount": 0.1},
            "VET": {"name": "VeChain", "symbol": "VET", "decimals": 18, "min_amount": 1},
            "ALGO": {"name": "Algorand", "symbol": "ALGO", "decimals": 6, "min_amount": 1},
            "FTM": {"name": "Fantom", "symbol": "FTM", "decimals": 18, "min_amount": 0.1},
            "EOS": {"name": "EOS", "symbol": "EOS", "decimals": 4, "min_amount": 0.1},
            "TRX": {"name": "Tron", "symbol": "TRX", "decimals": 6, "min_amount": 1},
            "XLM": {"name": "Stellar", "symbol": "XLM", "decimals": 7, "min_amount": 1},
        }
    
    def get_currency(self, symbol: str) -> Optional[Dict]:
        return self._currencies.get(symbol.upper())
    
    def get_all(self) -> Dict:
        return self._currencies
    
    def get_active(self) -> List[str]:
        return self.config.get_active_coins()
    
    def format_amount(self, symbol: str, amount: float) -> str:
        currency = self.get_currency(symbol)
        if not currency:
            return f"{amount:.8f}"
        decimals = currency.get('decimals', 8)
        return f"{amount:.{decimals}f}"

# ==================== تنظیمات زمان ====================

class TimeConfig:
    def __init__(self):
        self.timezone = "Asia/Tehran"
        self.timezone_offset = 3.5
        self.use_dst = False
        self.date_format = "%Y-%m-%d"
        self.time_format = "%H:%M:%S"
        self.datetime_format = "%Y-%m-%d %H:%M:%S"
        self.persian_date_format = "%Y/%m/%d"
        self.market_open_hour = 0
        self.market_close_hour = 24
        self.weekend_trading = True
        self.quiet_hours_start = 23
        self.quiet_hours_end = 7
    
    def get_offset_seconds(self) -> int:
        return int(self.timezone_offset * 3600)

# ==================== تنظیمات بازار ====================

class MarketSettings:
    def __init__(self, config: ConfigManager):
        self.config = config
        self.trading_enabled = True
        self.min_order_amount = 10.0
        self.max_order_amount = 10000.0
        self.default_leverage = 1
        self.max_position_size = 0.1
        self.max_drawdown = 0.2
        self.stop_loss_default = 0.02
        self.take_profit_default = 0.05
        self.order_timeout = 30
        self.order_retry_count = 3
        self.order_retry_delay = 1
        self.min_volume = 1000000
        self.min_market_cap = 10000000
        self.min_liquidity = 100000
    
    def get_min_order(self, symbol: str) -> float:
        return self.min_order_amount
    
    def calculate_position_size(self, balance: float, risk: float) -> float:
        max_position = balance * self.max_position_size
        risk_amount = balance * risk
        return min(max_position, risk_amount)

# ==================== تنظیمات امنیت ====================

class SecuritySettings:
    def __init__(self):
        self.encryption_enabled = True
        self.ssl_enabled = True
        self.ip_whitelist_enabled = False
        self.two_factor_enabled = False
        self.session_timeout = 86400
        self.max_login_attempts = 5
        self.lockout_duration = 3600
        self.api_key_rotation = 2592000
        self.password_policy = {
            'min_length': 8,
            'require_uppercase': True,
            'require_lowercase': True,
            'require_numbers': True,
            'require_special': True
        }

# ==================== تنظیمات تصاویر ====================

class ImageSettings:
    def __init__(self, config: ConfigManager):
        self.config = config
        self.use_url = config.get('use_image_url', False)
        self.image_path = config.get('image_path', 'assets/')
        self.image_url_base = config.get('image_url_base', 'https://cryptopulse.ai/images/')
        
        self.default_images = {
            'welcome': 'welcome_image.jpg',
            'logo': 'logo.png',
            'banner': 'banner.png',
            'signal': 'signal_image.jpg',
            'analysis': 'analysis_image.jpg',
            'vip': 'vip_image.jpg',
            'wallet': 'wallet_image.jpg',
            'admin': 'admin_image.jpg'
        }
        
        self.image_sizes = {
            'welcome': (1080, 500),
            'logo': (500, 500),
            'banner': (1200, 400),
            'signal': (800, 400),
            'analysis': (900, 500),
            'vip': (800, 400),
            'wallet': (800, 400),
            'admin': (800, 400)
        }
    
    def get_image(self, image_type: str = "welcome") -> str:
        if self.use_url:
            return self.image_url_base + self.default_images.get(image_type, self.default_images['welcome'])
        else:
            return self.image_path + self.default_images.get(image_type, self.default_images['welcome'])
    
    def get_size(self, image_type: str = "welcome") -> Tuple[int, int]:
        return self.image_sizes.get(image_type, (1080, 500))

# ==================== Export ====================

import sys
import traceback

class SafeInstance:
    """ایمن‌ساز ایجاد نمونه از کلاس‌ها"""
    
    _instances = {}
    
    @classmethod
    def create(cls, class_name, *args, **kwargs):
        """ایجاد ایمن نمونه از کلاس"""
        key = f"{class_name}_{args}_{kwargs}"
        
        if key in cls._instances:
            return cls._instances[key]
        
        try:
            # دریافت کلاس از فضای نام جهانی
            if class_name in globals():
                instance = globals()[class_name](*args, **kwargs)
            elif class_name in sys.modules.get('__main__', {}).__dict__:
                instance = sys.modules['__main__'].__dict__[class_name](*args, **kwargs)
            else:
                instance = None
            
            cls._instances[key] = instance
            return instance
        except Exception:
            cls._instances[key] = None
            return None

# ==================== ایجاد نمونه‌ها ====================

# ۱. ConfigManager - اولین و مهم‌ترین
config_manager = SafeInstance.create("ConfigManager")

# ۲. PermissionManager - وابسته به ConfigManager
permission_manager = SafeInstance.create("PermissionManager", config_manager) if config_manager else None

# ۳. CurrencyManager - وابسته به ConfigManager
currency_manager = SafeInstance.create("CurrencyManager", config_manager) if config_manager else None

# ۴. TimeConfig - مستقل
time_config = SafeInstance.create("TimeConfig")

# ۵. MarketSettings - وابسته به ConfigManager
market_settings = SafeInstance.create("MarketSettings", config_manager) if config_manager else None

# ۶. SecuritySettings - مستقل
security_settings = SafeInstance.create("SecuritySettings")

# ۷. ImageSettings - وابسته به ConfigManager
image_settings = SafeInstance.create("ImageSettings", config_manager) if config_manager else None

# ==================== توابع دسترسی ====================

def get_config():
    """دریافت نمونه ConfigManager"""
    return config_manager

def get_permissions():
    """دریافت نمونه PermissionManager"""
    return permission_manager

def get_currencies():
    """دریافت نمونه CurrencyManager"""
    return currency_manager

def get_time():
    """دریافت نمونه TimeConfig"""
    return time_config

def get_market_settings():
    """دریافت نمونه MarketSettings"""
    return market_settings

def get_security():
    """دریافت نمونه SecuritySettings"""
    return security_settings

def get_image_settings():
    """دریافت نمونه ImageSettings"""
    return image_settings

# ==================== تابع کمکی برای دیباگ ====================

def check_instances():
    """بررسی سلامت نمونه‌ها"""
    instances = {
        "config_manager": config_manager,
        "permission_manager": permission_manager,
        "currency_manager": currency_manager,
        "time_config": time_config,
        "market_settings": market_settings,
        "security_settings": security_settings,
        "image_settings": image_settings
    }
    
    result = {}
    for name, instance in instances.items():
        result[name] = "✅ OK" if instance else "❌ FAILED"
    
    return result
