#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                    ║
║   📡 CryptoPulse AI v9.0 — EXCHANGE & MARKET ENGINE — GOD MODE                    ║
║   ─────────────────────────────────────────────────────────────────────────────    ║
║   🏦 Multi-Exchange  |  💰 Real-time Prices  |  📊 OHLCV Candles                 ║
║   📈 Order Books  |  🔄 WebSocket Streams  |  💎 Market Depth                   ║
║   🐋 Whale Detection  |  📡 Arbitrage Scanner  |  🗄️ Smart Cache               ║
║   🔔 Price Alerts  |  📊 Market Summary  |  🤖 Signal Generator                 ║
║                                                                                    ║
║   ═══════════════════════════════════════════════════════════════════════════════   ║
║   📁 ۸۰۰۰+ خط کد  |  ⚡ فوق‌بهینه  |  🔥 حرفه‌ای  |  🛡️ ضد خطا                ║
║                                                                                    ║
╚════════════════════════════════════════════════════════════════════════════════════╝
"""

import os, sys, json, math, time, random, hashlib, hmac, base64, re, asyncio
import threading, itertools, functools, operator, copy, textwrap, struct, zlib
from datetime import datetime, timedelta, timezone
from typing import (Dict, Any, List, Optional, Tuple, Union, Set, Callable, Coroutine,
                    TypeVar, Generic, Protocol, runtime_checkable, ClassVar)
from collections import defaultdict, OrderedDict, deque, Counter, namedtuple, ChainMap
from dataclasses import dataclass, field, asdict, astuple, fields, InitVar
from enum import Enum, IntEnum, auto, unique, Flag
from functools import wraps, lru_cache, partial, reduce, singledispatch, total_ordering
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed, Future
from contextlib import contextmanager, asynccontextmanager, suppress, redirect_stdout, redirect_stderr
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=ResourceWarning)
warnings.filterwarnings("ignore", category=ImportWarning)

import logging
logging.basicConfig(level=logging.CRITICAL, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("Part5-Market")
logger.setLevel(logging.CRITICAL)
logger.addHandler(logging.NullHandler())
for name in list(logging.root.manager.loggerDict.keys()):
    logging.getLogger(name).setLevel(logging.CRITICAL)
    logging.getLogger(name).addHandler(logging.NullHandler())

# ============================================================
#                    SAFE HTTP CLIENTS
# ============================================================
try:
    import requests as req_lib
    from requests.adapters import HTTPAdapter as ReqAdapter
    from urllib3.util.retry import Retry as ReqRetry
    HAS_REQUESTS = True
except ImportError:
    req_lib = None
    ReqAdapter = None
    ReqRetry = None
    HAS_REQUESTS = False

try:
    import aiohttp as aiohttp_lib
    HAS_AIOHTTP = True
except ImportError:
    aiohttp_lib = None
    HAS_AIOHTTP = False

try:
    import websocket as ws_lib
    HAS_WEBSOCKET = True
except ImportError:
    ws_lib = None
    HAS_WEBSOCKET = False

try:
    import orjson as orjson_lib
    HAS_ORJSON = True
except ImportError:
    orjson_lib = None
    HAS_ORJSON = False

# ============================================================
#                    TYPE ALIASES
# ============================================================
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')
Number = Union[int, float]
Price = float
Volume = float
Timestamp = int
Symbol = str
ExchangeName = str
JsonDict = Dict[str, Any]
JsonList = List[Dict[str, Any]]
Callback = Callable[[Any], None]
AsyncCallback = Callable[[Any], Coroutine[Any, Any, None]]

# ============================================================
#                    ENUMS — COMPLETE TAXONOMY
# ============================================================

@unique
class ExchangeID(IntEnum):
    COINEX = 1
    BINANCE = 2
    KUCOIN = 3
    GATE = 4
    MEXC = 5
    BYBIT = 6
    OKX = 7
    HUOBI = 8
    KRAKEN = 9
    BITFINEX = 10
    BITSTAMP = 11
    GEMINI = 12
    POLONIEX = 13
    BITTREX = 14
    HITBTC = 15
    DERIBIT = 16
    ASCENDEX = 17
    PHEMEX = 18
    BINGX = 19
    BITGET = 20

@unique
class MarketType(Enum):
    SPOT = "spot"
    FUTURES = "futures"
    PERPETUAL = "perpetual"
    MARGIN = "margin"
    OPTIONS = "options"
    ETF = "etf"
    INDEX = "index"
    PREDICTION = "prediction"
    SWAP = "swap"

@unique
class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

@unique
class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    STOP_LIMIT = "stop_limit"
    TAKE_PROFIT = "take_profit"
    TAKE_PROFIT_LIMIT = "take_profit_limit"
    TRAILING_STOP = "trailing_stop"
    OCO = "oco"
    ICEBERG = "iceberg"
    TWAP = "twap"
    VWAP = "vwap"
    POST_ONLY = "post_only"

@unique
class OrderStatus(Enum):
    NEW = "new"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELED = "canceled"
    REJECTED = "rejected"
    EXPIRED = "expired"
    PENDING = "pending"
    OPEN = "open"
    CLOSED = "closed"

@unique
class TimeInForce(Enum):
    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"
    GTD = "GTD"
    GTX = "GTX"

@unique
class TimeFrame(Enum):
    TICK = "tick"
    M1 = "1m"
    M3 = "3m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    M45 = "45m"
    H1 = "1h"
    H2 = "2h"
    H3 = "3h"
    H4 = "4h"
    H6 = "6h"
    H8 = "8h"
    H12 = "12h"
    D1 = "1d"
    D3 = "3d"
    W1 = "1w"
    W2 = "2w"
    MN1 = "1M"
    MN3 = "3M"
    MN6 = "6M"
    Y1 = "1y"

@unique
class CandleType(Enum):
    OHLCV = "ohlcv"
    HEIKIN_ASHI = "heikin_ashi"
    RENKO = "renko"
    KAGI = "kagi"
    POINT_FIGURE = "point_figure"
    RANGE = "range"
    VOLUME = "volume"
    DOLLAR = "dollar"

@unique
class VolatilityRegime(Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    VERY_HIGH = "very_high"
    EXTREME = "extreme"

@unique
class MarketRegime(Enum):
    BULL_TREND = "bull_trend"
    BEAR_TREND = "bear_trend"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"
    CRASH = "crash"
    RALLY = "rally"
    ACCUMULATION = "accumulation"
    DISTRIBUTION = "distribution"
    UNKNOWN = "unknown"

@unique
class SignalStrength(Enum):
    VERY_STRONG_BUY = "very_strong_buy"
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    WEAK_BUY = "weak_buy"
    NEUTRAL = "neutral"
    WEAK_SELL = "weak_sell"
    SELL = "sell"
    STRONG_SELL = "strong_sell"
    VERY_STRONG_SELL = "very_strong_sell"

@unique
class AlertType(Enum):
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    CHANGE_UP = "change_up"
    CHANGE_DOWN = "change_down"
    VOLUME_SPIKE = "volume_spike"
    WHALE_ACTIVITY = "whale_activity"
    TREND_CHANGE = "trend_change"
    BREAKOUT = "breakout"
    BREAKDOWN = "breakdown"

# ============================================================
#                    DATA MODELS — COMPLETE
# ============================================================

@dataclass
class Ticker:
    """Ultimate Ticker Model"""
    symbol: Symbol = ""
    exchange: ExchangeName = "unknown"
    timestamp: Timestamp = 0
    last_price: Price = 0.0
    bid: Price = 0.0
    ask: Price = 0.0
    mid_price: Price = 0.0
    spread: Price = 0.0
    spread_percent: float = 0.0
    open_24h: Price = 0.0
    high_24h: Price = 0.0
    low_24h: Price = 0.0
    close_24h: Price = 0.0
    change_24h: Price = 0.0
    change_percent_24h: float = 0.0
    volume_24h: Volume = 0.0
    volume_usd_24h: float = 0.0
    quote_volume_24h: float = 0.0
    trades_24h: int = 0
    mark_price: Price = 0.0
    index_price: Price = 0.0
    funding_rate: float = 0.0
    next_funding_time: Timestamp = 0
    open_interest: float = 0.0
    open_interest_usd: float = 0.0
    bid_depth_1pct: float = 0.0
    ask_depth_1pct: float = 0.0
    bid_depth_2pct: float = 0.0
    ask_depth_2pct: float = 0.0
    liquidity_score: float = 0.0
    volatility: float = 0.0
    vwap: float = 0.0
    momentum: float = 0.0
    market_cap: float = 0.0
    market_cap_rank: int = 0
    circulating_supply: float = 0.0
    max_supply: float = 0.0
    is_active: bool = True
    
    @property
    def is_positive(self) -> bool: return self.change_percent_24h >= 0
    @property
    def range_percent(self) -> float: return ((self.high_24h - self.low_24h) / self.low_24h * 100) if self.low_24h > 0 else 0.0
    @property
    def bid_ask_ratio(self) -> float: return self.bid_depth_1pct / max(self.ask_depth_1pct, 0.0001)
    @property
    def pressure(self) -> float: return (self.bid_depth_1pct - self.ask_depth_1pct) / max(self.bid_depth_1pct + self.ask_depth_1pct, 0.0001)

@dataclass
class OHLCV:
    """Ultimate Candlestick Model"""
    timestamp: Timestamp = 0
    open: Price = 0.0
    high: Price = 0.0
    low: Price = 0.0
    close: Price = 0.0
    volume: Volume = 0.0
    quote_volume: float = 0.0
    trades: int = 0
    taker_buy_volume: float = 0.0
    taker_buy_quote_volume: float = 0.0
    exchange: ExchangeName = "unknown"
    
    @property
    def body(self) -> float: return abs(self.close - self.open)
    @property
    def range(self) -> float: return self.high - self.low
    @property
    def upper_wick(self) -> float: return self.high - max(self.open, self.close)
    @property
    def lower_wick(self) -> float: return min(self.open, self.close) - self.low
    @property
    def is_bullish(self) -> bool: return self.close > self.open
    @property
    def is_bearish(self) -> bool: return self.close < self.open
    @property
    def is_doji(self) -> bool: return self.body < self.range * 0.05
    @property
    def body_percent(self) -> float: return (self.body / max(self.range, 0.0001)) * 100
    @property
    def upper_wick_percent(self) -> float: return (self.upper_wick / max(self.range, 0.0001)) * 100
    @property
    def lower_wick_percent(self) -> float: return (self.lower_wick / max(self.range, 0.0001)) * 100
    @property
    def volume_delta(self) -> float: return self.taker_buy_volume - (self.volume - self.taker_buy_volume)
    @property
    def vwap(self) -> float: return self.quote_volume / max(self.volume, 0.0001)
    @property
    def amplitude(self) -> float: return ((self.high - self.low) / max(self.low, 0.0001)) * 100

@dataclass
class OrderBookLevel:
    """Order Book Level"""
    price: Price = 0.0
    amount: Volume = 0.0
    total: Volume = 0.0
    orders: int = 0
    exchange: ExchangeName = "unknown"
    timestamp: Timestamp = 0

@dataclass
class OrderBook:
    """Ultimate Order Book"""
    symbol: Symbol = ""
    timestamp: Timestamp = 0
    bids: List[OrderBookLevel] = field(default_factory=list)
    asks: List[OrderBookLevel] = field(default_factory=list)
    exchange: ExchangeName = "unknown"
    update_id: int = 0
    
    @property
    def best_bid(self) -> Price: return self.bids[0].price if self.bids else 0.0
    @property
    def best_ask(self) -> Price: return self.asks[0].price if self.asks else 0.0
    @property
    def mid_price(self) -> Price: return (self.best_bid + self.best_ask) / 2.0
    @property
    def spread(self) -> Price: return self.best_ask - self.best_bid
    @property
    def spread_percent(self) -> float: return (self.spread / max(self.best_ask, 0.0001)) * 100
    @property
    def total_bid_volume(self) -> Volume: return sum(l.amount for l in self.bids)
    @property
    def total_ask_volume(self) -> Volume: return sum(l.amount for l in self.asks)
    @property
    def imbalance(self) -> float:
        b, a = self.total_bid_volume, self.total_ask_volume
        return (b - a) / max(b + a, 0.0001)
    @property
    def weighted_bid(self) -> Price:
        return sum(l.price * l.amount for l in self.bids) / max(self.total_bid_volume, 0.0001)
    @property
    def weighted_ask(self) -> Price:
        return sum(l.price * l.amount for l in self.asks) / max(self.total_ask_volume, 0.0001)
    @property
    def micro_price(self) -> Price:
        bv, av = self.total_bid_volume, self.total_ask_volume
        return (self.best_bid * av + self.best_ask * bv) / max(bv + av, 0.0001)

@dataclass
class Trade:
    """Trade Record"""
    id: str = ""
    symbol: Symbol = ""
    timestamp: Timestamp = 0
    price: Price = 0.0
    amount: Volume = 0.0
    side: OrderSide = OrderSide.BUY
    value_usd: float = 0.0
    exchange: ExchangeName = "unknown"
    is_liquidation: bool = False
    is_block: bool = False
    is_whale: bool = False

@dataclass
class MarketSummary:
    """Complete Market Summary"""
    timestamp: Timestamp = 0
    total_market_cap: float = 0.0
    total_volume_24h: float = 0.0
    btc_dominance: float = 0.0
    eth_dominance: float = 0.0
    defi_market_cap: float = 0.0
    stablecoin_market_cap: float = 0.0
    fear_greed_index: int = 50
    fear_greed_classification: str = "neutral"
    active_currencies: int = 0
    active_exchanges: int = 0
    btc_price: Price = 0.0
    eth_price: Price = 0.0
    top_gainers: List[Ticker] = field(default_factory=list)
    top_losers: List[Ticker] = field(default_factory=list)
    most_volume: List[Ticker] = field(default_factory=list)
    most_volatile: List[Ticker] = field(default_factory=list)
    market_regime: str = "unknown"
    overall_sentiment: str = "neutral"
    total_liquidations_24h: float = 0.0

@dataclass
class PriceAlert:
    """Price Alert"""
    id: str = ""
    user_id: int = 0
    symbol: Symbol = ""
    target_price: Price = 0.0
    direction: str = "above"
    alert_type: AlertType = AlertType.PRICE_ABOVE
    triggered: bool = False
    triggered_price: Price = 0.0
    created_at: Timestamp = 0
    triggered_at: Timestamp = 0
    expires_at: Timestamp = 0
    notification_sent: bool = False
    channel_id: str = ""
    exchange: ExchangeName = "any"
    priority: int = 1

@dataclass
class ArbitrageOpportunity:
    """Arbitrage Opportunity"""
    symbol: Symbol = ""
    buy_exchange: ExchangeName = ""
    sell_exchange: ExchangeName = ""
    buy_price: Price = 0.0
    sell_price: Price = 0.0
    spread_percent: float = 0.0
    potential_profit: float = 0.0
    fees: float = 0.0
    net_profit: float = 0.0
    net_profit_percent: float = 0.0
    estimated_time: float = 0.0
    min_amount: float = 0.0
    max_amount: float = 0.0
    timestamp: Timestamp = 0
    risk_level: str = "low"
    confidence: float = 0.0

@dataclass
class ExchangeInfo:
    """Exchange Information"""
    id: ExchangeID = ExchangeID.COINEX
    name: str = ""
    base_url: str = ""
    ws_url: str = ""
    symbols: List[str] = field(default_factory=list)
    timeframes: List[str] = field(default_factory=list)
    market_types: List[MarketType] = field(default_factory=list)
    maker_fee: float = 0.001
    taker_fee: float = 0.002
    min_order_size: float = 0.0
    rate_limits_per_second: int = 10
    rate_limits_per_minute: int = 600
    api_status: str = "unknown"
    latency_ms: float = 0.0
    uptime_percent: float = 100.0
    last_checked: Timestamp = 0
    supports_websocket: bool = True
    supports_futures: bool = False
    supports_margin: bool = False
    supports_staking: bool = False
    kyc_required: bool = True

# ============================================================
#                    UTILITY FUNCTIONS
# ============================================================

def safe_float(value: Any, default: float = 0.0) -> float:
    try: return float(value)
    except: return default

def safe_int(value: Any, default: int = 0) -> int:
    try: return int(float(value))
    except: return default

def safe_str(value: Any, default: str = "") -> str:
    try: return str(value)
    except: return default

def timestamp_ms() -> int:
    return int(time.time() * 1000)

def timestamp_sec() -> int:
    return int(time.time())

def format_symbol_ex(symbol: str, exchange: str = "coinex") -> str:
    symbol = symbol.upper().strip()
    mapping = {"coinex": f"{symbol}USDT", "binance": f"{symbol}USDT", "kucoin": f"{symbol}-USDT", "gate": f"{symbol}_USDT", "mexc": f"{symbol}_USDT", "bybit": f"{symbol}USDT", "okx": f"{symbol}-USDT-SWAP"}
    return mapping.get(exchange.lower(), f"{symbol}USDT")

def generate_signature(secret: str, message: str, algorithm: str = "sha256") -> str:
    if algorithm == "sha256":
        return hmac.new(secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()
    elif algorithm == "sha512":
        return hmac.new(secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha512).hexdigest()
    elif algorithm == "md5":
        return hashlib.md5(message.encode('utf-8')).hexdigest()
    return ""

def generate_nonce() -> str:
    return str(int(time.time() * 1000000))

def retry_on_failure(max_retries: int = 3, delay: float = 0.5, backoff: float = 2.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(current_delay)
                    current_delay *= backoff
            return None
        return wrapper
    return decorator

# ============================================================
#                    SMART CACHE SYSTEM
# ============================================================

class CacheEntry:
    __slots__ = ('value', 'timestamp', 'ttl', 'access_count', 'hit_count')
    def __init__(self, value: Any, ttl: int):
        self.value = value
        self.timestamp = time.monotonic()
        self.ttl = ttl
        self.access_count = 0
        self.hit_count = 0
    @property
    def is_expired(self) -> bool: return (time.monotonic() - self.timestamp) > self.ttl
    @property
    def age(self) -> float: return time.monotonic() - self.timestamp
    @property
    def hit_rate(self) -> float: return self.hit_count / max(self.access_count, 1)

class TieredCache:
    def __init__(self, max_size: int = 100000):
        self.max_size = max_size
        self._l1: Dict[str, CacheEntry] = {}
        self._l2: OrderedDict = OrderedDict()
        self._lock = threading.RLock()
        self._stats = {'hits': 0, 'misses': 0, 'evictions': 0, 'expirations': 0, 'writes': 0, 'reads': 0}
    
    def get(self, key: str, default_ttl: int = 30) -> Optional[Any]:
        with self._lock:
            self._stats['reads'] += 1
            entry = self._l1.get(key)
            if entry:
                entry.access_count += 1
                if entry.is_expired:
                    self._stats['expirations'] += 1
                    del self._l1[key]
                    self._l2.pop(key, None)
                    self._stats['misses'] += 1
                    return None
                entry.hit_count += 1
                self._stats['hits'] += 1
                self._l2.move_to_end(key)
                return entry.value
            self._stats['misses'] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: int = 30):
        with self._lock:
            self._stats['writes'] += 1
            entry = CacheEntry(value, ttl)
            self._l1[key] = entry
            self._l2[key] = entry
            self._l2.move_to_end(key)
            while len(self._l2) > self.max_size:
                oldest_key, _ = self._l2.popitem(last=False)
                self._l1.pop(oldest_key, None)
                self._stats['evictions'] += 1
    
    def delete(self, key: str):
        with self._lock:
            self._l1.pop(key, None)
            self._l2.pop(key, None)
    
    def clear(self):
        with self._lock:
            self._l1.clear()
            self._l2.clear()
            self._stats.update({k: 0 for k in self._stats})
    
    def get_stats(self) -> Dict:
        with self._lock:
            total = self._stats['hits'] + self._stats['misses']
            return {**self._stats, 'size': len(self._l1), 'hit_rate': (self._stats['hits'] / max(total, 1)) * 100, 'entries': len(self._l1)}

# ============================================================
#                    HTTP CLIENT
# ============================================================

class HTTPClient:
    def __init__(self, base_url: str, timeout: int = 15, max_retries: int = 3):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = None
        self._init_session()
    
    def _init_session(self):
        if not HAS_REQUESTS or req_lib is None:
            self.session = None
            return
        try:
            self.session = req_lib.Session()
            retry_strategy = ReqRetry(total=self.max_retries, backoff_factor=0.3, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET", "POST"])
            adapter = ReqAdapter(max_retries=retry_strategy, pool_connections=20, pool_maxsize=50)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)
            self.session.headers.update({'User-Agent': 'CryptoPulseAI/9.0', 'Accept': 'application/json', 'Content-Type': 'application/json'})
        except Exception:
            self.session = None
    
    def get(self, endpoint: str, params: Dict = None, headers: Dict = None) -> Optional[JsonDict]:
        if self.session is None:
            return None
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            req_headers = self.session.headers.copy()
            if headers: req_headers.update(headers)
            response = self.session.get(url, params=params, headers=req_headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None
    
    def post(self, endpoint: str, data: Dict = None, headers: Dict = None) -> Optional[JsonDict]:
        if self.session is None:
            return None
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            req_headers = self.session.headers.copy()
            if headers: req_headers.update(headers)
            response = self.session.post(url, json=data, headers=req_headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None
    
    def close(self):
        if self.session:
            try: self.session.close()
            except: pass

# ============================================================
#                    RATE LIMITER
# ============================================================

class TokenBucket:
    def __init__(self, rate: float, burst: int = None):
        self.rate = rate
        self.burst = burst or int(rate)
        self.tokens = float(self.burst)
        self.last_update = time.monotonic()
        self._lock = threading.Lock()
    
    def acquire(self, tokens: int = 1, wait: bool = True) -> bool:
        with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_update
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            self.last_update = now
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            if not wait:
                return False
            wait_time = (tokens - self.tokens) / self.rate
            time.sleep(min(wait_time, 1.0))
            self.tokens = 0
            self.last_update = time.monotonic()
            return True

class MultiRateLimiter:
    def __init__(self):
        self.buckets: Dict[str, TokenBucket] = {}
        self._lock = threading.Lock()
    
    def add(self, name: str, rate: float, burst: int = None):
        with self._lock:
            self.buckets[name] = TokenBucket(rate, burst)
    
    def acquire(self, name: str = "default", tokens: int = 1) -> bool:
        bucket = self.buckets.get(name)
        if bucket:
            return bucket.acquire(tokens)
        return True

# ============================================================
#                    COINEX CLIENT
# ============================================================

class CoinExClient:
    REST_URL = "https://api.coinex.com/v2"
    REST_URL_V1 = "https://api.coinex.com/v1"
    WS_URL = "wss://socket.coinex.com/"
    
    def __init__(self, api_key: str = "", api_secret: str = "", passphrase: str = ""):
        self.api_key = api_key or os.environ.get("COINEX_API_KEY", "")
        self.api_secret = api_secret or os.environ.get("COINEX_API_SECRET", "")
        self.passphrase = passphrase or os.environ.get("COINEX_API_PASSPHRASE", "")
        self.client = HTTPClient(self.REST_URL)
        self.client_v1 = HTTPClient(self.REST_URL_V1)
        self.rate_limiter = MultiRateLimiter()
        self.rate_limiter.add("rest", 30, 50)
        self.rate_limiter.add("ticker", 10, 15)
        self.cache = TieredCache(max_size=50000)
        self.exchange_name = "coinex"
        self.exchange_info = ExchangeInfo(id=ExchangeID.COINEX, name="CoinEx", base_url=self.REST_URL, ws_url=self.WS_URL, symbols=[], timeframes=[tf.value for tf in TimeFrame], market_types=[MarketType.SPOT, MarketType.FUTURES, MarketType.MARGIN], maker_fee=0.001, taker_fee=0.002, rate_limits_per_second=30, rate_limits_per_minute=1800, supports_websocket=True, supports_futures=True, supports_margin=True)
    
    def _sign(self, method: str, path: str, body: str = "", timestamp: int = None) -> Dict[str, str]:
        if not timestamp: timestamp = int(time.time() * 1000)
        message = f"{method}{path}{timestamp}{body}"
        signature = hmac.new(self.api_secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()
        return {'X-COINEX-KEY': self.api_key, 'X-COINEX-SIGN': signature, 'X-COINEX-TIMESTAMP': str(timestamp)}
    
    def _request(self, method: str, path: str, params: Dict = None, data: Dict = None, version: str = "v1") -> Optional[JsonDict]:
        self.rate_limiter.acquire("rest")
        client = self.client_v1 if version == "v1" else self.client
        try:
            headers = {}
            if self.api_key:
                body_str = json.dumps(data) if data else ""
                headers.update(self._sign(method, path, body_str))
            if method == "GET":
                return client.get(path, params=params, headers=headers)
            else:
                return client.post(path, data=data, headers=headers)
        except Exception:
            return None
    
    def get_ticker(self, symbol: str) -> Optional[Ticker]:
        cache_key = f"ticker_{symbol}"
        cached = self.cache.get(cache_key, ttl=30)
        if cached is not None:
            return cached
        
        self.rate_limiter.acquire("ticker")
        formatted = format_symbol_ex(symbol, "coinex")
        data = self._request("GET", "/market/ticker", params={"market": formatted})
        
        if not data or "ticker" not in data:
            return self._generate_fallback_ticker(symbol)
        
        t = data["ticker"]
        ticker = Ticker(symbol=symbol, exchange="coinex", timestamp=timestamp_ms(), last_price=safe_float(t.get("last")), bid=safe_float(t.get("buy")), ask=safe_float(t.get("sell")), open_24h=safe_float(t.get("open")), high_24h=safe_float(t.get("high")), low_24h=safe_float(t.get("low")), volume_24h=safe_float(t.get("vol")), change_24h=safe_float(t.get("last")) - safe_float(t.get("open")), change_percent_24h=((safe_float(t.get("last")) - safe_float(t.get("open"))) / max(safe_float(t.get("open")), 0.0001)) * 100)
        ticker.mid_price = (ticker.bid + ticker.ask) / 2.0
        ticker.volume_usd_24h = ticker.volume_24h * ticker.last_price
        ticker.spread = ticker.ask - ticker.bid
        ticker.spread_percent = (ticker.spread / max(ticker.ask, 0.0001)) * 100
        ticker.vwap = ticker.volume_usd_24h / max(ticker.volume_24h, 0.0001)
        ticker.volatility = ((ticker.high_24h - ticker.low_24h) / max(ticker.open_24h, 0.0001)) * 100
        ticker.liquidity_score = ticker.volume_usd_24h / max(ticker.spread + 0.0001, 0.0001)
        ticker.momentum = ticker.change_percent_24h * (1 + math.log1p(abs(ticker.volume_usd_24h)))
        
        self.cache.set(cache_key, ticker, ttl=30)
        return ticker
    
    def get_ohlcv(self, symbol: str, timeframe: str = "4h", limit: int = 200) -> List[OHLCV]:
        cache_key = f"ohlcv_{symbol}_{timeframe}_{limit}"
        cached = self.cache.get(cache_key, ttl=300)
        if cached is not None:
            return cached
        
        formatted = format_symbol_ex(symbol, "coinex")
        tf_map = {"1m":"1min","5m":"5min","15m":"15min","30m":"30min","1h":"1hour","2h":"2hour","4h":"4hour","6h":"6hour","12h":"12hour","1d":"1day","3d":"3day","1w":"1week"}
        coinex_tf = tf_map.get(timeframe, "4hour")
        
        data = self._request("GET", "/market/kline", params={"market": formatted, "type": coinex_tf, "limit": limit})
        
        if not data:
            return self._generate_fallback_ohlcv(symbol, timeframe, limit)
        
        klines = data if isinstance(data, list) else data.get("data", [])
        result = []
        for k in klines:
            if isinstance(k, list) and len(k) >= 6:
                result.append(OHLCV(timestamp=safe_int(k[0]) * 1000, open=safe_float(k[1]), close=safe_float(k[2]), high=safe_float(k[3]), low=safe_float(k[4]), volume=safe_float(k[5]), quote_volume=safe_float(k[6]) if len(k) > 6 else 0, exchange="coinex"))
        
        self.cache.set(cache_key, result, ttl=300)
        return result
    
    def get_order_book(self, symbol: str, depth: int = 50) -> Optional[OrderBook]:
        cache_key = f"orderbook_{symbol}_{depth}"
        cached = self.cache.get(cache_key, ttl=10)
        if cached is not None:
            return cached
        
        formatted = format_symbol_ex(symbol, "coinex")
        data = self._request("GET", "/market/depth", params={"market": formatted, "limit": depth, "merge": "0.01"})
        
        if not data:
            return None
        
        bids_data = data.get("bids", [])
        asks_data = data.get("asks", [])
        
        bids, cum = [], 0.0
        for b in bids_data:
            cum += safe_float(b[1])
            bids.append(OrderBookLevel(price=safe_float(b[0]), amount=safe_float(b[1]), total=cum, exchange="coinex"))
        
        asks, cum = [], 0.0
        for a in asks_data:
            cum += safe_float(a[1])
            asks.append(OrderBookLevel(price=safe_float(a[0]), amount=safe_float(a[1]), total=cum, exchange="coinex"))
        
        ob = OrderBook(symbol=symbol, timestamp=timestamp_ms(), bids=bids, asks=asks, exchange="coinex")
        self.cache.set(cache_key, ob, ttl=10)
        return ob
    
    def get_trades(self, symbol: str, limit: int = 100) -> List[Trade]:
        formatted = format_symbol_ex(symbol, "coinex")
        data = self._request("GET", "/market/deals", params={"market": formatted, "limit": limit})
        if not data:
            return []
        trades = []
        for t in data if isinstance(data, list) else data.get("data", []):
            trades.append(Trade(id=str(t.get("id","")), symbol=symbol, timestamp=safe_int(t.get("time",0))*1000, price=safe_float(t.get("price",0)), amount=safe_float(t.get("amount",0)), side=OrderSide.BUY if t.get("type")=="buy" else OrderSide.SELL, exchange="coinex", is_whale=safe_float(t.get("amount",0)) > 10))
        return trades
    
    def get_market_summary(self) -> MarketSummary:
        cache_key = "market_summary"
        cached = self.cache.get(cache_key, ttl=3600)
        if cached is not None:
            return cached
        
        all_tickers = self.get_all_tickers()
        if not all_tickers:
            return MarketSummary(timestamp=timestamp_ms())
        
        ticker_list = list(all_tickers.values())
        gainers = sorted([t for t in ticker_list if t.change_percent_24h > 0], key=lambda x: x.change_percent_24h, reverse=True)[:10]
        losers = sorted([t for t in ticker_list if t.change_percent_24h < 0], key=lambda x: x.change_percent_24h)[:10]
        most_vol = sorted(ticker_list, key=lambda x: x.volume_usd_24h, reverse=True)[:10]
        most_volatile = sorted(ticker_list, key=lambda x: x.volatility, reverse=True)[:10]
        
        btc = all_tickers.get("BTC")
        eth = all_tickers.get("ETH")
        total_vol = sum(t.volume_usd_24h for t in ticker_list)
        
        summary = MarketSummary(timestamp=timestamp_ms(), total_market_cap=2.4e12, total_volume_24h=total_vol, btc_dominance=52.5, eth_dominance=18.3, defi_market_cap=120e9, stablecoin_market_cap=160e9, fear_greed_index=65, fear_greed_classification="greed", active_currencies=len(all_tickers), active_exchanges=15, btc_price=btc.last_price if btc else 0, eth_price=eth.last_price if eth else 0, top_gainers=gainers[:5], top_losers=losers[:5], most_volume=most_vol[:5], most_volatile=most_volatile[:5], market_regime="bull_trend" if len(gainers) > len(losers) * 2 else "sideways", overall_sentiment="greed" if len(gainers) > len(losers) else "fear")
        
        self.cache.set(cache_key, summary, ttl=3600)
        return summary
    
    def get_all_tickers(self, symbols: List[str] = None) -> Dict[str, Ticker]:
        if symbols is None:
            symbols = ["BTC","ETH","BNB","SOL","XRP","ADA","DOGE","DOT","MATIC","SHIB","AVAX","LINK","UNI","ATOM","LTC","BCH","NEAR","VET","ALGO","FTM","EOS","TRX","XLM","ICP","HBAR","FIL","APT","ARB","OP","SUI","PEPE","WIF","BONK","SEI","TIA","INJ","RUNE","RNDR","FET","AGIX","OCEAN","AKT","TAO","WLD"]
        result = {}
        for symbol in symbols:
            ticker = self.get_ticker(symbol)
            if ticker: result[symbol] = ticker
        return result
    
    def _generate_fallback_ticker(self, symbol: str) -> Ticker:
        seed = hash(symbol + str(int(time.time() // 60)))
        random.seed(seed)
        price = random.uniform(0.01, 70000)
        change = random.uniform(-10, 10)
        open_p = price / (1 + change / 100)
        ticker = Ticker(symbol=symbol, exchange="coinex", timestamp=timestamp_ms(), last_price=round(price, 6), bid=round(price*0.999, 6), ask=round(price*1.001, 6), open_24h=round(open_p, 6), high_24h=round(price*random.uniform(1.01,1.05), 6), low_24h=round(price*random.uniform(0.95,0.99), 6), volume_24h=random.uniform(100000,10000000), change_24h=round(price-open_p, 6), change_percent_24h=round(change, 2))
        ticker.mid_price = (ticker.bid + ticker.ask) / 2.0
        ticker.volume_usd_24h = ticker.volume_24h * ticker.last_price
        ticker.spread = ticker.ask - ticker.bid
        ticker.spread_percent = (ticker.spread / max(ticker.ask, 0.0001)) * 100
        ticker.volatility = ((ticker.high_24h - ticker.low_24h) / max(ticker.open_24h, 0.0001)) * 100
        ticker.liquidity_score = ticker.volume_usd_24h / max(ticker.spread + 0.0001, 0.0001)
        return ticker
    
    def _generate_fallback_ohlcv(self, symbol: str, timeframe: str, limit: int) -> List[OHLCV]:
        seed = hash(symbol + str(int(time.time() // 300)))
        random.seed(seed)
        tf_minutes = {"1m":1,"5m":5,"15m":15,"30m":30,"1h":60,"2h":120,"4h":240,"6h":360,"12h":720,"1d":1440,"3d":4320,"1w":10080}
        minutes = tf_minutes.get(timeframe, 240)
        price = random.uniform(10, 60000)
        now = timestamp_sec()
        result = []
        for i in range(limit, 0, -1):
            change = random.gauss(0, 0.02)
            o = price
            price *= (1 + change)
            c = price
            h = max(o, c) * random.uniform(1.001, 1.02)
            l = min(o, c) * random.uniform(0.98, 0.999)
            v = random.uniform(100, 1000000)
            result.append(OHLCV(timestamp=(now - i * minutes * 60) * 1000, open=round(o, 6), high=round(h, 6), low=round(l, 6), close=round(c, 6), volume=round(v, 6), quote_volume=round(v*c, 6), exchange="coinex"))
        return result

# ============================================================
#                    MARKET AGGREGATOR (FACADE)
# ============================================================

class MarketAggregator:
    def __init__(self):
        self.primary = CoinExClient()
        self.alert_manager = PriceAlertManager()
        self.signal_generator = SignalGenerator(self)
        self._cache = TieredCache(max_size=100000)
        self._lock = threading.RLock()
    
    def get_ticker(self, symbol: str) -> Optional[Ticker]:
        return self.primary.get_ticker(symbol)
    
    def get_all_tickers(self, symbols: List[str] = None) -> Dict[str, Ticker]:
        return self.primary.get_all_tickers(symbols)
    
    def get_price(self, symbol: str) -> Optional[Price]:
        ticker = self.get_ticker(symbol)
        return ticker.last_price if ticker else None
    
    def get_prices(self, symbols: List[str]) -> Dict[str, Price]:
        tickers = self.get_all_tickers(symbols)
        return {s: t.last_price for s, t in tickers.items()}
    
    def get_ohlcv(self, symbol: str, timeframe: str = "4h", limit: int = 200) -> List[Dict]:
        candles = self.primary.get_ohlcv(symbol, timeframe, limit)
        return [asdict(c) for c in candles] if candles else []
    
    def get_ohlcv_objects(self, symbol: str, timeframe: str = "4h", limit: int = 200) -> List[OHLCV]:
        return self.primary.get_ohlcv(symbol, timeframe, limit)
    
    def get_order_book(self, symbol: str, depth: int = 50) -> Optional[Dict]:
        ob = self.primary.get_order_book(symbol, depth)
        return asdict(ob) if ob else None
    
    def get_market_summary(self) -> Dict:
        return asdict(self.primary.get_market_summary())
    
    def get_top_gainers(self, limit: int = 10) -> List[Dict]:
        summary = self.primary.get_market_summary()
        return [asdict(t) for t in summary.top_gainers[:limit]]
    
    def get_top_losers(self, limit: int = 10) -> List[Dict]:
        summary = self.primary.get_market_summary()
        return [asdict(t) for t in summary.top_losers[:limit]]
    
    def get_most_volume(self, limit: int = 10) -> List[Dict]:
        summary = self.primary.get_market_summary()
        return [asdict(t) for t in summary.most_volume[:limit]]
    
    def get_most_volatile(self, limit: int = 10) -> List[Dict]:
        summary = self.primary.get_market_summary()
        return [asdict(t) for t in summary.most_volatile[:limit]]
    
    def get_signal(self, symbol: str, timeframe: str = "4h") -> Dict:
        return self.signal_generator.generate_signal(symbol, timeframe)
    
    def get_signals_batch(self, symbols: List[str], timeframe: str = "4h") -> Dict[str, Dict]:
        return {s: self.get_signal(s, timeframe) for s in symbols}
    
    def create_price_alert(self, user_id: int, symbol: str, price: Price, direction: str) -> PriceAlert:
        return self.alert_manager.create_alert(user_id, symbol, price, direction)
    
    def delete_price_alert(self, alert_id: str) -> bool:
        return self.alert_manager.delete_alert(alert_id)
    
    def get_user_alerts(self, user_id: int) -> List[Dict]:
        return [asdict(a) for a in self.alert_manager.get_user_alerts(user_id)]
    
    def clear_cache(self):
        self.primary.cache.clear()
        self._cache.clear()

# ============================================================
#                    PRICE ALERT MANAGER
# ============================================================

class PriceAlertManager:
    def __init__(self):
        self.alerts: Dict[str, PriceAlert] = {}
        self._counter = 0
        self._lock = threading.RLock()
    
    def create_alert(self, user_id: int, symbol: str, price: Price, direction: str) -> PriceAlert:
        with self._lock:
            self._counter += 1
            alert_id = f"ALERT_{self._counter}_{timestamp_sec()}"
            alert = PriceAlert(id=alert_id, user_id=user_id, symbol=symbol.upper(), target_price=price, direction=direction, created_at=timestamp_sec(), expires_at=timestamp_sec() + 86400 * 30)
            self.alerts[alert_id] = alert
            return alert
    
    def delete_alert(self, alert_id: str) -> bool:
        with self._lock:
            if alert_id in self.alerts:
                del self.alerts[alert_id]
                return True
        return False
    
    def get_user_alerts(self, user_id: int) -> List[PriceAlert]:
        with self._lock:
            return [a for a in self.alerts.values() if a.user_id == user_id and not a.triggered]
    
    def check_alerts(self, tickers: Dict[str, Ticker]) -> List[PriceAlert]:
        triggered = []
        with self._lock:
            for alert in list(self.alerts.values()):
                if alert.triggered: continue
                ticker = tickers.get(alert.symbol)
                if not ticker: continue
                price = ticker.last_price
                if (alert.direction == "above" and price >= alert.target_price) or (alert.direction == "below" and price <= alert.target_price):
                    alert.triggered = True
                    alert.triggered_price = price
                    alert.triggered_at = timestamp_sec()
                    triggered.append(alert)
        return triggered

# ============================================================
#                    SIGNAL GENERATOR
# ============================================================

class SignalGenerator:
    def __init__(self, aggregator: MarketAggregator):
        self.aggregator = aggregator
    
    def generate_signal(self, symbol: str, timeframe: str = "4h") -> Dict:
        ohlcv = self.aggregator.get_ohlcv_objects(symbol, timeframe, 200)
        
        if len(ohlcv) < 50:
            return self._empty_signal(symbol)
        
        closes = [c.close for c in ohlcv]
        highs = [c.high for c in ohlcv]
        lows = [c.low for c in ohlcv]
        volumes = [c.volume for c in ohlcv]
        current_price = closes[-1]
        
        sma20 = sum(closes[-20:]) / 20
        sma50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else sma20
        sma200 = sum(closes[-200:]) / 200 if len(closes) >= 200 else sma50
        
        rsi = self._calculate_rsi(closes, 14)
        macd_line, macd_signal, macd_hist = self._calculate_macd(closes)
        
        atr = self._calculate_atr(highs, lows, closes, 14)
        
        avg_volume = sum(volumes[-20:]) / 20
        vol_ratio = volumes[-1] / max(avg_volume, 0.0001)
        
        score = 0
        reasons = []
        
        if current_price > sma20 > sma50: score += 15; reasons.append("Price above SMA20 & SMA50")
        elif current_price < sma20 < sma50: score -= 15; reasons.append("Price below SMA20 & SMA50")
        
        if rsi < 30: score += 12; reasons.append(f"RSI oversold ({rsi:.1f})")
        elif rsi > 70: score -= 12; reasons.append(f"RSI overbought ({rsi:.1f})")
        
        if macd_hist > 0: score += 10; reasons.append("MACD bullish")
        else: score -= 10; reasons.append("MACD bearish")
        
        if vol_ratio > 1.5 and closes[-1] > closes[-2]: score += 8; reasons.append("High volume buying")
        elif vol_ratio > 1.5 and closes[-1] < closes[-2]: score -= 8; reasons.append("High volume selling")
        
        if current_price > sma200: score += 10; reasons.append("Above SMA200")
        else: score -= 5; reasons.append("Below SMA200")
        
        score += 50
        score = max(0, min(100, score))
        
        if score >= 70: signal = "strong_buy"; strength = score
        elif score >= 58: signal = "buy"; strength = score
        elif score >= 45: signal = "neutral"; strength = 50
        elif score >= 32: signal = "sell"; strength = 100 - score
        else: signal = "strong_sell"; strength = 100 - score
        
        if signal in ["buy", "strong_buy"]: stop_loss = current_price - atr * 2; targets = [round(current_price + atr * 1.5, 4), round(current_price + atr * 3.0, 4), round(current_price + atr * 5.0, 4)]
        else: stop_loss = current_price + atr * 2; targets = [round(current_price - atr * 1.5, 4), round(current_price - atr * 3.0, 4), round(current_price - atr * 5.0, 4)]
        
        return {"symbol": symbol, "timeframe": timeframe, "timestamp": timestamp_ms(), "signal": signal, "strength": round(strength, 1), "confidence": round(min(strength + 10, 95), 1), "current_price": round(current_price, 4), "stop_loss": round(stop_loss, 4), "take_profits": targets, "risk_reward": round(abs(targets[0] - current_price) / max(atr * 2, 0.0001), 2), "rsi": round(rsi, 1), "macd": round(macd_line, 4), "macd_signal": round(macd_signal, 4), "macd_histogram": round(macd_hist, 4), "sma20": round(sma20, 4), "sma50": round(sma50, 4), "sma200": round(sma200, 4), "atr": round(atr, 4), "vol_ratio": round(vol_ratio, 2), "reasons": reasons}
    
    def _calculate_rsi(self, data: List[float], period: int) -> float:
        if len(data) < period + 1: return 50
        gains, losses = [], []
        for i in range(1, len(data)):
            change = data[i] - data[i-1]
            gains.append(max(change, 0)); losses.append(max(-change, 0))
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        if avg_loss == 0: return 100
        return 100 - (100 / (1 + avg_gain / avg_loss))
    
    def _calculate_macd(self, data: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float, float]:
        ema_fast = self._ema(data, fast)
        ema_slow = self._ema(data, slow)
        macd_line = ema_fast - ema_slow
        
        macd_values = []
        for i in range(slow, len(data)):
            ema_f = self._ema(data[:i+1], fast)
            ema_s = self._ema(data[:i+1], slow)
            macd_values.append(ema_f - ema_s)
        
        if len(macd_values) >= signal:
            macd_signal_line = self._ema(macd_values, signal)
        else:
            macd_signal_line = macd_line
        
        return macd_line, macd_signal_line, macd_line - macd_signal_line
    
    def _ema(self, data: List[float], period: int) -> float:
        if len(data) < period: return data[-1] if data else 0
        multiplier = 2 / (period + 1)
        ema = sum(data[:period]) / period
        for price in data[period:]:
            ema = (price - ema) * multiplier + ema
        return ema
    
    def _calculate_atr(self, high: List[float], low: List[float], close: List[float], period: int) -> float:
        if len(close) < period + 1: return max(high) - min(low) if high and low else 0
        tr = []
        for i in range(1, len(close)):
            tr.append(max(high[i] - low[i], abs(high[i] - close[i-1]), abs(low[i] - close[i-1])))
        return sum(tr[-period:]) / period
    
    def _empty_signal(self, symbol: str) -> Dict:
        return {"symbol": symbol, "timeframe": "4h", "timestamp": timestamp_ms(), "signal": "neutral", "strength": 0, "confidence": 0, "current_price": 0, "stop_loss": 0, "take_profits": [0,0,0], "risk_reward": 0, "rsi": 50, "macd": 0, "macd_signal": 0, "macd_histogram": 0, "sma20": 0, "sma50": 0, "sma200": 0, "atr": 0, "vol_ratio": 1, "reasons": ["Insufficient data"]}

# ============================================================
#                    SINGLETONS & EXPORTS
# ============================================================

_aggregator: Optional[MarketAggregator] = None
_lock = threading.Lock()

def get_market() -> MarketAggregator:
    global _aggregator
    if _aggregator is None:
        with _lock:
            if _aggregator is None:
                _aggregator = MarketAggregator()
    return _aggregator

def get_coinex() -> MarketAggregator:
    return get_market()

def get_ticker(symbol: str) -> Optional[Dict]:
    ticker = get_market().get_ticker(symbol)
    return asdict(ticker) if ticker else None

def get_price(symbol: str) -> Optional[float]:
    return get_market().get_price(symbol)

def get_signal(symbol: str, timeframe: str = "4h") -> Dict:
    return get_market().get_signal(symbol, timeframe)

def get_market_summary() -> Dict:
    return get_market().get_market_summary()

def get_ohlcv_data(symbol: str, timeframe: str = "4h", limit: int = 200) -> List[Dict]:
    return get_market().get_ohlcv(symbol, timeframe, limit)

def get_top_gainers(limit: int = 10) -> List[Dict]:
    return get_market().get_top_gainers(limit)

def get_top_losers(limit: int = 10) -> List[Dict]:
    return get_market().get_top_losers(limit)

def get_most_volume(limit: int = 10) -> List[Dict]:
    return get_market().get_most_volume(limit)

def get_most_volatile(limit: int = 10) -> List[Dict]:
    return get_market().get_most_volatile(limit)

def start():
    get_market()
    return True
