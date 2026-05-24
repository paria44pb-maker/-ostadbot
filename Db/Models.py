from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Signal(Base):
    __tablename__ = 'signals'
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20))
    action = Column(String(10))
    confidence = Column(Float)
    strength = Column(Integer)
    created_at = Column(DateTime)

class Trade(Base):
    __tablename__ = 'trades'
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20))
    side = Column(String(10))
    amount = Column(Float)
    entry_price = Column(Float)
    exit_price = Column(Float)
    pnl = Column(Float)
    created_at = Column(DateTime)

class AIMessage(Base):
    __tablename__ = 'ai_messages'
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    content_hash = Column(String(64), unique=True)
    created_at = Column(DateTime)
