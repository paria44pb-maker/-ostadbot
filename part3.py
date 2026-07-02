#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🗄️  CryptoPulse AI Bot v3.0 - Database & Repository Layer ║
║   ────────────────────────────────────────────────────────   ║
║   💾 SQLite + SQLAlchemy  |  🔄 Repository Pattern           ║
║   👤 Users  |  💰 Payments  |  🚨 Signals  |  📊 Stats       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from contextlib import contextmanager
from sqlalchemy import (
    create_engine, Column, String, Integer, Float, Boolean,
    DateTime, Text, ForeignKey, Index, func, desc, asc
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import SQLAlchemyError

# ============================================================
#                    LOGGING
# ============================================================

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("Bot3-Database")

# ============================================================
#                    CONFIG
# ============================================================

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///bot.db")

# Fix Railway Postgres URL if needed
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

logger.info(f"📊 Database: {DATABASE_URL[:30]}...")

# ============================================================
#                    SQLAlchemy Setup
# ============================================================

if "postgresql" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=False
    )
else:
    # SQLite with thread-safe settings
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============================================================
#                    MODELS
# ============================================================

class User(Base):
    """👤 مدل کاربر"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(String(50), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    language = Column(String(10), default="fa")
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)

    # Wallet
    balance = Column(Float, default=0.0)
    total_deposited = Column(Float, default=0.0)
    total_withdrawn = Column(Float, default=0.0)
    total_profit = Column(Float, default=0.0)

    # Referral
    referral_code = Column(String(20), unique=True, nullable=True)
    referred_by = Column(String(50), nullable=True)
    referral_count = Column(Integer, default=0)
    referral_earnings = Column(Float, default=0.0)

    # Trading
    total_trades = Column(Integer, default=0)
    successful_trades = Column(Integer, default=0)
    failed_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)

    # VIP
    is_vip = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    vip_level = Column(Integer, default=0)
    vip_plan = Column(String(50), nullable=True)
    vip_expire = Column(DateTime, nullable=True)
    vip_activated_at = Column(DateTime, nullable=True)
    vip_trial_used = Column(Boolean, default=False)

    # Status
    is_admin = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    ban_reason = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    # Settings
    notifications_enabled = Column(Boolean, default=True)
    timeframe = Column(String(10), default="4h")
    ai_enabled = Column(Boolean, default=True)
    sound_alert = Column(Boolean, default=False)
    night_mode = Column(Boolean, default=False)

    # Timestamps
    registered_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    last_signal = Column(DateTime, nullable=True)

    # Relationships
    payments = relationship("Payment", back_populates="user", lazy="dynamic")
    signals = relationship("Signal", back_populates="user", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "telegram_id": self.telegram_id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "language": self.language,
            "phone": self.phone,
            "email": self.email,
            "balance": self.balance,
            "total_deposited": self.total_deposited,
            "total_withdrawn": self.total_withdrawn,
            "total_profit": self.total_profit,
            "referral_code": self.referral_code,
            "referred_by": self.referred_by,
            "referral_count": self.referral_count,
            "referral_earnings": self.referral_earnings,
            "total_trades": self.total_trades,
            "successful_trades": self.successful_trades,
            "failed_trades": self.failed_trades,
            "win_rate": self.win_rate,
            "is_vip": self.is_vip,
            "is_premium": self.is_premium,
            "vip_level": self.vip_level,
            "vip_plan": self.vip_plan,
            "vip_expire": self.vip_expire.isoformat() if self.vip_expire else None,
            "vip_activated_at": self.vip_activated_at.isoformat() if self.vip_activated_at else None,
            "vip_trial_used": self.vip_trial_used,
            "is_admin": self.is_admin,
            "is_banned": self.is_banned,
            "ban_reason": self.ban_reason,
            "is_active": self.is_active,
            "notifications_enabled": self.notifications_enabled,
            "timeframe": self.timeframe,
            "ai_enabled": self.ai_enabled,
            "sound_alert": self.sound_alert,
            "night_mode": self.night_mode,
            "registered_at": self.registered_at.isoformat() if self.registered_at else None,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "last_signal": self.last_signal.isoformat() if self.last_signal else None,
        }


class Payment(Base):
    """💰 مدل پرداخت"""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_id = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(String(50), ForeignKey("users.telegram_id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="IRT")
    payment_type = Column(String(50), nullable=False)  # vip_monthly, vip_yearly, vip_lifetime, deposit
    status = Column(String(20), default="pending")  # pending, completed, failed, rejected
    transaction_id = Column(String(100), nullable=True)
    receipt_file_id = Column(String(200), nullable=True)
    admin_id = Column(String(50), nullable=True)  # Who confirmed
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="payments")

    def to_dict(self):
        return {
            "id": self.id,
            "payment_id": self.payment_id,
            "user_id": self.user_id,
            "amount": self.amount,
            "currency": self.currency,
            "payment_type": self.payment_type,
            "status": self.status,
            "transaction_id": self.transaction_id,
            "receipt_file_id": self.receipt_file_id,
            "admin_id": self.admin_id,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "confirmed_at": self.confirmed_at.isoformat() if self.confirmed_at else None,
        }


class Signal(Base):
    """🚨 مدل سیگنال"""
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    signal_id = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(String(50), ForeignKey("users.telegram_id"), nullable=False, index=True)
    coin = Column(String(20), nullable=False)
    signal_type = Column(String(10), nullable=False)  # buy, sell, hold
    confidence = Column(Float, default=50.0)
    entry_price = Column(Float, nullable=True)
    current_price = Column(Float, nullable=True)
    exit_price = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    targets = Column(Text, nullable=True)  # JSON string
    timeframe = Column(String(10), default="4h")
    analysis = Column(Text, nullable=True)
    result = Column(String(20), nullable=True)  # win, loss, pending
    profit_loss = Column(Float, nullable=True)
    risk_reward = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="signals")

    def to_dict(self):
        return {
            "id": self.id,
            "signal_id": self.signal_id,
            "user_id": self.user_id,
            "coin": self.coin,
            "signal_type": self.signal_type,
            "confidence": self.confidence,
            "entry_price": self.entry_price,
            "current_price": self.current_price,
            "exit_price": self.exit_price,
            "stop_loss": self.stop_loss,
            "targets": self.targets,
            "timeframe": self.timeframe,
            "analysis": self.analysis,
            "result": self.result,
            "profit_loss": self.profit_loss,
            "risk_reward": self.risk_reward,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
        }


class Backup(Base):
    """💾 مدل بکاپ"""
    __tablename__ = "backups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    path = Column(String(200), nullable=True)
    size = Column(Integer, default=0)
    checksum = Column(String(100), nullable=True)
    type = Column(String(20), default="auto")  # auto, manual
    status = Column(String(20), default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "path": self.path,
            "size": self.size,
            "checksum": self.checksum,
            "type": self.type,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ============================================================
#                    Create Tables
# ============================================================

def init_db():
    """ایجاد جداول دیتابیس"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")

