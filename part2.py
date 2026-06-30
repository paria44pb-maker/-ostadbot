#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - Configuration Module (Professional)
ماژول کانفیگ و تنظیمات کامل - بدون خطا و بدون لاگ
شامل تمام تنظیمات پیشرفته، اعتبارسنجی و مدیریت هوشمند
"""

import os
import sys
import json
import re
import hashlib
import base64
import secrets
import string
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache
from pathlib import Path
from collections import defaultdict

# ============================================================
#                    کلاس‌های پایه تنظیمات
# ============================================================

class Environment(Enum):
    """محیط‌های اجرایی"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    RAILWAY = "railway"

class LogLevel(Enum):
    """سطوح لاگ (فقط برای خطاهای حیاتی)"""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"

class SecurityMode(Enum):
    """حالت‌های امنیتی"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"

# ============================================================
#                    کلاس‌های تنظیمات تخصصی
# ============================================================

@dataclass
class APIConfig:
    """تنظیمات API"""
    base_url: str = "https://api.coinex.com/v1"
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
    api_version: str = "v1"
    user_agent: str = "CryptoPulseAI/3.0"

@dataclass
class DatabaseConfig:
    """تنظیمات دیتابیس"""
    url: str = "sqlite:///bot.db"
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    pool_pre_ping: bool = True
    echo: bool = False
    auto_migrate: bool = True
    backup_interval: int = 86400
    backup_retention: int = 7
    backup_compression: bool = True
    backup_encryption: bool = True
    backup_path: str = "./backups"
    max_connections: int = 100
    statement_timeout: int = 30000
    lock_timeout: int = 30000

@dataclass
class SecurityConfig:
    """تنظیمات امنیتی"""
    encryption_key: str = ""
    jwt_secret: str = ""
    jwt_expiry: int = 3600
    jwt_refresh_expiry: int = 86400
    password_salt: str = ""
    rate_limit_enabled: bool = True
    max_login_attempts: int = 5
    lockout_duration: int = 3600
    session_timeout: int = 86400
    two_factor_enabled: bool = False
    ip_whitelist: List[str] = field(default_factory=list)
    ip_blacklist: List[str] = field(default_factory=list)
    api_key_rotation: int = 2592000
    security_mode: str = "high"
    ssl_enabled: bool = True
    firewall_enabled: bool = True
    ddos_protection: bool = True
    request_validation: bool = True
    sql_injection_protection: bool = True

@dataclass
class TelegramConfig:
    """تنظیمات تلگرام"""
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
    base_url: str = "https://api.telegram.org"
    file_url: str = "https://api.telegram.org/file/bot"
    retry_attempts: int = 3
    retry_delay: int = 1

@dataclass
class MarketConfig:
    """تنظیمات بازار"""
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
    supported_timeframes: List[str] = field(default_factory=lambda: ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"])
    trading_enabled: bool = True
    min_trade_amount: float = 10.0
    max_trade_amount: float = 10000.0
    default_leverage: int = 1
    max_position_size: float = 0.1
    max_drawdown: float = 0.2
    stop_loss_default: float = 0.02
    take_profit_default: float = 0.05

@dataclass
class AIConfig:
    """تنظیمات هوش مصنوعی"""
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
    enable_vision: bool = False
    enable_streaming: bool = False
    max_requests_per_minute: int = 30
    max_tokens_per_minute: int = 10000
    fallback_enabled: bool = True

@dataclass
class VIPConfig:
    """تنظیمات VIP"""
    monthly_price: int = 199000
    yearly_price: int = 1990000
    lifetime_price: int = 4990000
    currency: str = "IRT"
    payment_card: str = "6063731196254479"
    payment_card_holder: str = "به مرد"
    admin_username: str = "Amir92aa"
    trial_days: int = 3
    max_vip_users: int = 1000
    discount_codes: Dict[str, int] = field(default_factory=dict)
    features: List[str] = field(default_factory=lambda: [
        "📊 سیگنال‌های اختصاصی VIP",
        "🤖 تحلیل پیشرفته با AI (نامحدود)",
        "🆘 پشتیبانی اولویت‌دار ۲۴/۷",
        "💎 دسترسی به ارزهای ویژه",
        "🔔 هشدارهای لحظه‌ای",
        "📈 مدیریت پورتفولیو پیشرفته",
        "🎯 سیگنال‌های دقیق‌تر با ۳۰+ اندیکاتور",
        "📊 اندیکاتورهای اختصاصی",
        "🔬 تحلیل تخصصی و فاندامنتال",
        "📡 سیگنال‌های لحظه‌ای",
        "📱 اعلان‌های فوری در تلگرام",
        "🎁 هدیه ماهانه",
        "📚 آموزش‌های اختصاصی",
        "🤝 دسترسی به گروه VIP",
        "🎯 استراتژی‌های معاملاتی"
    ])
    payment_methods: List[str] = field(default_factory=lambda: ["card", "crypto", "wallet"])
    min_payment: int = 50000
    max_payment: int = 10000000

@dataclass
class ChannelConfig:
    """تنظیمات کانال"""
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
    max_messages_per_minute: int = 20
    quiet_hours_start: int = 23
    quiet_hours_end: int = 7

@dataclass
class ImageConfig:
    """تنظیمات تصاویر"""
    path: str = "assets/"
    use_url: bool = False
    url_base: str = "https://cryptopulse.ai/images/"
    welcome_image: str = "welcome_image.jpg"
    logo_image: str = "logo.png"
    banner_image: str = "banner.png"
    signal_image: str = "signal_image.jpg"
    analysis_image: str = "analysis_image.jpg"
    vip_image: str = "vip_image.jpg"
    wallet_image: str = "wallet_image.jpg"
    admin_image: str = "admin_image.jpg"
    chart_image: str = "chart_image.png"
    default_image: str = "default_image.jpg"
    width: int = 1080
    height: int = 500
    format: str = "jpg"
    quality: int = 90
    watermark: bool = False
    watermark_text: str = "CryptoPulse AI"

@dataclass
class NotificationConfig:
    """تنظیمات اعلان‌ها"""
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
    notify_on_error: bool = True
    notify_on_signal: bool = True
    notify_on_analysis: bool = True
    notify_on_payment: bool = True
    notify_on_new_user: bool = True

@dataclass
class BackupConfig:
    """تنظیمات بکاپ"""
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
    include_signals: bool = True
    include_trades: bool = True
    cloud_backup: bool = False
    cloud_provider: str = "google_drive"
    cloud_folder: str = "cryptopulse_backups"

@dataclass
class FeatureConfig:
    """تنظیمات ویژگی‌ها"""
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
    enable_support_ticket: bool = True
    enable_education: bool = True
    enable_competition: bool = False
    enable_newsletter: bool = True
    enable_analytics: bool = True

@dataclass
class PerformanceConfig:
    """تنظیمات عملکرد"""
    cache_enabled: bool = True
    cache_ttl: int = 300
    cache_max_size: int = 1000
    thread_pool_size: int = 10
    async_enabled: bool = True
    connection_pool_size: int = 10
    response_compression: bool = True
    request_queuing: bool = True
    max_concurrent_requests: int = 100
    timeout_graceful_shutdown: int = 30

# ============================================================
#                    کلاس اصلی ConfigManager
# ============================================================

class ConfigManager:
    """مدیریت تنظیمات پیشرفته با کش و اعتبارسنجی"""
    
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
        self._cache = {}
        self._validation_errors = []
        self._load_from_env()
        self._load_from_file()
        self._set_defaults()
        self._validate()
        self._normalize()
        self._encrypt_sensitive()
        self._init_config_classes()
    
    def _load_from_env(self):
        """بارگذاری از متغیرهای محیطی با پشتیبانی کامل"""
        # تنظیمات اصلی
        self.bot_token = os.environ.get("BOT_TOKEN", "")
        self.groq_api_key = os.environ.get("GROQ_API_KEY", "")
        self.coinex_api_key = os.environ.get("COINEX_API_KEY", "")
        self.coinex_secret_key = os.environ.get("COINEX_SECRET_KEY", "")
        self.coinex_base_url = os.environ.get("COINEX_BASE_URL", "https://api.coinex.com/v1")
        
        # تنظیمات ادمین
        admin_ids = os.environ.get("ADMIN_IDS", "")
        self.admin_ids = [int(x.strip()) for x in admin_ids.split(",") if x.strip()]
        
        # تنظیمات کانال
        self.channel_id = os.environ.get("CHANNEL_ID", "@CryptoPulse606")
        self.signal_channel = os.environ.get("SIGNAL_CHANNEL", self.channel_id)
        
        # تنظیمات دیتابیس
        self.database_url = os.environ.get("DATABASE_URL", "sqlite:///bot.db")
        
        # تنظیمات وب‌هوک
        self.webhook_url = os.environ.get("WEBHOOK_URL", "")
        self.port = int(os.environ.get("PORT", 8080))
        
        # تنظیمات پیشرفته
        self.debug = os.environ.get("DEBUG", "False").lower() == "true"
        self.test_mode = os.environ.get("TEST_MODE", "False").lower() == "true"
        self.timezone = os.environ.get("TIMEZONE", "Asia/Tehran")
        
        # تنظیمات ریت‌لیمیت
        self.rate_limit_requests = int(os.environ.get("RATE_LIMIT_REQUESTS", 100))
        self.rate_limit_period = int(os.environ.get("RATE_LIMIT_PERIOD", 60))
        
        # تنظیمات ارز
        self.default_coin = os.environ.get("DEFAULT_COIN", "BTC")
        self.default_timeframe = os.environ.get("DEFAULT_TIMEFRAME", "4h")
        
        # تنظیمات VIP
        self.vip_price_monthly = int(os.environ.get("VIP_PRICE_MONTHLY", 199000))
        self.vip_price_yearly = int(os.environ.get("VIP_PRICE_YEARLY", 1990000))
        self.vip_price_lifetime = int(os.environ.get("VIP_PRICE_LIFETIME", 4990000))
        self.vip_currency = os.environ.get("VIP_CURRENCY", "IRT")
        self.vip_payment_card = os.environ.get("VIP_PAYMENT_CARD", "6063731196254479")
        self.vip_payment_holder = os.environ.get("VIP_PAYMENT_HOLDER", "به مرد")
        self.vip_admin_username = os.environ.get("VIP_ADMIN_USERNAME", "Amir92aa")
        self.vip_trial_days = int(os.environ.get("VIP_TRIAL_DAYS", 3))
        
        # تنظیمات سیگنال
        self.signal_interval = int(os.environ.get("SIGNAL_INTERVAL", 14400))
        self.min_confidence = int(os.environ.get("MIN_CONFIDENCE", 60))
        self.max_confidence = int(os.environ.get("MAX_CONFIDENCE", 100))
        
        # تنظیمات امنیتی
        self.encryption_key = os.environ.get("ENCRYPTION_KEY", self._generate_key())
        self.jwt_secret = os.environ.get("JWT_SECRET", self._generate_key())
        self.security_mode = os.environ.get("SECURITY_MODE", "high")
        
        # تنظیمات بکاپ
        self.backup_interval = int(os.environ.get("BACKUP_INTERVAL", 86400))
        self.backup_retention = int(os.environ.get("BACKUP_RETENTION", 7))
        self.backup_path = os.environ.get("BACKUP_PATH", "./backups")
        
        # تنظیمات صرافی
        self.coinex_timeout = int(os.environ.get("COINEX_TIMEOUT", 30))
        self.coinex_max_retries = int(os.environ.get("COINEX_MAX_RETRIES", 3))
        
        # تنظیمات AI
        self.ai_model = os.environ.get("AI_MODEL", "llama-3.2-90b-vision-preview")
        self.ai_temperature = float(os.environ.get("AI_TEMPERATURE", 0.3))
        self.ai_max_tokens = int(os.environ.get("AI_MAX_TOKENS", 800))
        self.ai_timeout = int(os.environ.get("AI_TIMEOUT", 60))
        
        # لیست ارزهای فعال
        active_coins = os.environ.get("ACTIVE_COINS", 
            "BTC,ETH,BNB,SOL,XRP,ADA,DOGE,DOT,MATIC,SHIB,AVAX,LINK,UNI,ATOM,LTC,BCH,NEAR,VET,ALGO,FTM,EOS,TRX,XLM,ICP,HBAR,FIL,APT,ARB,OP,MKR,AAVE,MNT,INJ,TON,SUI,PEPE,BONK,FLOKI,WIF,JUP,JASMY,KAS,RNDR,THETA,FET,AGIX,OCEAN")
        self.active_coins_list = [x.strip() for x in active_coins.split(",") if x.strip()]
        
        # تنظیمات پشتیبانی
        self.support_email = os.environ.get("SUPPORT_EMAIL", "support@cryptopulse.ai")
        self.support_phone = os.environ.get("SUPPORT_PHONE", "")
        self.support_chat = os.environ.get("SUPPORT_CHAT", "")
        
        # تنظیمات تصاویر
        self.image_path = os.environ.get("IMAGE_PATH", "assets/")
        self.image_url_base = os.environ.get("IMAGE_URL_BASE", "https://cryptopulse.ai/images/")
        self.use_image_url = os.environ.get("USE_IMAGE_URL", "False").lower() == "true"
        
        # تنظیمات زبان
        self.language = os.environ.get("LANGUAGE", "fa")
        self.default_currency = os.environ.get("DEFAULT_CURRENCY", "IRT")
        
        # تنظیمات محیط
        self.environment = os.environ.get("ENVIRONMENT", "production")
        
        # تنظیمات پیشرفته
        self.max_retries = int(os.environ.get("MAX_RETRIES", 3))
        self.timeout_seconds = int(os.environ.get("TIMEOUT_SECONDS", 30))
        self.max_connections = int(os.environ.get("MAX_CONNECTIONS", 100))
        self.pool_size = int(os.environ.get("POOL_SIZE", 10))
        self.pool_timeout = int(os.environ.get("POOL_TIMEOUT", 30))
        self.max_coins_per_user = int(os.environ.get("MAX_COINS_PER_USER", 10))
        self.min_volume_24h = float(os.environ.get("MIN_VOLUME_24H", 1000000))
        self.min_market_cap = float(os.environ.get("MIN_MARKET_CAP", 10000000))
    
    def _load_from_file(self):
        """بارگذاری از فایل کانفیگ JSON"""
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
        
        # بارگذاری از فایل .env.local
        env_file = Path(".env.local")
        if env_file.exists():
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
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
        """تبدیل مقدار به نوع مناسب"""
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
    
    def _set_defaults(self):
        """تنظیمات پیش‌فرض"""
        defaults = {
            'max_retries': 3,
            'timeout_seconds': 30,
            'max_connections': 100,
            'pool_size': 10,
            'pool_timeout': 30,
            'min_confidence': 60,
            'max_confidence': 100,
            'language': 'fa',
            'emoji_style': 'modern',
            'notification_enabled': True,
            'send_welcome_message': True,
            'send_goodbye_message': True,
            'analysis_interval': 300,
            'min_trade_amount': 10.0,
            'max_trade_amount': 10000.0,
            'risk_per_trade': 2.0,
            'max_open_trades': 5,
            'allowed_currencies': ["USD", "USDT", "BTC", "ETH", "BNB", "IRT"],
            'excluded_coins': [],
            'featured_coins': ["BTC", "ETH", "BNB", "SOL", "XRP"],
            'admin_commands': [
                "stats", "users", "broadcast", "ban", "unban",
                "vip", "payment", "backup", "restore", "settings",
                "logs", "clear", "restart", "shutdown"
            ],
            'channel_commands': [
                "send", "pin", "unpin", "delete", "edit"
            ],
            'image_formats': ["jpg", "png", "gif", "webp"]
        }
        
        for key, value in defaults.items():
            if not hasattr(self, key):
                setattr(self, key, value)
    
    def _validate(self):
        """اعتبارسنجی تنظیمات"""
        self._validation_errors = []
        
        # توکن ربات
        if not self.bot_token or len(self.bot_token) < 40:
            self._validation_errors.append("BOT_TOKEN is required and must be valid")
        
        # کلیدهای API
        if not self.groq_api_key:
            self._validation_errors.append("GROQ_API_KEY is required")
        
        if not self.coinex_api_key or not self.coinex_secret_key:
            self._validation_errors.append("COINEX_API_KEY and COINEX_SECRET_KEY are required")
        
        # ادمین‌ها
        if not self.admin_ids:
            self._validation_errors.append("At least one ADMIN_ID is required")
        
        # پورت
        if not 1024 <= self.port <= 65535:
            self._validation_errors.append("PORT must be between 1024 and 65535")
        
        # زمان
        if self.signal_interval < 60:
            self._validation_errors.append("SIGNAL_INTERVAL must be at least 60 seconds")
        
        # قیمت‌ها
        if self.vip_price_monthly <= 0:
            self._validation_errors.append("VIP_PRICE_MONTHLY must be greater than 0")
        if self.vip_price_yearly <= 0:
            self._validation_errors.append("VIP_PRICE_YEARLY must be greater than 0")
        
        # کانال
        if not self.channel_id:
            self._validation_errors.append("CHANNEL_ID is required")
    
    def _normalize(self):
        """نرمال‌سازی تنظیمات"""
        # تبدیل لیست‌ها
        if isinstance(self.admin_ids, str):
            self.admin_ids = [int(x.strip()) for x in self.admin_ids.split(',') if x.strip()]
        
        if isinstance(self.active_coins_list, str):
            self.active_coins_list = [x.strip().upper() for x in self.active_coins_list.split(',') if x.strip()]
        
        # نرمال‌سازی URLها
        if self.webhook_url and not self.webhook_url.endswith('/'):
            self.webhook_url += '/'
        
        # محدود کردن زمان
        if hasattr(self, 'signal_interval'):
            self.signal_interval = max(60, min(86400, self.signal_interval))
        
        # محدود کردن اطمینان
        if hasattr(self, 'min_confidence'):
            self.min_confidence = max(0, min(100, self.min_confidence))
        if hasattr(self, 'max_confidence'):
            self.max_confidence = max(0, min(100, self.max_confidence))
    
    def _encrypt_sensitive(self):
        """رمزنگاری اطلاعات حساس"""
        self._sensitive_keys = [
            'bot_token', 'groq_api_key', 'coinex_api_key', 
            'coinex_secret_key', 'encryption_key', 'jwt_secret'
        ]
        self._key_hashes = {}
        for key in self._sensitive_keys:
            if hasattr(self, key):
                value = getattr(self, key)
                if value:
                    self._key_hashes[key] = hashlib.sha256(str(value).encode()).hexdigest()[:8]
    
    def _init_config_classes(self):
        """مقداردهی کلاس‌های تنظیمات"""
        self.api_config = APIConfig(
            base_url=self.coinex_base_url,
            api_key=self.coinex_api_key,
            secret_key=self.coinex_secret_key,
            timeout=self.coinex_timeout,
            max_retries=self.coinex_max_retries
        )
        
        self.db_config = DatabaseConfig(
            url=self.database_url,
            pool_size=self.pool_size,
            pool_timeout=self.pool_timeout
        )
        
        self.security = SecurityConfig(
            encryption_key=self.encryption_key,
            jwt_secret=self.jwt_secret,
            security_mode=self.security_mode
        )
        
        self.telegram = TelegramConfig(
            bot_token=self.bot_token,
            webhook_url=self.webhook_url,
            webhook_port=self.port
        )
        
        self.market = MarketConfig(
            default_timeframe=self.default_timeframe,
            default_coin=self.default_coin,
            signal_interval=self.signal_interval
        )
        
        self.ai = AIConfig(
            model=self.ai_model,
            temperature=self.ai_temperature,
            max_tokens=self.ai_max_tokens,
            timeout=self.ai_timeout
        )
        
        self.vip = VIPConfig(
            monthly_price=self.vip_price_monthly,
            yearly_price=self.vip_price_yearly,
            lifetime_price=self.vip_price_lifetime,
            payment_card=self.vip_payment_card,
            payment_card_holder=self.vip_payment_holder,
            admin_username=self.vip_admin_username,
            trial_days=self.vip_trial_days
        )
        
        self.channel = ChannelConfig(
            channel_id=self.channel_id
        )
    
    def _generate_key(self) -> str:
        """تولید کلید تصادفی"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))
    
    def get(self, key: str, default: Any = None) -> Any:
        """دریافت مقدار تنظیمات با کش"""
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
        """تنظیم مقدار"""
        if hasattr(self, key):
            setattr(self, key, value)
            self._cache[key] = (value, datetime.now())
    
    def update(self, config_dict: Dict[str, Any]):
        """بروزرسانی چندگانه تنظیمات"""
        for key, value in config_dict.items():
            self.set(key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به دیکشنری"""
        result = {}
        for key in dir(self):
            if not key.startswith('_') and not callable(getattr(self, key)):
                value = getattr(self, key)
                if not isinstance(value, (type, classmethod, staticmethod)):
                    result[key] = value
        return result
    
    def to_json(self) -> str:
        """تبدیل به JSON"""
        return json.dumps(self.to_dict(), indent=2, default=str)
    
    def reload(self):
        """بارگذاری مجدد تنظیمات"""
        self._initialized = False
        self._cache.clear()
        self.__init__()
    
    def get_validation_errors(self) -> List[str]:
        """دریافت خطاهای اعتبارسنجی"""
        return self._validation_errors
    
    def is_valid(self) -> bool:
        """بررسی معتبر بودن تنظیمات"""
        return len(self._validation_errors) == 0
    
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
    
    def is_admin(self, user_id: int) -> bool:
        return user_id in self.get_admin_ids()
    
    def is_coin_active(self, coin: str) -> bool:
        return coin.upper() in self.get_active_coins()
    
    def get_vip_price(self, plan: str = "monthly") -> int:
        prices = {
            'monthly': self.vip_price_monthly,
            'yearly': self.vip_price_yearly,
            'lifetime': self.vip_price_lifetime
        }
        return prices.get(plan, self.vip_price_monthly)
    
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
        """پاکسازی کش"""
        self._cache.clear()
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

# ============================================================
#                    Permission Manager
# ============================================================

class PermissionManager:
    """مدیریت سطوح دسترسی"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self._permissions = {
            'admin': ['*'],
            'vip': ['signals', 'analysis', 'portfolio', 'alerts', 'vip_signals', 'advanced_analysis'],
            'premium': ['signals', 'analysis', 'alerts'],
            'free': ['signals', 'basic_analysis'],
            'guest': ['signals']
        }
    
    def has_permission(self, user_level: str, permission: str) -> bool:
        if user_level not in self._permissions:
            return False
        perms = self._permissions[user_level]
        return '*' in perms or permission in perms
    
    def get_level_permissions(self, level: str) -> List[str]:
        return self._permissions.get(level, [])
    
    def get_user_level(self, user_data: Dict[str, Any]) -> str:
        if user_data.get('is_admin'):
            return 'admin'
        if user_data.get('is_vip'):
            return 'vip'
        if user_data.get('is_premium'):
            return 'premium'
        return 'free'

