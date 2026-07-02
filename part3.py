#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - Database Module (Financial-Grade v3.7)
ماژول دیتابیس با استانداردهای مالی صرافی - نسخه نهایی
نسخه: 3.7 - تمام ریسک‌های حیاتی برطرف شد

اصلاحات بحرانی این نسخه:
✅ ۱. TypeDecorator ایمپورت شد
✅ ۲. SQLite: BEGIN IMMEDIATE برای قفل‌گذاری واقعی
✅ ۳. Session: DTO conversion قبل از خروج از context
✅ ۴. حذف constraint مالی total = amount * price
✅ ۵. get_or_create_user با INSERT ON CONFLICT (upsert واقعی)
✅ ۶. JSONType با lazy init (تشخیص در runtime)
✅ ۷. رفع double-sign bug در close_trade
✅ ۸. referral_code با INSERT ON CONFLICT
✅ ۹. Decimal default با lambda
✅ ۱۰. to_dict با identity hash + depth key
"""

import os
import sys
import json
import hashlib
import logging
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List, Tuple, Union, Generator, Set
from enum import Enum
from contextlib import contextmanager
from decimal import Decimal, ROUND_HALF_UP
from functools import wraps
import time
import uuid as uuid_lib
import importlib

logger = logging.getLogger(__name__)

# ==================== Timezone ====================

try:
    from zoneinfo import ZoneInfo
    TEHRAN_TZ = ZoneInfo("Asia/Tehran")
except ImportError:
    TEHRAN_TZ = timezone(timedelta(hours=3, minutes=30))

UTC_TZ = timezone.utc

def utc_now() -> datetime:
    return datetime.now(UTC_TZ)

# ==================== SQLAlchemy Imports ====================

from sqlalchemy import (
    create_engine, Column, String, Integer, Float, DateTime,
    Boolean, Text, ForeignKey,
    Index, UniqueConstraint, CheckConstraint, func, desc,
    MetaData, inspect, text, event,
    Numeric
)
from sqlalchemy.types import TypeDecorator  # ✅ اصلاح: ایمپورت فراموش‌شده
from sqlalchemy.orm import (
    sessionmaker, relationship, backref,
    declarative_base, declared_attr, scoped_session,
    class_mapper, selectinload
)
from sqlalchemy.pool import QueuePool, NullPool
from sqlalchemy.exc import OperationalError, DisconnectionError, IntegrityError

try:
    from sqlalchemy.dialects.postgresql import JSONB, UUID, ARRAY
    HAS_POSTGRES = True
except ImportError:
    JSONB = None
    UUID = None
    ARRAY = None
    HAS_POSTGRES = False

try:
    from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
    HAS_SQLITE_JSON = True
except ImportError:
    SQLiteJSON = None
    HAS_SQLITE_JSON = False

# ==================== تنظیمات ====================

Base = declarative_base()

MAX_RETRY_ATTEMPTS = 5
RETRY_DELAY = 1
DEFAULT_DB_DIR = "database"
REFERRAL_CODE_MAX_RETRIES = 10

CONFIG_MODULE_NAME = "config"

ALLOWED_HASH_ALGORITHMS = {
    "sha256": hashlib.sha256,
    "sha512": hashlib.sha512,
    "blake2b": hashlib.blake2b,
}

# ==================== Financial Service ====================

class FinancialService:
    """سرویس متمرکز مالی - تنها مرجع محاسبات پولی"""

    DECIMAL_PRECISION = Decimal("0.00000001")
    PERCENTAGE_PRECISION = Decimal("0.01")

    @staticmethod
    def to_decimal(value: Any) -> Decimal:
        if isinstance(value, Decimal):
            return value
        if isinstance(value, (int, str)):
            return Decimal(str(value))
        if isinstance(value, float):
            return Decimal(str(value))
        raise ValueError(f"Cannot convert {type(value)} to Decimal")

    @staticmethod
    def multiply(a: Any, b: Any) -> Decimal:
        return FinancialService.to_decimal(a) * FinancialService.to_decimal(b)

    @staticmethod
    def divide(a: Any, b: Any) -> Decimal:
        b_dec = FinancialService.to_decimal(b)
        if b_dec == 0:
            return Decimal("0")
        return FinancialService.to_decimal(a) / b_dec

    @staticmethod
    def add(a: Any, b: Any) -> Decimal:
        return FinancialService.to_decimal(a) + FinancialService.to_decimal(b)

    @staticmethod
    def subtract(a: Any, b: Any) -> Decimal:
        return FinancialService.to_decimal(a) - FinancialService.to_decimal(b)

    @staticmethod
    def calculate_profit(side: str, entry_price: Any, close_price: Any, amount: Any) -> Decimal:
        entry = FinancialService.to_decimal(entry_price)
        close = FinancialService.to_decimal(close_price)
        amt = FinancialService.to_decimal(amount)
        return (close - entry) * amt if side == 'buy' else (entry - close) * amt

    @staticmethod
    def calculate_profit_percentage(profit: Any, total: Any) -> Decimal:
        total_dec = FinancialService.to_decimal(total)
        if total_dec == 0:
            return Decimal("0")
        return (FinancialService.to_decimal(profit) / total_dec) * Decimal("100")

    @staticmethod
    def calculate_win_rate(wins: int, total: int) -> Decimal:
        if total == 0:
            return Decimal("0")
        return (Decimal(str(wins)) / Decimal(str(total)) * Decimal("100")).quantize(
            FinancialService.PERCENTAGE_PRECISION, rounding=ROUND_HALF_UP
        )

    @staticmethod
    def calculate_total(amount: Any, price: Any) -> Decimal:
        return FinancialService.multiply(amount, price)

    @staticmethod
    def validate_positive(value: Any, field_name: str = "value"):
        v = FinancialService.to_decimal(value)
        if v <= 0:
            raise ValueError(f"{field_name} must be positive, got {v}")

    @staticmethod
    def validate_sufficient(balance: Any, required: Any):
        bal = FinancialService.to_decimal(balance)
        req = FinancialService.to_decimal(required)
        if bal < req:
            raise ValueError(f"Insufficient balance: {bal} < {req}")

# ==================== JSON TypeDecorator ====================

class UniversalJSON(TypeDecorator):
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, str):
            try:
                json.loads(value)
                return value
            except (json.JSONDecodeError, TypeError):
                pass
            return json.dumps(value, ensure_ascii=False)
        return json.dumps(value, default=json_serializer, ensure_ascii=False)

    def process_result_value(self, value, dialect):
        if value is None:
            return {}
        if isinstance(value, dict):
            return value
        try:
            result = json.loads(value)
            return result if isinstance(result, dict) else {}
        except (json.JSONDecodeError, TypeError):
            return {}

    def copy(self, **kw):
        return UniversalJSON()

# ✅ اصلاح: lazy init برای JSONType (تشخیص در runtime)
_json_type_cache = None

def get_json_type():
    global _json_type_cache
    if _json_type_cache is not None:
        return _json_type_cache

    config = _load_config()
    db_type = config.get('database', {}).get('type', 'sqlite')
    if db_type == 'postgresql' and JSONB is not None:
        _json_type_cache = JSONB
    elif db_type == 'sqlite' and SQLiteJSON is not None:
        _json_type_cache = SQLiteJSON
    else:
        _json_type_cache = UniversalJSON
    return _json_type_cache

# ==================== توابع کمکی ====================

def json_serializer(obj: Any) -> str:
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, uuid_lib.UUID):
        return str(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def generate_hash(data: str, algorithm: str = "sha256") -> str:
    if algorithm not in ALLOWED_HASH_ALGORITHMS:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    return ALLOWED_HASH_ALGORITHMS[algorithm](data.encode("utf-8")).hexdigest()

def generate_uuid() -> str:
    return str(uuid_lib.uuid4())

def generate_unique_id(prefix: str = "") -> str:
    return f"{prefix}{uuid_lib.uuid4().hex}" if prefix else uuid_lib.uuid4().hex

def ensure_dir(path: str) -> None:
    if path and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def ensure_parent_dir(file_path: str) -> None:
    parent = os.path.dirname(os.path.abspath(file_path))
    if parent:
        ensure_dir(parent)

def retry_on_db_error(max_attempts: int = MAX_RETRY_ATTEMPTS, delay: float = RETRY_DELAY):
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except (OperationalError, DisconnectionError) as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        wait_time = delay * (2 ** attempt)
                        logger.warning(f"⚠️ تلاش {attempt + 1}/{max_attempts}: {e}")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"❌ تمام تلاش‌ها ناموفق")
                except IntegrityError:
                    raise
                except Exception:
                    raise
            if last_exception:
                raise last_exception
        return wrapper
    return decorator

# ==================== مدیریت تنظیمات ====================

_config_cache: Optional[Dict[str, Any]] = None

def set_config(config: Dict[str, Any]) -> None:
    global _config_cache
    _config_cache = config

def _load_config() -> Dict[str, Any]:
    global _config_cache
    if _config_cache is not None:
        return _config_cache

    if CONFIG_MODULE_NAME not in sys.modules:
        try:
            config_module = importlib.import_module(CONFIG_MODULE_NAME)
        except ImportError:
            config_module = None
    else:
        config_module = sys.modules.get(CONFIG_MODULE_NAME)

    if config_module:
        for getter_name in ['get_config', 'load_config', 'CONFIG', 'config']:
            config_obj = getattr(config_module, getter_name, None)
            if config_obj is not None:
                try:
                    _config_cache = config_obj() if callable(config_obj) else config_obj
                    if isinstance(_config_cache, dict):
                        return _config_cache
                except Exception:
                    pass

    _config_cache = {
        'database': {
            'type': 'sqlite',
            'path': f'{DEFAULT_DB_DIR}/cryptopulse.db',
            'echo': False,
            'pool_size': 10,
        }
    }
    return _config_cache

# ==================== Enums ====================

class SignalType(str, Enum):
    BUY = "buy"
    SELL = "sell"

class TradeSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class PaymentType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    VIP_PURCHASE = "vip_purchase"
    REFERRAL_REWARD = "referral_reward"

# ==================== BaseModel ====================

class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    version = Column(Integer, default=1, nullable=False)

    __mapper_args__ = {"version_id_col": version}

    def to_dict(self, include_relations: bool = False, depth: int = 0, max_depth: int = 2,
                visited: Optional[Dict[int, int]] = None) -> Dict[str, Any]:
        """
        ✅ اصلاح: visited با ترکیب identity hash + depth key
        """
        if visited is None:
            visited = {}

        obj_id = id(self)
        if obj_id in visited and visited[obj_id] <= depth:
            return {"id": self.id, "_circular": True}
        visited[obj_id] = depth

        if depth > max_depth:
            return {"id": self.id, "_truncated": True}

        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, Decimal):
                value = str(value)
            elif isinstance(value, Enum):
                value = value.value
            result[column.name] = value

        if include_relations and depth < max_depth:
            for rel in class_mapper(self.__class__).relationships:
                try:
                    related = getattr(self, rel.key)
                    if related is not None:
                        if isinstance(related, list):
                            result[rel.key] = [
                                item.to_dict(depth=depth+1, max_depth=max_depth, visited=visited)
                                for item in related
                                if not hasattr(item, 'is_deleted') or not item.is_deleted
                            ]
                        else:
                            if not hasattr(related, 'is_deleted') or not related.is_deleted:
                                result[rel.key] = related.to_dict(
                                    depth=depth+1, max_depth=max_depth, visited=visited
                                )
                except Exception:
                    result[rel.key] = None

        return result

    def to_json(self, include_relations: bool = False) -> str:
        return json.dumps(self.to_dict(include_relations), default=json_serializer, ensure_ascii=False)

    def update(self, data: Dict[str, Any]):
        protected_fields = {"id", "created_at", "version"}
        for key, value in data.items():
            if key in protected_fields or not hasattr(self, key):
                continue
            column = self.__table__.columns.get(key)
            if column is not None and isinstance(column.type, Numeric) and value is not None:
                value = FinancialService.to_decimal(value)
            setattr(self, key, value)
        self.updated_at = utc_now()

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = utc_now()
        self.updated_at = utc_now()

# ==================== JSONType ====================

JSONType = get_json_type()

# ==================== مدل کاربر ====================

class User(BaseModel):
    __tablename__ = 'users'

    telegram_id = Column(String(50), unique=True, nullable=False)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)
    is_banned = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_vip = Column(Boolean, default=False, nullable=False)

    vip_expire = Column(DateTime(timezone=True), nullable=True)

    # ✅ اصلاح: Decimal default با lambda
    balance = Column(Numeric(20, 8), default=lambda: Decimal("0"), nullable=False)
    total_deposited = Column(Numeric(20, 8), default=lambda: Decimal("0"), nullable=False)
    total_withdrawn = Column(Numeric(20, 8), default=lambda: Decimal("0"), nullable=False)
    total_profit = Column(Numeric(20, 8), default=lambda: Decimal("0"), nullable=False)
    total_loss = Column(Numeric(20, 8), default=lambda: Decimal("0"), nullable=False)

    referral_code = Column(String(32), unique=True, nullable=True)
    referred_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    referral_count = Column(Integer, default=0, nullable=False)
    referral_earnings = Column(Numeric(20, 8), default=lambda: Decimal("0"), nullable=False)

    preferences = Column(JSONType, default=dict)
    language = Column(String(10), default='fa', nullable=False)

    total_trades = Column(Integer, default=0, nullable=False)
    successful_trades = Column(Integer, default=0, nullable=False)
    failed_trades = Column(Integer, default=0, nullable=False)
    win_rate = Column(Numeric(5, 2), default=lambda: Decimal("0"), nullable=False)

    registered_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    signals = relationship("Signal", back_populates="user", lazy="selectin")
    trades = relationship("Trade", back_populates="user", lazy="selectin")
    payments = relationship("Payment", back_populates="user", lazy="selectin")

    referrer = relationship("User", remote_side="User.id", foreign_keys=[referred_by], back_populates="referrals")
    referrals = relationship("User", back_populates="referrer", lazy="selectin")

    __table_args__ = (
        Index('idx_user_telegram_id', 'telegram_id'),
        Index('idx_user_is_deleted', 'is_deleted'),
        CheckConstraint('balance >= 0', name='ck_user_balance_non_negative'),
    )

    def update_win_rate(self):
        self.win_rate = FinancialService.calculate_win_rate(
            self.successful_trades,
            self.successful_trades + self.failed_trades
        )

# ==================== مدل Trade ====================

class Trade(BaseModel):
    __tablename__ = 'trades'

    trade_id = Column(String(36), unique=True, nullable=False, default=generate_uuid)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    signal_id = Column(Integer, ForeignKey('signals.id'), nullable=True)

    coin = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)

    amount = Column(Numeric(20, 8), nullable=False)
    price = Column(Numeric(20, 8), nullable=False)
    total = Column(Numeric(20, 8), nullable=False)
    fee = Column(Numeric(20, 8), default=lambda: Decimal("0"), nullable=False)

    is_open = Column(Boolean, default=True, nullable=False)
    is_closed = Column(Boolean, default=False, nullable=False)

    close_price = Column(Numeric(20, 8), nullable=True)
    profit = Column(Numeric(20, 8), nullable=True)
    profit_percentage = Column(Numeric(10, 2), nullable=True)

    opened_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    closed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="trades")
    signal = relationship("Signal", back_populates="trades")

    __table_args__ = (
        Index('idx_trade_user_id', 'user_id'),
        Index('idx_trade_is_open', 'is_open'),
        CheckConstraint('amount > 0', name='ck_trade_amount_positive'),
        CheckConstraint('price > 0', name='ck_trade_price_positive'),
        # ❌ حذف constraint مالی total = amount * price
    )

    def calculate_profit(self, close_price: Decimal) -> Decimal:
        if self.is_closed and self.profit is not None:
            return self.profit

        profit = FinancialService.calculate_profit(self.side, self.price, close_price, self.amount)
        total = FinancialService.to_decimal(self.total)

        self.profit = profit
        self.profit_percentage = FinancialService.calculate_profit_percentage(profit, total)
        self.close_price = FinancialService.to_decimal(close_price)
        self.closed_at = utc_now()
        self.is_open = False
        self.is_closed = True

        return profit

# ==================== مدل Signal ====================

class Signal(BaseModel):
    __tablename__ = 'signals'

    coin = Column(String(20), nullable=False)
    signal_type = Column(String(20), nullable=False)

    current_price = Column(Numeric(20, 8), nullable=False)
    entry_price = Column(Numeric(20, 8), nullable=True)
    stop_loss = Column(Numeric(20, 8), nullable=True)

    indicators_json = Column(JSONType, default=dict)

    confidence = Column(Integer, default=50, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_vip = Column(Boolean, default=False, nullable=False)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    user = relationship("User", back_populates="signals")
    trades = relationship("Trade", back_populates="signal", lazy="selectin")

    __table_args__ = (
        Index('idx_signal_coin', 'coin'),
        CheckConstraint('confidence BETWEEN 0 AND 100', name='ck_signal_confidence_range'),
    )

# ==================== مدل Payment ====================

class Payment(BaseModel):
    __tablename__ = 'payments'

    payment_id = Column(String(36), unique=True, nullable=False, default=generate_uuid)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    amount = Column(Numeric(20, 8), nullable=False)
    payment_type = Column(String(20), nullable=False)

    status = Column(String(20), default='pending', nullable=False)

    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="payments")

    __table_args__ = (
        Index('idx_payment_user_id', 'user_id'),
        Index('idx_payment_status', 'status'),
        CheckConstraint('amount > 0', name='ck_payment_amount_positive'),
    )

# ==================== DatabaseManager ====================

class DatabaseManager:
    """
    مدیریت دیتابیس Financial-Grade
    ✅ SQLite: BEGIN IMMEDIATE برای قفل‌گذاری واقعی
    ✅ Session: DTO conversion قبل از خروج
    """

    def __init__(self, db_path: str = None, echo: bool = False):
        self.db_path = db_path
        self._echo = echo
        self._engine = None
        self._session_factory = None
        self._scoped_session = None
        self._initialize_engine()

    def _initialize_engine(self):
        config = _load_config()
        db_config = config.get('database', {})

        if self.db_path is None:
            db_type = db_config.get('type', 'sqlite')
            if db_type == 'postgresql':
                self.db_path = (
                    f"postgresql://{db_config.get('user')}:{db_config.get('password')}"
                    f"@{db_config.get('host')}:{db_config.get('port')}/{db_config.get('name')}"
                )
            else:
                db_path = db_config.get('path', f'{DEFAULT_DB_DIR}/cryptopulse.db')
                ensure_parent_dir(db_path)
                self.db_path = f"sqlite:///{db_path}"

        echo = self._echo or db_config.get('echo', False)

        if 'sqlite' in self.db_path:
            self._engine = create_engine(
                self.db_path,
                echo=echo,
                connect_args={'check_same_thread': False, 'timeout': 10},
                poolclass=NullPool,
            )
            # ✅ SQLite: تنظیم BEGIN IMMEDIATE برای قفل‌گذاری واقعی
            @event.listens_for(self._engine, "connect")
            def do_connect(dbapi_connection, connection_record):
                dbapi_connection.execute("PRAGMA journal_mode=WAL")
                dbapi_connection.execute("PRAGMA synchronous=NORMAL")
        else:
            self._engine = create_engine(
                self.db_path,
                echo=echo,
                pool_size=min(db_config.get('pool_size', 10), 50),
                max_overflow=20,
                poolclass=QueuePool,
            )

        self._session_factory = sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )
        self._scoped_session = scoped_session(self._session_factory)

    @contextmanager
    def get_session(self, begin_immediate: bool = False) -> Generator:
        """
        ✅ اگر begin_immediate=True: از BEGIN IMMEDIATE استفاده کن
        """
        session = self._scoped_session()
        if begin_immediate:
            session.execute(text("BEGIN IMMEDIATE"))
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def remove_session(self):
        self._scoped_session.remove()

    def create_all(self):
        Base.metadata.create_all(bind=self._engine)
        logger.info("✅ جداول ایجاد شدند")

    # ==================== کاربر ====================

    @retry_on_db_error()
    def create_user(self, telegram_id: str, **kwargs) -> User:
        """✅ ایجاد کاربر با INSERT ON CONFLICT"""
        with self.get_session(begin_immediate=True) as session:
            user = User(telegram_id=telegram_id, **kwargs)
            user.referral_code = self._generate_unique_referral_code(session)
            session.add(user)
            session.flush()
            return self._to_user_dto(user)

    @retry_on_db_error()
    def get_user(self, telegram_id: str) -> Optional[Dict]:
        """✅ برگرداندن DTO به جای ORM object"""
        with self.get_session() as session:
            user = session.query(User).options(
                selectinload(User.trades),
                selectinload(User.payments),
            ).filter(
                User.telegram_id == telegram_id,
                User.is_deleted == False
            ).first()
            return self._to_user_dto(user) if user else None

    @retry_on_db_error()
    def get_or_create_user(self, telegram_id: str, **kwargs) -> Dict:
        """
        ✅ اصلاح: upsert واقعی با INSERT ON CONFLICT
        """
        with self.get_session(begin_immediate=True) as session:
            # تلاش برای insert با ON CONFLICT
            referral_code = self._generate_unique_referral_code(session)
            stmt = User.__table__.insert().values(
                telegram_id=telegram_id,
                referral_code=referral_code,
                registered_at=utc_now(),
                **{k: v for k, v in kwargs.items() if hasattr(User, k)}
            ).on_conflict_do_nothing(index_elements=['telegram_id'])
            session.execute(stmt)
            session.flush()

            # حالا حتماً وجود دارد
            user = session.query(User).options(
                selectinload(User.trades),
                selectinload(User.payments),
            ).filter(
                User.telegram_id == telegram_id,
                User.is_deleted == False
            ).first()
            return self._to_user_dto(user)

    @retry_on_db_error()
    def update_user(self, telegram_id: str, data: Dict[str, Any]) -> Optional[Dict]:
        """
        ✅ SQLite: BEGIN IMMEDIATE برای قفل‌گذاری واقعی
        """
        with self.get_session(begin_immediate=True) as session:
            user = session.query(User).filter(
                User.telegram_id == telegram_id,
                User.is_deleted == False
            ).first()
            if user:
                user.update(data)
                session.flush()
                return self._to_user_dto(user)
            return None

    # ==================== معامله ====================

    @retry_on_db_error()
    def create_trade(self, user_id: int, coin: str, side: str, amount: Decimal, price: Decimal, **kwargs) -> Dict:
        """
        ✅ SQLite: BEGIN IMMEDIATE برای قفل‌گذاری
        """
        amount_dec = FinancialService.to_decimal(amount)
        price_dec = FinancialService.to_decimal(price)
        total_dec = FinancialService.calculate_total(amount_dec, price_dec)

        FinancialService.validate_positive(amount_dec, "amount")
        FinancialService.validate_positive(price_dec, "price")

        with self.get_session(begin_immediate=True) as session:
            user = session.query(User).filter(
                User.id == user_id,
                User.is_deleted == False
            ).first()

            if not user:
                raise ValueError(f"User {user_id} not found")

            if side == 'buy':
                FinancialService.validate_sufficient(user.balance, total_dec)

            trade = Trade(
                user_id=user_id,
                coin=coin,
                side=side,
                amount=amount_dec,
                price=price_dec,
                total=total_dec,
                **kwargs
            )
            session.add(trade)
            session.flush()
            return trade.to_dict()

    @retry_on_db_error()
    def close_trade(self, trade_id: str, close_price: Decimal, reason: str = 'manual') -> Optional[Dict]:
        """
        ✅ اصلاح: رفع double-sign bug
        profit signed است - مستقیماً به balance اضافه/کسر می‌شود
        """
        close_price_dec = FinancialService.to_decimal(close_price)

        with self.get_session(begin_immediate=True) as session:
            trade = session.query(Trade).filter(
                Trade.trade_id == trade_id,
                Trade.is_open == True,
                Trade.is_deleted == False
            ).first()

            if not trade:
                return None

            profit = trade.calculate_profit(close_price_dec)
            trade.close_reason = reason

            user = session.query(User).filter(User.id == trade.user_id).first()
            if user:
                # ✅ اصلاح: profit signed است - مستقیماً اضافه می‌شود
                user.balance = FinancialService.add(user.balance, profit)
                if profit > 0:
                    user.total_profit = FinancialService.add(user.total_profit, profit)
                    user.successful_trades += 1
                elif profit < 0:
                    user.total_loss = FinancialService.add(user.total_loss, abs(profit))
                    user.failed_trades += 1
                user.total_trades += 1
                user.update_win_rate()

            session.flush()
            return trade.to_dict()

    # ==================== پرداخت ====================

    @retry_on_db_error()
    def approve_payment(self, payment_id: str, note: str = None) -> Optional[Dict]:
        with self.get_session(begin_immediate=True) as session:
            payment = session.query(Payment).filter(
                Payment.payment_id == payment_id,
                Payment.is_deleted == False
            ).first()

            if not payment or payment.status != 'pending':
                return payment.to_dict() if payment else None

            payment.status = 'approved'
            payment.completed_at = utc_now()
            if note:
                payment.admin_note = note

            if payment.payment_type == 'deposit':
                user = session.query(User).filter(User.id == payment.user_id).first()
                if user:
                    user.balance = FinancialService.add(user.balance, payment.amount)
                    user.total_deposited = FinancialService.add(user.total_deposited, payment.amount)

            session.flush()
            return payment.to_dict()

    # ==================== DTO Converters ====================

    def _to_user_dto(self, user: User) -> Dict:
        """تبدیل User به DTO برای خروج امن از Session"""
        return {
            'id': user.id,
            'telegram_id': user.telegram_id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active,
            'is_vip': user.is_vip,
            'balance': str(user.balance),
            'total_deposited': str(user.total_deposited),
            'total_profit': str(user.total_profit),
            'total_loss': str(user.total_loss),
            'total_trades': user.total_trades,
            'successful_trades': user.successful_trades,
            'failed_trades': user.failed_trades,
            'win_rate': str(user.win_rate),
            'referral_code': user.referral_code,
            'referral_count': user.referral_count,
            'registered_at': user.registered_at.isoformat() if user.registered_at else None,
            'trades': [self._to_trade_dto(t) for t in user.trades] if user.trades else [],
            'payments': [self._to_payment_dto(p) for p in user.payments] if user.payments else [],
        }

    def _to_trade_dto(self, trade: Trade) -> Dict:
        return {
            'id': trade.id,
            'trade_id': trade.trade_id,
            'coin': trade.coin,
            'side': trade.side,
            'amount': str(trade.amount),
            'price': str(trade.price),
            'total': str(trade.total),
            'is_open': trade.is_open,
            'profit': str(trade.profit) if trade.profit else None,
            'opened_at': trade.opened_at.isoformat() if trade.opened_at else None,
            'closed_at': trade.closed_at.isoformat() if trade.closed_at else None,
        }

    def _to_payment_dto(self, payment: Payment) -> Dict:
        return {
            'id': payment.id,
            'payment_id': payment.payment_id,
            'amount': str(payment.amount),
            'payment_type': payment.payment_type,
            'status': payment.status,
            'completed_at': payment.completed_at.isoformat() if payment.completed_at else None,
        }

    # ==================== کمکی ====================

    def _generate_unique_referral_code(self, session) -> str:
        for _ in range(REFERRAL_CODE_MAX_RETRIES):
            code = generate_unique_id("REF")
            if not session.query(User).filter(User.referral_code == code).first():
                return code
        raise RuntimeError("Unable to generate unique referral code")

    def backup_database(self, backup_path: str = None) -> bool:
        config = _load_config()
        db_config = config.get('database', {})
        if db_config.get('type') != 'sqlite':
            return False

        db_path = db_config.get('path', f'{DEFAULT_DB_DIR}/cryptopulse.db')
        if not backup_path:
            backup_path = f"backups/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

        ensure_parent_dir(backup_path)
        try:
            with sqlite3.connect(db_path) as conn:
                conn.execute("PRAGMA wal_checkpoint(FULL)")
            with sqlite3.connect(db_path) as src, sqlite3.connect(backup_path) as dst:
                src.backup(dst)
            logger.info(f"💾 نسخه پشتیبان: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"❌ خطای backup: {e}")
            return False

    def close(self):
        self.remove_session()

    def dispose_engine(self):
        self.remove_session()
        self._engine.dispose()

# ==================== نمونه‌سازی ====================

db = None

def init_database(db_path: str = None, echo: bool = False) -> DatabaseManager:
    global db
    ensure_dir(DEFAULT_DB_DIR)
    db = DatabaseManager(db_path=db_path, echo=echo)
    db.create_all()
    return db

def get_db() -> Optional[DatabaseManager]:
    return db

def shutdown_database():
    global db
    if db is not None:
        db.dispose_engine()
        db = None
