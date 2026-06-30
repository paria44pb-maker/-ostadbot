
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - Database Module
ماژول دیتابیس کامل با مدل‌های پیشرفته، ایندکس‌ها و روابط
"""

import os
import sys
import json
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple, Union, Generator
from dataclasses import dataclass, field
from enum import Enum
from contextlib import contextmanager
from sqlalchemy import (
    create_engine, Column, String, Integer, Float, DateTime,
    Boolean, Text, BigInteger, Date, Time, Interval, ForeignKey,
    Index, UniqueConstraint, CheckConstraint, func, and_, or_, not_,
    desc, asc, event, MetaData, Table, inspect, text
)
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import (
    sessionmaker, relationship, backref, aliased,
    Query, Session, joinedload, selectinload, contains_eager
)
from sqlalchemy.pool import QueuePool, NullPool
from sqlalchemy.sql.expression import case, cast
from sqlalchemy.dialects.postgresql import JSONB, UUID, ARRAY
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON

# ==================== تنظیمات پایه ====================

Base = declarative_base()
metadata = Base.metadata

# ==================== توابع کمکی دیتابیس ====================

def get_tehran_time():
    import pytz
    tehran = pytz.timezone('Asia/Tehran')
    return datetime.now(tehran)

def json_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

# ==================== کلاس‌های پایه مدل ====================

class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=get_tehran_time, nullable=False)
    updated_at = Column(DateTime, default=get_tehran_time, onupdate=get_tehran_time)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def to_dict(self, include_relations: bool = False) -> Dict[str, Any]:
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, Enum):
                value = value.value
            result[column.name] = value
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=json_serializer)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        obj = cls()
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

# ==================== مدل کاربر ====================

class User(BaseModel):
    __tablename__ = 'users'

    # اطلاعات پایه
    telegram_id = Column(String(50), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone_number = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)

    # وضعیت
    is_active = Column(Boolean, default=True)
    is_banned = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_vip = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)

    # VIP
    vip_level = Column(Integer, default=0)
    vip_expire = Column(DateTime, nullable=True)
    vip_purchase_date = Column(DateTime, nullable=True)
    vip_plan = Column(String(20), nullable=True)  # monthly, yearly, lifetime

    # مالی
    balance = Column(Float, default=0.0)
    total_deposited = Column(Float, default=0.0)
    total_withdrawn = Column(Float, default=0.0)
    total_spent = Column(Float, default=0.0)
    total_profit = Column(Float, default=0.0)

    # ارجاع
    referral_code = Column(String(20), unique=True, nullable=True)
    referred_by = Column(String(50), nullable=True)
    referral_count = Column(Integer, default=0)
    referral_earnings = Column(Float, default=0.0)

    # تنظیمات کاربر
    preferences = Column(Text, default='{}')
    language = Column(String(10), default='fa')
    timezone = Column(String(50), default='Asia/Tehran')
    notification_enabled = Column(Boolean, default=True)

    # آمار
    total_signals = Column(Integer, default=0)
    total_trades = Column(Integer, default=0)
    successful_trades = Column(Integer, default=0)
    failed_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)

    # زمان‌ها
    last_activity = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)
    registered_at = Column(DateTime, default=get_tehran_time)

    # اطلاعات اضافی
    metadata_json = Column(Text, default='{}')

    # روابط
    signals = relationship("Signal", back_populates="user", lazy="dynamic")
    trades = relationship("Trade", back_populates="user", lazy="dynamic")
    payments = relationship("Payment", back_populates="user", lazy="dynamic")
    favorites = relationship("Favorite", back_populates="user", lazy="dynamic")
    alerts = relationship("Alert", back_populates="user", lazy="dynamic")
    channel_messages = relationship("ChannelMessage", back_populates="user", lazy="dynamic")

    # ایندکس‌ها
    __table_args__ = (
        Index('idx_user_telegram_id', 'telegram_id'),
        Index('idx_user_username', 'username'),
        Index('idx_user_is_active', 'is_active'),
        Index('idx_user_is_vip', 'is_vip'),
        Index('idx_user_vip_expire', 'vip_expire'),
        Index('idx_user_registered_at', 'registered_at'),
        Index('idx_user_referral_code', 'referral_code'),
        Index('idx_user_is_banned', 'is_banned'),
        Index('idx_user_is_admin', 'is_admin'),
    )

    def __repr__(self):
        return f"<User {self.telegram_id} - {self.username or self.first_name}>"

    def get_full_name(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.username or str(self.telegram_id)

    def get_preferences(self) -> Dict[str, Any]:
        try:
            return json.loads(self.preferences) if self.preferences else {}
        except:
            return {}

    def set_preference(self, key: str, value: Any):
        prefs = self.get_preferences()
        prefs[key] = value
        self.preferences = json.dumps(prefs)

    def get_metadata(self) -> Dict[str, Any]:
        try:
            return json.loads(self.metadata_json) if self.metadata_json else {}
        except:
            return {}

    def set_metadata(self, key: str, value: Any):
        meta = self.get_metadata()
        meta[key] = value
        self.metadata_json = json.dumps(meta)

    def is_vip_active(self) -> bool:
        if not self.is_vip:
            return False
        if not self.vip_expire:
            return False
        return self.vip_expire > get_tehran_time()

    def get_vip_days_left(self) -> int:
        if not self.is_vip_active():
            return 0
        delta = self.vip_expire - get_tehran_time()
        return max(0, delta.days)

    def update_win_rate(self):
        total = self.total_trades
        if total > 0:
            self.win_rate = (self.successful_trades / total) * 100
        else:
            self.win_rate = 0.0

# ==================== مدل سیگنال ====================

class Signal(BaseModel):
    __tablename__ = 'signals'

    # اطلاعات سیگنال
    coin = Column(String(20), nullable=False, index=True)
    exchange = Column(String(20), default='CoinEx')
    signal_type = Column(String(20), nullable=False)
    timeframe = Column(String(10), default='4h')

    # قیمت‌ها
    current_price = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=True)
    target_price_1 = Column(Float, nullable=True)
    target_price_2 = Column(Float, nullable=True)
    target_price_3 = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)

    # سطوح
    support_1 = Column(Float, nullable=True)
    support_2 = Column(Float, nullable=True)
    resistance_1 = Column(Float, nullable=True)
    resistance_2 = Column(Float, nullable=True)

    # اندیکاتورها
    rsi = Column(Float, nullable=True)
    macd = Column(Float, nullable=True)
    macd_signal = Column(Float, nullable=True)
    macd_histogram = Column(Float, nullable=True)
    sma_7 = Column(Float, nullable=True)
    sma_25 = Column(Float, nullable=True)
    sma_99 = Column(Float, nullable=True)
    ema_12 = Column(Float, nullable=True)
    ema_26 = Column(Float, nullable=True)
    bb_upper = Column(Float, nullable=True)
    bb_middle = Column(Float, nullable=True)
    bb_lower = Column(Float, nullable=True)
    adx = Column(Float, nullable=True)
    mfi = Column(Float, nullable=True)
    cci = Column(Float, nullable=True)

    # نمرات
    confidence = Column(Integer, default=50)
    risk_score = Column(Integer, default=50)
    reward_ratio = Column(Float, default=0.0)

    # تحلیل
    ai_analysis = Column(Text, nullable=True)
    technical_analysis = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)

    # وضعیت
    is_active = Column(Boolean, default=True)
    is_executed = Column(Boolean, default=False)
    is_vip = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)

    # نتایج
    result_price = Column(Float, nullable=True)
    result_profit = Column(Float, nullable=True)
    result_percentage = Column(Float, nullable=True)
    executed_at = Column(DateTime, nullable=True)

    # اطلاعات
    user_id = Column(String(50), ForeignKey('users.telegram_id'), nullable=True)
    metadata_json = Column(Text, default='{}')

    # روابط
    user = relationship("User", back_populates="signals")
    trades = relationship("Trade", back_populates="signal", lazy="dynamic")

    # ایندکس‌ها
    __table_args__ = (
        Index('idx_signal_coin', 'coin'),
        Index('idx_signal_type', 'signal_type'),
        Index('idx_signal_confidence', 'confidence'),
        Index('idx_signal_is_active', 'is_active'),
        Index('idx_signal_is_vip', 'is_vip'),
        Index('idx_signal_created_at', 'created_at'),
        Index('idx_signal_user_id', 'user_id'),
        Index('idx_signal_coin_type_active', 'coin', 'signal_type', 'is_active'),
        Index('idx_signal_timeframe', 'timeframe'),
    )

    def __repr__(self):
        return f"<Signal {self.coin} - {self.signal_type} - {self.confidence}%>"

    def get_metadata(self) -> Dict[str, Any]:
        try:
            return json.loads(self.metadata_json) if self.metadata_json else {}
        except:
            return {}

    def get_targets(self) -> List[float]:
        targets = []
        if self.target_price_1:
            targets.append(self.target_price_1)
        if self.target_price_2:
            targets.append(self.target_price_2)
        if self.target_price_3:
            targets.append(self.target_price_3)
        return targets

    def calculate_risk_reward(self) -> float:
        if not self.entry_price or not self.stop_loss:
            return 0.0
        if not self.target_price_1:
            return 0.0

        risk = abs(self.entry_price - self.stop_loss)
        reward = abs(self.target_price_1 - self.entry_price)

        if risk == 0:
            return 0.0
        return reward / risk

    def is_expired(self) -> bool:
        expiry_hours = 24 if self.timeframe == '1d' else 4
        expiry_time = self.created_at + timedelta(hours=expiry_hours)
        return get_tehran_time() > expiry_time

    def get_signal_emoji(self) -> str:
        emojis = {
            'buy': '🟢',
            'sell': '🔴',
            'hold': '🟡',
            'strong_buy': '💚',
            'strong_sell': '❤️'
        }
        return emojis.get(self.signal_type, '⚪')

# ==================== مدل معامله ====================

class Trade(BaseModel):
    __tablename__ = 'trades'

    trade_id = Column(String(50), unique=True, nullable=False)
    user_id = Column(String(50), ForeignKey('users.telegram_id'), nullable=False)
    signal_id = Column(Integer, ForeignKey('signals.id'), nullable=True)

    coin = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)
    order_type = Column(String(20), default='limit')

    amount = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    fee = Column(Float, default=0.0)
    fee_currency = Column(String(10), default='USDT')

    status = Column(String(20), default='pending')
    is_open = Column(Boolean, default=True)
    is_closed = Column(Boolean, default=False)

    close_price = Column(Float, nullable=True)
    close_amount = Column(Float, nullable=True)
    close_total = Column(Float, nullable=True)
    profit = Column(Float, nullable=True)
    profit_percentage = Column(Float, nullable=True)

    opened_at = Column(DateTime, default=get_tehran_time)
    closed_at = Column(DateTime, nullable=True)

    metadata_json = Column(Text, default='{}')

    user = relationship("User", back_populates="trades")
    signal = relationship("Signal", back_populates="trades")

    __table_args__ = (
        Index('idx_trade_user_id', 'user_id'),
        Index('idx_trade_coin', 'coin'),
        Index('idx_trade_status', 'status'),
        Index('idx_trade_is_open', 'is_open'),
        Index('idx_trade_created_at', 'created_at'),
        Index('idx_trade_trade_id', 'trade_id'),
        Index('idx_trade_user_coin', 'user_id', 'coin'),
    )

    def __repr__(self):
        return f"<Trade {self.trade_id} - {self.coin} - {self.side}>"

    def get_metadata(self) -> Dict[str, Any]:
        try:
            return json.loads(self.metadata_json) if self.metadata_json else {}
        except:
            return {}

    def calculate_profit(self, close_price: float):
        if self.side == 'buy':
            self.profit = (close_price - self.price) * self.amount
        else:
            self.profit = (self.price - close_price) * self.amount

        self.profit_percentage = (self.profit / self.total) * 100
        self.close_price = close_price
        self.close_amount = self.amount
        self.close_total = close_price * self.amount
        self.closed_at = get_tehran_time()
        self.is_open = False
        self.is_closed = True
        self.status = 'closed'

# ==================== مدل پرداخت ====================

class Payment(BaseModel):
    __tablename__ = 'payments'

    payment_id = Column(String(50), unique=True, nullable=False)
    user_id = Column(String(50), ForeignKey('users.telegram_id'), nullable=False)

    amount = Column(Float, nullable=False)
    currency = Column(String(10), default='IRT')
    payment_type = Column(String(20), nullable=False)

    status = Column(String(20), default='pending')
    gateway = Column(String(20), default='card')
    transaction_id = Column(String(100), nullable=True)
    receipt_image = Column(String(500), nullable=True)

    description = Column(Text, nullable=True)
    metadata_json = Column(Text, default='{}')
    admin_note = Column(Text, nullable=True)

    completed_at = Column(DateTime, nullable=True)
    refunded_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="payments")

    __table_args__ = (
        Index('idx_payment_user_id', 'user_id'),
        Index('idx_payment_status', 'status'),
        Index('idx_payment_type', 'payment_type'),
        Index('idx_payment_created_at', 'created_at'),
        Index('idx_payment_payment_id', 'payment_id'),
        Index('idx_payment_transaction_id', 'transaction_id'),
    )

    def __repr__(self):
        return f"<Payment {self.payment_id} - {self.amount} {self.currency}>"

    def get_metadata(self) -> Dict[str, Any]:
        try:
            return json.loads(self.metadata_json) if self.metadata_json else {}
        except:
            return {}

# ==================== مدل علاقه‌مندی‌ها ====================

class Favorite(BaseModel):
    __tablename__ = 'favorites'

    user_id = Column(String(50), ForeignKey('users.telegram_id'), nullable=False)
    coin = Column(String(20), nullable=False)
    exchange = Column(String(20), default='CoinEx')

    price_alert = Column(Boolean, default=True)
    signal_alert = Column(Boolean, default=True)
    alert_threshold = Column(Float, nullable=True)

    last_check = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="favorites")

    __table_args__ = (
        UniqueConstraint('user_id', 'coin', name='uq_user_coin'),
        Index('idx_favorite_user_id', 'user_id'),
        Index('idx_favorite_coin', 'coin'),
        Index('idx_favorite_price_alert', 'price_alert'),
    )

    def __repr__(self):
        return f"<Favorite {self.user_id} - {self.coin}>"

# ==================== مدل هشدار ====================

class Alert(BaseModel):
    __tablename__ = 'alerts'

    user_id = Column(String(50), ForeignKey('users.telegram_id'), nullable=False)
    alert_type = Column(String(20), nullable=False)
    coin = Column(String(20), nullable=True)

    condition = Column(String(20), nullable=True)
    value = Column(Float, nullable=True)

    is_active = Column(Boolean, default=True)
    is_triggered = Column(Boolean, default=False)

    triggered_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="alerts")

    __table_args__ = (
        Index('idx_alert_user_id', 'user_id'),
        Index('idx_alert_is_active', 'is_active'),
        Index('idx_alert_coin', 'coin'),
        Index('idx_alert_type', 'alert_type'),
    )

    def __repr__(self):
        return f"<Alert {self.user_id} - {self.alert_type}>"

# ==================== مدل تنظیمات ====================

class Setting(BaseModel):
    __tablename__ = 'settings'

    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=True)
    data_type = Column(String(20), default='string')

    description = Column(Text, nullable=True)
    category = Column(String(50), default='general')
    is_public = Column(Boolean, default=False)

    __table_args__ = (
        Index('idx_setting_key', 'key'),
        Index('idx_setting_category', 'category'),
    )

    def __repr__(self):
        return f"<Setting {self.key} = {self.value}>"

    def get_value(self):
        if self.data_type == 'int':
            return int(self.value) if self.value else 0
        elif self.data_type == 'float':
            return float(self.value) if self.value else 0.0
        elif self.data_type == 'boolean':
            return self.value.lower() == 'true' if self.value else False
        elif self.data_type == 'json':
            return json.loads(self.value) if self.value else {}
        else:
            return self.value

# ==================== مدل بکاپ ====================

class Backup(BaseModel):
    __tablename__ = 'backups'

    backup_id = Column(String(50), unique=True, nullable=False)
    filename = Column(String(200), nullable=False)
    file_size = Column(Integer, default=0)
    checksum = Column(String(64), nullable=True)

    backup_type = Column(String(20), default='full')
    status = Column(String(20), default='created')

    path = Column(String(500), nullable=True)
    url = Column(String(500), nullable=True)

    restored_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index('idx_backup_backup_id', 'backup_id'),
        Index('idx_backup_status', 'status'),
        Index('idx_backup_created_at', 'created_at'),
        Index('idx_backup_type', 'backup_type'),
    )

    def __repr__(self):
        return f"<Backup {self.backup_id} - {self.filename}>"

# ==================== مدل پیام کانال ====================

class ChannelMessage(BaseModel):
    __tablename__ = 'channel_messages'

    message_id = Column(Integer, nullable=False)
    channel_id = Column(String(50), default="@CryptoPulse606")

    message_type = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)

    coin = Column(String(20), nullable=True)
    signal_type = Column(String(10), nullable=True)
    confidence = Column(Integer, nullable=True)

    is_sent = Column(Boolean, default=True)
    is_pinned = Column(Boolean, default=False)
    views = Column(Integer, default=0)
    reactions = Column(Integer, default=0)

    user_id = Column(String(50), ForeignKey('users.telegram_id'), nullable=True)
    sent_at = Column(DateTime, default=get_tehran_time)

    user = relationship("User", back_populates="channel_messages")

    __table_args__ = (
        Index('idx_channel_message_type', 'message_type'),
        Index('idx_channel_message_created', 'created_at'),
        Index('idx_channel_message_coin', 'coin'),
        Index('idx_channel_message_sent', 'sent_at'),
        Index('idx_channel_message_user_id', 'user_id'),
    )

    def __repr__(self):
        return f"<ChannelMessage {self.message_id} - {self.message_type}>"

# ==================== کلاس مدیریت دیتابیس ====================

class DatabaseManager:
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

        from bot2 import get_config
        config = get_config()

        self.engine = None
        self.SessionLocal = None
        self._setup_engine(config)
        self._setup_session()
        self._create_tables()
        self._create_indexes()
        self._setup_listeners()
        self._init_default_settings()

    def _setup_engine(self, config):
        database_url = config.get('database_url', 'sqlite:///bot.db')

        pool_size = config.get('pool_size', 10)
        max_overflow = config.get('max_overflow', 20)
        pool_timeout = config.get('pool_timeout', 30)
        pool_recycle = config.get('pool_recycle', 3600)

        if database_url.startswith('sqlite'):
            connect_args = {'check_same_thread': False}
            pool_class = NullPool
        else:
            connect_args = {}
            pool_class = QueuePool

        self.engine = create_engine(
            database_url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            pool_pre_ping=True,
            poolclass=pool_class,
            connect_args=connect_args,
            echo=False,
            hide_parameters=True
        )

    def _setup_session(self):
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def _create_tables(self):
        Base.metadata.create_all(bind=self.engine)

    def _create_indexes(self):
        with self.engine.connect() as conn:
            if self.engine.dialect.name == 'sqlite':
                conn.execute(text("PRAGMA journal_mode=WAL"))
                conn.execute(text("PRAGMA synchronous=NORMAL"))
                conn.execute(text("PRAGMA cache_size=10000"))

    def _setup_listeners(self):
        @event.listens_for(User, 'before_update')
        def user_before_update(mapper, connection, target):
            target.updated_at = get_tehran_time()

        @event.listens_for(Signal, 'before_update')
        def signal_before_update(mapper, connection, target):
            target.updated_at = get_tehran_time()

    def _init_default_settings(self):
        default_settings = {
            'system_name': {'value': 'CryptoPulse AI', 'type': 'string'},
            'system_version': {'value': '3.0.0', 'type': 'string'},
            'maintenance_mode': {'value': 'false', 'type': 'boolean'},
            'max_users': {'value': '10000', 'type': 'int'},
            'signal_interval': {'value': '14400', 'type': 'int'},
            'vip_price_monthly': {'value': '199000', 'type': 'int'},
            'vip_price_yearly': {'value': '1990000', 'type': 'int'},
            'vip_price_lifetime': {'value': '4990000', 'type': 'int'},
            'vip_payment_card': {'value': '6063731196254479', 'type': 'string'},
            'vip_payment_holder': {'value': 'به مرد', 'type': 'string'},
            'vip_admin_username': {'value': 'Amir92aa', 'type': 'string'},
            'channel_id': {'value': '@CryptoPulse606', 'type': 'string'},
            'default_coin': {'value': 'BTC', 'type': 'string'},
            'default_timeframe': {'value': '4h', 'type': 'string'},
            'min_confidence': {'value': '60', 'type': 'int'},
            'max_confidence': {'value': '100', 'type': 'int'},
            'enable_signals': {'value': 'true', 'type': 'boolean'},
            'enable_ai': {'value': 'true', 'type': 'boolean'},
            'enable_vip': {'value': 'true', 'type': 'boolean'},
            'enable_payments': {'value': 'true', 'type': 'boolean'},
            'enable_referrals': {'value': 'true', 'type': 'boolean'},
            'enable_images': {'value': 'true', 'type': 'boolean'},
        }

        session = self.SessionLocal()
        try:
            for key, config in default_settings.items():
                setting = session.query(Setting).filter_by(key=key).first()
                if not setting:
                    setting = Setting(
                        key=key,
                        value=config['value'],
                        data_type=config['type'],
                        category='system'
                    )
                    session.add(setting)
            session.commit()
        except:
            session.rollback()
        finally:
            session.close()

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def health_check(self) -> Dict[str, Any]:
        try:
            with self.get_session() as session:
                result = session.execute(text("SELECT 1"))
                return {
                    'status': 'healthy',
                    'engine': self.engine.dialect.name,
                    'connected': True
                }
        except:
            return {
                'status': 'unhealthy',
                'error': 'Connection failed',
                'connected': False
            }

    def backup(self, backup_path: str = None) -> Dict[str, Any]:
        if not backup_path:
            backup_path = f"./backups/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

        os.makedirs(os.path.dirname(backup_path), exist_ok=True)

        try:
            if self.engine.dialect.name == 'sqlite':
                import shutil
                db_path = self.engine.url.database
                shutil.copy2(db_path, backup_path)

                with open(backup_path, 'rb') as f:
                    checksum = hashlib.sha256(f.read()).hexdigest()

                return {
                    'success': True,
                    'path': backup_path,
                    'checksum': checksum,
                    'size': os.path.getsize(backup_path)
                }
            else:
                return {
                    'success': False,
                    'error': 'PostgreSQL backup not implemented yet'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def restore(self, backup_path: str) -> Dict[str, Any]:
        try:
            if self.engine.dialect.name == 'sqlite':
                import shutil
                db_path = self.engine.url.database
                shutil.copy2(db_path, f"{db_path}.backup")
                shutil.copy2(backup_path, db_path)

                return {
                    'success': True,
                    'message': 'Database restored successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'PostgreSQL restore not implemented yet'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def vacuum(self) -> Dict[str, Any]:
        try:
            with self.engine.connect() as conn:
                if self.engine.dialect.name == 'sqlite':
                    conn.execute(text("VACUUM"))
                    conn.execute(text("ANALYZE"))
                else:
                    conn.execute(text("VACUUM ANALYZE"))
            return {'success': True, 'message': 'Database optimized'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_stats(self) -> Dict[str, Any]:
        stats = {}
        with self.get_session() as session:
            stats['users'] = session.query(User).count()
            stats['active_users'] = session.query(User).filter_by(is_active=True).count()
            stats['vip_users'] = session.query(User).filter_by(is_vip=True).count()
            stats['banned_users'] = session.query(User).filter_by(is_banned=True).count()
            stats['admins'] = session.query(User).filter_by(is_admin=True).count()

            stats['signals'] = session.query(Signal).count()
            stats['active_signals'] = session.query(Signal).filter_by(is_active=True).count()
            stats['vip_signals'] = session.query(Signal).filter_by(is_vip=True).count()

            stats['trades'] = session.query(Trade).count()
            stats['open_trades'] = session.query(Trade).filter_by(is_open=True).count()

            stats['payments'] = session.query(Payment).count()
            stats['pending_payments'] = session.query(Payment).filter_by(status='pending').count()
            stats['completed_payments'] = session.query(Payment).filter_by(status='completed').count()

            from sqlalchemy import func
            total_amount = session.query(func.sum(Payment.amount)).filter_by(status='completed').scalar()
            stats['total_revenue'] = float(total_amount or 0)

            today = get_tehran_time().date()
            today_payments = session.query(Payment).filter(
                func.date(Payment.completed_at) == today,
                Payment.status == 'completed'
            ).all()
            stats['today_revenue'] = sum(p.amount for p in today_payments)

            week_ago = get_tehran_time() - timedelta(days=7)
            week_payments = session.query(Payment).filter(
                Payment.completed_at >= week_ago,
                Payment.status == 'completed'
            ).all()
            stats['week_revenue'] = sum(p.amount for p in week_payments)

            month_ago = get_tehran_time() - timedelta(days=30)
            month_payments = session.query(Payment).filter(
                Payment.completed_at >= month_ago,
                Payment.status == 'completed'
            ).all()
            stats['month_revenue'] = sum(p.amount for p in month_payments)

            # VIP stats
            stats['active_vip'] = session.query(User).filter(
                User.is_vip == True,
                User.vip_expire > get_tehran_time()
            ).count()

            stats['pending_vip'] = session.query(Payment).filter(
                Payment.payment_type.like('vip_%'),
                Payment.status == 'pending'
            ).count()

            vip_payments = session.query(Payment).filter(
                Payment.payment_type.like('vip_%'),
                Payment.status == 'completed'
            ).all()
            stats['vip_revenue'] = sum(p.amount for p in vip_payments)

            # Today
            today_users = session.query(User).filter(
                func.date(User.registered_at) == today
            ).count()
            stats['today_users'] = today_users

            # Week
            week_ago_date = get_tehran_time() - timedelta(days=7)
            week_users = session.query(User).filter(
                User.registered_at >= week_ago_date
            ).count()
            stats['week_users'] = week_users

            # Month
            month_ago_date = get_tehran_time() - timedelta(days=30)
            month_users = session.query(User).filter(
                User.registered_at >= month_ago_date
            ).count()
            stats['month_users'] = month_users

        return stats

# ==================== Repository Pattern ====================

class BaseRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.model = None

    def get_by_id(self, id: int) -> Optional[BaseModel]:
        with self.db.get_session() as session:
            return session.query(self.model).filter_by(id=id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[BaseModel]:
        with self.db.get_session() as session:
            return session.query(self.model).offset(skip).limit(limit).all()

    def create(self, **kwargs) -> BaseModel:
        with self.db.get_session() as session:
            obj = self.model(**kwargs)
            session.add(obj)
            session.flush()
            return obj

    def update(self, id: int, **kwargs) -> Optional[BaseModel]:
        with self.db.get_session() as session:
            obj = session.query(self.model).filter_by(id=id).first()
            if obj:
                for key, value in kwargs.items():
                    if hasattr(obj, key):
                        setattr(obj, key, value)
                session.flush()
            return obj

    def delete(self, id: int) -> bool:
        with self.db.get_session() as session:
            obj = session.query(self.model).filter_by(id=id).first()
            if obj:
                session.delete(obj)
                session.flush()
                return True
            return False

    def count(self) -> int:
        with self.db.get_session() as session:
            return session.query(self.model).count()

# ==================== ریپازیتوری‌ها ====================

class UserRepository(BaseRepository):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__(db_manager)
        self.model = User

    def get_by_telegram_id(self, telegram_id: str) -> Optional[User]:
        with self.db.get_session() as session:
            return session.query(User).filter_by(telegram_id=telegram_id).first()

    def get_by_username(self, username: str) -> Optional[User]:
        with self.db.get_session() as session:
            return session.query(User).filter_by(username=username).first()

    def get_by_referral_code(self, referral_code: str) -> Optional[User]:
        with self.db.get_session() as session:
            return session.query(User).filter_by(referral_code=referral_code).first()

    def get_vip_users(self) -> List[User]:
        with self.db.get_session() as session:
            return session.query(User).filter_by(is_vip=True).filter(
                User.vip_expire > get_tehran_time()
            ).all()

    def get_active_users(self) -> List[User]:
        with self.db.get_session() as session:
            return session.query(User).filter_by(is_active=True, is_banned=False).all()

    def get_admins(self) -> List[User]:
        with self.db.get_session() as session:
            return session.query(User).filter_by(is_admin=True).all()

    def get_banned_users(self) -> List[User]:
        with self.db.get_session() as session:
            return session.query(User).filter_by(is_banned=True).all()

class SignalRepository(BaseRepository):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__(db_manager)
        self.model = Signal

    def get_active_by_coin(self, coin: str) -> List[Signal]:
        with self.db.get_session() as session:
            return session.query(Signal).filter_by(
                coin=coin,
                is_active=True
            ).order_by(desc(Signal.created_at)).limit(10).all()

    def get_vip_signals(self) -> List[Signal]:
        with self.db.get_session() as session:
            return session.query(Signal).filter_by(
                is_vip=True,
                is_active=True
            ).order_by(desc(Signal.created_at)).limit(10).all()

    def get_user_signals(self, user_id: str) -> List[Signal]:
        with self.db.get_session() as session:
            return session.query(Signal).filter_by(
                user_id=user_id
            ).order_by(desc(Signal.created_at)).all()

class PaymentRepository(BaseRepository):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__(db_manager)
        self.model = Payment

    def get_pending_payments(self) -> List[Payment]:
        with self.db.get_session() as session:
            return session.query(Payment).filter_by(status='pending').all()

    def get_user_payments(self, user_id: str) -> List[Payment]:
        with self.db.get_session() as session:
            return session.query(Payment).filter_by(user_id=user_id).all()

    def get_completed_payments(self) -> List[Payment]:
        with self.db.get_session() as session:
            return session.query(Payment).filter_by(status='completed').all()

# ==================== Export ====================

db_manager = DatabaseManager()
user_repo = UserRepository(db_manager)
signal_repo = SignalRepository(db_manager)
payment_repo = PaymentRepository(db_manager)

def get_db() -> DatabaseManager:
    return db_manager

def get_user_repo() -> UserRepository:
    return user_repo

def get_signal_repo() -> SignalRepository:
    return signal_repo

def get_payment_repo() -> PaymentRepository:
    return payment_repo