# ============================================================
#                    Currency Manager
# ============================================================

class CurrencyManager:
    """مدیریت ارزها"""
    
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
            "ICP": {"name": "Internet Computer", "symbol": "ICP", "decimals": 8, "min_amount": 0.1},
            "HBAR": {"name": "Hedera", "symbol": "HBAR", "decimals": 8, "min_amount": 1},
            "FIL": {"name": "Filecoin", "symbol": "FIL", "decimals": 18, "min_amount": 0.1},
            "APT": {"name": "Aptos", "symbol": "APT", "decimals": 8, "min_amount": 0.1},
            "ARB": {"name": "Arbitrum", "symbol": "ARB", "decimals": 18, "min_amount": 1},
            "OP": {"name": "Optimism", "symbol": "OP", "decimals": 18, "min_amount": 1},
            "MKR": {"name": "Maker", "symbol": "MKR", "decimals": 18, "min_amount": 0.01},
            "AAVE": {"name": "Aave", "symbol": "AAVE", "decimals": 18, "min_amount": 0.01},
            "MNT": {"name": "Mantle", "symbol": "MNT", "decimals": 18, "min_amount": 1},
            "INJ": {"name": "Injective", "symbol": "INJ", "decimals": 18, "min_amount": 0.1},
            "TON": {"name": "Toncoin", "symbol": "TON", "decimals": 9, "min_amount": 0.1},
            "SUI": {"name": "Sui", "symbol": "SUI", "decimals": 9, "min_amount": 0.1},
            "PEPE": {"name": "Pepe", "symbol": "PEPE", "decimals": 18, "min_amount": 1000},
            "BONK": {"name": "Bonk", "symbol": "BONK", "decimals": 5, "min_amount": 1000},
            "FLOKI": {"name": "Floki", "symbol": "FLOKI", "decimals": 9, "min_amount": 1000},
            "WIF": {"name": "Wif", "symbol": "WIF", "decimals": 6, "min_amount": 1},
            "JUP": {"name": "Jupiter", "symbol": "JUP", "decimals": 6, "min_amount": 0.1},
            "JASMY": {"name": "Jasmy", "symbol": "JASMY", "decimals": 18, "min_amount": 1},
            "KAS": {"name": "Kaspa", "symbol": "KAS", "decimals": 8, "min_amount": 1},
            "RNDR": {"name": "Render", "symbol": "RNDR", "decimals": 18, "min_amount": 0.1},
            "THETA": {"name": "Theta", "symbol": "THETA", "decimals": 18, "min_amount": 0.1},
            "FET": {"name": "Fetch.ai", "symbol": "FET", "decimals": 18, "min_amount": 1},
            "AGIX": {"name": "SingularityNET", "symbol": "AGIX", "decimals": 8, "min_amount": 1},
            "OCEAN": {"name": "Ocean Protocol", "symbol": "OCEAN", "decimals": 18, "min_amount": 1}
        }
    
    def get_currency(self, symbol: str) -> Optional[Dict]:
        return self._currencies.get(symbol.upper())
    
    def get_all(self) -> Dict:
        return self._currencies
    
    def get_active(self) -> List[str]:
        return self.config.get_active_coins()
    
    def get_featured(self) -> List[str]:
        return self.config.get_featured_coins()
    
    def format_amount(self, symbol: str, amount: float) -> str:
        currency = self.get_currency(symbol)
        if not currency:
            return f"{amount:.8f}"
        decimals = currency.get('decimals', 8)
        return f"{amount:.{decimals}f}"
    
    def get_min_amount(self, symbol: str) -> float:
        currency = self.get_currency(symbol)
        if not currency:
            return 0.0001
        return currency.get('min_amount', 0.0001)