init_db()

# ============================================================
#                    REPOSITORIES
# ============================================================

class UserRepository:
    """👤 Repository کاربران"""

    def __init__(self):
        self.session = SessionLocal()

    def _new_session(self):
        if not self.session or not self.session.is_active:
            self.session = SessionLocal()
        return self.session

    def get_all(self) -> List[Dict]:
        """دریافت همه کاربران"""
        try:
            session = self._new_session()
            users = session.query(User).order_by(desc(User.registered_at)).all()
            return [u.to_dict() for u in users]
        except Exception as e:
            logger.error(f"get_all error: {e}")
            return []
        finally:
            session.close()

    def get_by_telegram_id(self, telegram_id: str) -> Optional[Dict]:
        """دریافت کاربر با آیدی تلگرام"""
        try:
            session = self._new_session()
            user = session.query(User).filter(User.telegram_id == str(telegram_id)).first()
            return user.to_dict() if user else None
        except Exception as e:
            logger.error(f"get_by_telegram_id error: {e}")
            return None
        finally:
            session.close()

    def get_by_id(self, user_id: int) -> Optional[Dict]:
        """دریافت کاربر با ID"""
        try:
            session = self._new_session()
            user = session.query(User).filter(User.id == user_id).first()
            return user.to_dict() if user else None
        except Exception as e:
            logger.error(f"get_by_id error: {e}")
            return None
        finally:
            session.close()

    def get_vip_users(self) -> List[Dict]:
        """دریافت کاربران VIP"""
        try:
            session = self._new_session()
            users = session.query(User).filter(User.is_vip == True).all()
            return [u.to_dict() for u in users]
        except Exception as e:
            logger.error(f"get_vip_users error: {e}")
            return []
        finally:
            session.close()

    def create(self, **kwargs) -> Optional[Dict]:
        """ایجاد کاربر جدید"""
        try:
            session = self._new_session()

            # Check if exists
            existing = session.query(User).filter(
                User.telegram_id == str(kwargs.get("telegram_id"))
            ).first()
            if existing:
                return existing.to_dict()

            # Generate referral code if not provided
            if "referral_code" not in kwargs:
                import random
                import string
                while True:
                    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                    if not session.query(User).filter(User.referral_code == code).first():
                        break
                kwargs["referral_code"] = code

            user = User(**kwargs)
            session.add(user)
            session.commit()
            session.refresh(user)
            logger.info(f"✅ User created: {kwargs.get('telegram_id')}")
            return user.to_dict()
        except Exception as e:
            session.rollback()
            logger.error(f"create error: {e}")
            return None
        finally:
            session.close()

    def update(self, telegram_id: str, **kwargs) -> Optional[Dict]:
        """آپدیت کاربر"""
        try:
            session = self._new_session()
            user = session.query(User).filter(User.telegram_id == str(telegram_id)).first()
            if not user:
                logger.warning(f"User not found for update: {telegram_id}")
                return None

            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)

            # Update last_active
            user.last_active = datetime.utcnow()

            session.commit()
            session.refresh(user)
            logger.info(f"✅ User updated: {telegram_id}")
            return user.to_dict()
        except Exception as e:
            session.rollback()
            logger.error(f"update error: {e}")
            return None
        finally:
            session.close()

    def ban_user(self, telegram_id: str, reason: str = None) -> bool:
        """بن کردن کاربر"""
        return self.update(telegram_id, is_banned=True, ban_reason=reason) is not None

    def unban_user(self, telegram_id: str) -> bool:
        """آنبن کردن کاربر"""
        return self.update(telegram_id, is_banned=False, ban_reason=None) is not None

    def make_admin(self, telegram_id: str) -> bool:
        """ادمین کردن کاربر"""
        return self.update(telegram_id, is_admin=True) is not None

    def delete(self, telegram_id: str) -> bool:
        """حذف کاربر"""
        try:
            session = self._new_session()
            user = session.query(User).filter(User.telegram_id == str(telegram_id)).first()
            if user:
                session.delete(user)
                session.commit()
                logger.info(f"🗑️ User deleted: {telegram_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"delete error: {e}")
            return False
        finally:
            session.close()

    def count(self) -> int:
        """تعداد کل کاربران"""
        try:
            session = self._new_session()
            return session.query(User).count()
        except Exception as e:
            logger.error(f"count error: {e}")
            return 0
        finally:
            session.close()

    def count_vip(self) -> int:
        """تعداد کاربران VIP"""
        try:
            session = self._new_session()
            return session.query(User).filter(User.is_vip == True).count()
        except Exception as e:
            logger.error(f"count_vip error: {e}")
            return 0
        finally:
            session.close()


class PaymentRepository:
    """💰 Repository پرداخت‌ها"""

    def __init__(self):
        self.session = SessionLocal()

    def _new_session(self):
        if not self.session or not self.session.is_active:
            self.session = SessionLocal()
        return self.session

    def get_all(self) -> List[Dict]:
        """دریافت همه پرداخت‌ها"""
        try:
            session = self._new_session()
            payments = session.query(Payment).order_by(desc(Payment.created_at)).all()
            return [p.to_dict() for p in payments]
        except Exception as e:
            logger.error(f"get_all error: {e}")
            return []
        finally:
            session.close()

    def get_pending_payments(self) -> List[Dict]:
        """دریافت پرداخت‌های در انتظار"""
        try:
            session = self._new_session()
            payments = session.query(Payment).filter(
                Payment.status == "pending"
            ).order_by(desc(Payment.created_at)).all()
            return [p.to_dict() for p in payments]
        except Exception as e:
            logger.error(f"get_pending_payments error: {e}")
            return []
        finally:
            session.close()

    def get_by_id(self, payment_id: str) -> Optional[Dict]:
        """دریافت پرداخت با شناسه"""
        try:
            session = self._new_session()
            payment = session.query(Payment).filter(Payment.payment_id == str(payment_id)).first()
            return payment.to_dict() if payment else None
        except Exception as e:
            logger.error(f"get_by_id error: {e}")
            return None
        finally:
            session.close()

    def get_user_payments(self, user_id: str) -> List[Dict]:
        """دریافت پرداخت‌های یک کاربر"""
        try:
            session = self._new_session()
            payments = session.query(Payment).filter(
                Payment.user_id == str(user_id)
            ).order_by(desc(Payment.created_at)).all()
            return [p.to_dict() for p in payments]
        except Exception as e:
            logger.error(f"get_user_payments error: {e}")
            return []
        finally:
            session.close()

    def create(self, **kwargs) -> Optional[Dict]:
        """ایجاد پرداخت جدید"""
        try:
            session = self._new_session()

            # Generate payment_id
            import random
            import string
            while True:
                pid = "PAY-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                if not session.query(Payment).filter(Payment.payment_id == pid).first():
                    break

            kwargs["payment_id"] = pid
            kwargs.setdefault("status", "pending")
            kwargs.setdefault("currency", "IRT")

            payment = Payment(**kwargs)
            session.add(payment)
            session.commit()
            session.refresh(payment)
            logger.info(f"✅ Payment created: {pid}")
            return payment.to_dict()
        except Exception as e:
            session.rollback()
            logger.error(f"create error: {e}")
            return None
        finally:
            session.close()

    def confirm_payment(self, payment_id: str, admin_id: str = None) -> bool:
        """تایید پرداخت"""
        try:
            session = self._new_session()
            payment = session.query(Payment).filter(Payment.payment_id == str(payment_id)).first()
            if payment:
                payment.status = "completed"
                payment.admin_id = admin_id
                payment.confirmed_at = datetime.utcnow()
                session.commit()
                logger.info(f"✅ Payment confirmed: {payment_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"confirm_payment error: {e}")
            return False
        finally:
            session.close()

    def reject_payment(self, payment_id: str, reason: str = None) -> bool:
        """رد پرداخت"""
        try:
            session = self._new_session()
            payment = session.query(Payment).filter(Payment.payment_id == str(payment_id)).first()
            if payment:
                payment.status = "rejected"
                payment.notes = reason
                session.commit()
                logger.info(f"❌ Payment rejected: {payment_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"reject_payment error: {e}")
            return False
        finally:
            session.close()

    def get_total_revenue(self) -> float:
        """درآمد کل"""
        try:
            session = self._new_session()
            result = session.query(func.sum(Payment.amount)).filter(
                Payment.status == "completed"
            ).scalar()
            return result or 0.0
        except Exception as e:
            logger.error(f"get_total_revenue error: {e}")
            return 0.0
        finally:
            session.close()


class SignalRepository:
    """🚨 Repository سیگنال‌ها"""

    def __init__(self):
        self.session = SessionLocal()

    def _new_session(self):
        if not self.session or not self.session.is_active:
            self.session = SessionLocal()
        return self.session

    def get_all(self) -> List[Dict]:
        """دریافت همه سیگنال‌ها"""
        try:
            session = self._new_session()
            signals = session.query(Signal).order_by(desc(Signal.created_at)).all()
            return [s.to_dict() for s in signals]
        except Exception as e:
            logger.error(f"get_all error: {e}")
            return []
        finally:
            session.close()

    def get_by_signal_id(self, signal_id: str) -> Optional[Dict]:
        """دریافت سیگنال با شناسه"""
        try:
            session = self._new_session()
            signal = session.query(Signal).filter(Signal.signal_id == str(signal_id)).first()
            return signal.to_dict() if signal else None
        except Exception as e:
            logger.error(f"get_by_signal_id error: {e}")
            return None
        finally:
            session.close()

    def create(self, **kwargs) -> Optional[Dict]:
        """ایجاد سیگنال جدید"""
        try:
            session = self._new_session()

            # Generate signal_id
            import random
            import string
            while True:
                sid = "SIG-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                if not session.query(Signal).filter(Signal.signal_id == sid).first():
                    break

            kwargs["signal_id"] = sid

            signal = Signal(**kwargs)
            session.add(signal)
            session.commit()
            session.refresh(signal)
            logger.info(f"✅ Signal created: {sid}")
            return signal.to_dict()
        except Exception as e:
            session.rollback()
            logger.error(f"create error: {e}")
            return None
        finally:
            session.close()

    def update_result(self, signal_id: str, result: str, exit_price: float = None) -> bool:
        """آپدیت نتیجه سیگنال"""
        try:
            session = self._new_session()
            signal = session.query(Signal).filter(Signal.signal_id == str(signal_id)).first()
            if signal:
                signal.result = result
                signal.closed_at = datetime.utcnow()
                if exit_price and signal.entry_price:
                    signal.exit_price = exit_price
                    if result == "win":
                        signal.profit_loss = exit_price - signal.entry_price
                    elif result == "loss":
                        signal.profit_loss = signal.entry_price - exit_price
                session.commit()
                logger.info(f"✅ Signal result updated: {signal_id} -> {result}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"update_result error: {e}")
            return False
        finally:
            session.close()

    def count(self) -> int:
        """تعداد کل سیگنال‌ها"""
        try:
            session = self._new_session()
            return session.query(Signal).count()
        except Exception as e:
            logger.error(f"count error: {e}")
            return 0
        finally:
            session.close()


# ============================================================
#                    DATABASE MANAGER
# ============================================================

class DatabaseManager:
    """🗄️ مدیریت کلی دیتابیس"""

    def __init__(self):
        self.user_repo = UserRepository()
        self.payment_repo = PaymentRepository()
        self.signal_repo = SignalRepository()

    def get_stats(self) -> Dict[str, Any]:
        """دریافت آمار کلی"""
        try:
            session = SessionLocal()
            total_users = session.query(User).count()
            vip_users = session.query(User).filter(User.is_vip == True).count()
            active_users = session.query(User).filter(User.is_active == True).count()
            banned_users = session.query(User).filter(User.is_banned == True).count()
            total_signals = session.query(Signal).count()
            total_revenue = session.query(func.sum(Payment.amount)).filter(
                Payment.status == "completed"
            ).scalar() or 0.0
            pending_payments = session.query(Payment).filter(
                Payment.status == "pending"
            ).count()
            completed_payments = session.query(Payment).filter(
                Payment.status == "completed"
            ).count()
            failed_payments = session.query(Payment).filter(
                Payment.status.in_(["failed", "rejected"])
            ).count()

            # Today
            today = datetime.utcnow().date()
            today_users = session.query(User).filter(
                func.date(User.registered_at) == today
            ).count()
            today_revenue = session.query(func.sum(Payment.amount)).filter(
                Payment.status == "completed",
                func.date(Payment.confirmed_at) == today
            ).scalar() or 0.0

            # This week
            week_ago = datetime.utcnow() - timedelta(days=7)
            week_users = session.query(User).filter(
                User.registered_at >= week_ago
            ).count()
            week_revenue = session.query(func.sum(Payment.amount)).filter(
                Payment.status == "completed",
                Payment.confirmed_at >= week_ago
            ).scalar() or 0.0

            # This month
            month_ago = datetime.utcnow() - timedelta(days=30)
            month_users = session.query(User).filter(
                User.registered_at >= month_ago
            ).count()
            month_revenue = session.query(func.sum(Payment.amount)).filter(
                Payment.status == "completed",
                Payment.confirmed_at >= month_ago
            ).scalar() or 0.0

            # VIP stats
            active_vip = session.query(User).filter(
                User.is_vip == True,
                User.vip_expire >= datetime.utcnow()
            ).count()
            pending_vip = session.query(Payment).filter(
                Payment.payment_type.like("%vip%"),
                Payment.status == "pending"
            ).count()
            vip_revenue = session.query(func.sum(Payment.amount)).filter(
                Payment.payment_type.like("%vip%"),
                Payment.status == "completed"
            ).scalar() or 0.0
            vip_monthly_revenue = session.query(func.sum(Payment.amount)).filter(
                Payment.payment_type.like("%vip%"),
                Payment.status == "completed",
                Payment.confirmed_at >= month_ago
            ).scalar() or 0.0
            trial_active = session.query(User).filter(
                User.vip_trial_used == True
            ).count()

            # Conversion rate
            conversion_rate = (vip_users / total_users * 100) if total_users > 0 else 0

            return {
                "users": total_users,
                "vip_users": vip_users,
                "active_users": active_users,
                "banned_users": banned_users,
                "signals": total_signals,
                "total_revenue": total_revenue,
                "pending_payments": pending_payments,
                "completed_payments": completed_payments,
                "failed_payments": failed_payments,
                "today_users": today_users,
                "today_revenue": today_revenue,
                "week_users": week_users,
                "week_revenue": week_revenue,
                "month_users": month_users,
                "month_revenue": month_revenue,
                "active_vip": active_vip,
                "pending_vip": pending_vip,
                "vip_revenue": vip_revenue,
                "vip_monthly_revenue": vip_monthly_revenue,
                "trial_active": trial_active,
                "vip_conversion_rate": round(conversion_rate, 1),
                "payments": completed_payments,
            }
        except Exception as e:
            logger.error(f"get_stats error: {e}")
            return {}
        finally:
            session.close()

    def backup(self) -> Dict:
        """ایجاد بکاپ از دیتابیس"""
        try:
            import shutil
            import os

            backup_dir = "backups"
            os.makedirs(backup_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}.db"
            backup_path = os.path.join(backup_dir, backup_name)

            # For SQLite
            if "sqlite" in DATABASE_URL:
                db_path = DATABASE_URL.replace("sqlite:///", "")
                if os.path.exists(db_path):
                    shutil.copy2(db_path, backup_path)
                    size = os.path.getsize(backup_path)

                    # Calculate checksum
                    with open(backup_path, "rb") as f:
                        checksum = hashlib.md5(f.read()).hexdigest()

                    # Save to database
                    session = SessionLocal()
                    backup_record = Backup(
                        name=backup_name,
                        path=backup_path,
                        size=size,
                        checksum=checksum,
                        type="manual"
                    )
                    session.add(backup_record)
                    session.commit()
                    session.close()

                    logger.info(f"✅ Backup created: {backup_name}")
                    return {
                        "success": True,
                        "name": backup_name,
                        "path": backup_path,
                        "size": size,
                        "checksum": checksum
                    }

            return {"success": False, "error": "Not SQLite"}
        except Exception as e:
            logger.error(f"backup error: {e}")
            return {"success": False, "error": str(e)}

    def get_backups_list(self) -> List[Dict]:
        """لیست بکاپ‌ها"""
        try:
            session = SessionLocal()
            backups = session.query(Backup).order_by(desc(Backup.created_at)).all()
            return [b.to_dict() for b in backups]
        except Exception as e:
            logger.error(f"get_backups_list error: {e}")
            return []
        finally:
            session.close()


# ============================================================
#                    SINGLETON INSTANCES
# ============================================================

_user_repo_instance = None
_payment_repo_instance = None
_signal_repo_instance = None
_db_manager_instance = None


def get_user_repo() -> UserRepository:
    global _user_repo_instance
    if _user_repo_instance is None:
        _user_repo_instance = UserRepository()
    return _user_repo_instance


def get_payment_repo() -> PaymentRepository:
    global _payment_repo_instance
    if _payment_repo_instance is None:
        _payment_repo_instance = PaymentRepository()
    return _payment_repo_instance


def get_signal_repo() -> SignalRepository:
    global _signal_repo_instance
    if _signal_repo_instance is None:
        _signal_repo_instance = SignalRepository()
    return _signal_repo_instance


def get_db_manager() -> DatabaseManager:
    global _db_manager_instance
    if _db_manager_instance is None:
        _db_manager_instance = DatabaseManager()
    return _db_manager_instance


# For backward compatibility with part9
db_manager = DatabaseManager()

# ============================================================
#                    EXPORT CHECK
# ============================================================

logger.info("✅ bot3.py loaded successfully")
logger.info(f"   📊 Users: {get_user_repo().count()}")
logger.info(f"   💰 Revenue: {get_payment_repo().get_total_revenue():,.0f} Toman")
logger.info(f"   🚨 Signals: {get_signal_repo().count()}")