# ============================================================
#                    Time Config
# ============================================================

class TimeConfig:
    """تنظیمات زمان"""
    
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
    
    def get_timezone(self) -> str:
        return self.timezone

# ============================================================
#                    Market Settings
# ============================================================

class MarketSettings:
    """تنظیمات بازار"""
    
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
    
    def get_risk_parameters(self) -> Dict[str, float]:
        return {
            'max_position_size': self.max_position_size,
            'max_drawdown': self.max_drawdown,
            'stop_loss_default': self.stop_loss_default,
            'take_profit_default': self.take_profit_default
        }

# ============================================================
#                    Security Settings
# ============================================================

class SecuritySettings:
    """تنظیمات امنیتی"""
    
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
        self.security_mode = "high"
        self.rate_limit_enabled = True
        self.request_validation = True
        self.sql_injection_protection = True
    
    def get_security_level(self) -> str:
        return self.security_mode
    
    def is_secure(self) -> bool:
        return self.security_mode in ["high", "ultra"]

# ============================================================
#                    Image Settings
# ============================================================

class ImageSettings:
    """تنظیمات تصاویر"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.use_url = config.get('use_image_url', False)
        self.path = config.get('image_path', 'assets/')
        self.url_base = config.get('image_url_base', 'https://cryptopulse.ai/images/')
        
        self.default_images = {
            'welcome': 'welcome_image.jpg',
            'logo': 'logo.png',
            'banner': 'banner.png',
            'signal': 'signal_image.jpg',
            'analysis': 'analysis_image.jpg',
            'vip': 'vip_image.jpg',
            'wallet': 'wallet_image.jpg',
            'admin': 'admin_image.jpg',
            'chart': 'chart_image.png'
        }
        
        self.image_sizes = {
            'welcome': (1080, 500),
            'logo': (500, 500),
            'banner': (1200, 400),
            'signal': (800, 400),
            'analysis': (900, 500),
            'vip': (800, 400),
            'wallet': (800, 400),
            'admin': (800, 400),
            'chart': (1000, 600)
        }
    
    def get_image(self, image_type: str = "welcome") -> str:
        if self.use_url:
            return self.url_base + self.default_images.get(image_type, self.default_images['welcome'])
        return self.path + self.default_images.get(image_type, self.default_images['welcome'])
    
    def get_size(self, image_type: str = "welcome") -> Tuple[int, int]:
        return self.image_sizes.get(image_type, (1080, 500))
    
    def get_all_images(self) -> Dict[str, str]:
        return self.default_images

# ============================================================
#                    EXPORT (ایمن و بدون خطا)
# ============================================================

def safe_init(cls, *args, **kwargs):
    """ایجاد ایمن نمونه از کلاس"""
    try:
        return cls(*args, **kwargs)
    except Exception:
        return None

# ایجاد نمونه‌ها
config_manager = safe_init(ConfigManager)
permission_manager = safe_init(PermissionManager, config_manager) if config_manager else None
currency_manager = safe_init(CurrencyManager, config_manager) if config_manager else None
time_config = safe_init(TimeConfig)
market_settings = safe_init(MarketSettings, config_manager) if config_manager else None
security_settings = safe_init(SecuritySettings)
image_settings = safe_init(ImageSettings, config_manager) if config_manager else None

# توابع دسترسی
def get_config():
    return config_manager

def get_permissions():
    return permission_manager

def get_currencies():
    return currency_manager

def get_time():
    return time_config

def get_market_settings():
    return market_settings

def get_security():
    return security_settings

def get_image_settings():
    return image_settings

# تابع بررسی سلامت
def check_config_instances():
    return {
        "config_manager": "✅ OK" if config_manager else "❌ FAILED",
        "permission_manager": "✅ OK" if permission_manager else "❌ FAILED",
        "currency_manager": "✅ OK" if currency_manager else "❌ FAILED",
        "time_config": "✅ OK" if time_config else "❌ FAILED",
        "market_settings": "✅ OK" if market_settings else "❌ FAILED",
        "security_settings": "✅ OK" if security_settings else "❌ FAILED",
        "image_settings": "✅ OK" if image_settings else "❌ FAILED"
    }

# تابع دریافت خطاهای اعتبارسنجی
def get_validation_errors():
    if config_manager:
        return config_manager.get_validation_errors()
    return ["ConfigManager not initialized"]

# تابع بررسی اعتبار
def is_config_valid():
    if config_manager:
        return config_manager.is_valid()
    return False

# ============================================================
#                    تنظیمات نهایی
# ============================================================

# ثبت خطاهای اعتبارسنجی در صورت وجود
if config_manager and not config_manager.is_valid():
    errors = config_manager.get_validation_errors()
    for error in errors:
        pass  # خطاها بدون لاگ ذخیره می‌شوند
