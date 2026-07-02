#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.5 - Market & Exchange Module (Platinum Edition)
ماژول اتصال به صرافی‌ها، دریافت قیمت‌ها، سفارشات، تاریخچه
تحلیل تکنیکال پیشرفته با ۵۰+ اندیکاتور حرفه‌ای
پشتیبانی کامل از تمام ارزها با هوش مصنوعی ترکیبی
"""

import os
import sys
import json
import time
import hmac
import hashlib
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple, Union, Set
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal, ROUND_DOWN, ROUND_UP, getcontext
from pathlib import Path
from cachetools import TTLCache
import aiohttp
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
load_dotenv()

# تنظیم دقت اعشار برای محاسبات مالی
getcontext().prec = 28

# تنظیم لاگر بدون خروجی اضافی
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.NullHandler()]
)
logger = logging.getLogger(__name__)

# ============================================================
# ENUMS & CONSTANTS
# ============================================================

class ExchangeType(Enum):
    """انواع صرافی‌های پشتیبانی شده"""
    COINEX = "coinex"
    BINANCE = "binance"
    KUCOIN = "kucoin"
    BYBIT = "bybit"
    OKX = "okx"
    MEXC = "mexc"
    GATE = "gate"
    BITGET = "bitget"

class OrderSide(Enum):
    """جهت سفارش"""
    BUY = "buy"
    SELL = "sell"

class OrderType(Enum):
    """انواع سفارش"""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"
    OCO = "oco"

class OrderStatus(Enum):
    """وضعیت سفارش"""
    PENDING = "pending"
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    FAILED = "failed"
    EXPIRED = "expired"

class TimeFrame(Enum):
    """تایم‌فریم‌های استاندارد"""
    M1 = "1min"
    M5 = "5min"
    M15 = "15min"
    M30 = "30min"
    H1 = "1hour"
    H4 = "4hour"
    H12 = "12hour"
    D1 = "1day"
    W1 = "1week"
    MN1 = "1month"

class MarketType(Enum):
    """نوع بازار"""
    SPOT = "spot"
    FUTURES = "futures"
    MARGIN = "margin"

# ============================================================
# DATA CLASSES
# ============================================================

@dataclass(frozen=True)
class MarketData:
    """داده‌های بازار (غیرقابل تغییر)"""
    symbol: str
    price: Decimal
    change_24h: Decimal
    volume_24h: Decimal
    high_24h: Decimal
    low_24h: Decimal
    open_24h: Decimal
    close_24h: Decimal
    bid: Decimal
    ask: Decimal
    spread: Decimal = field(init=False)
    timestamp: datetime
    
    def __post_init__(self):
        object.__setattr__(self, 'spread', self.ask - self.bid)

@dataclass(frozen=True)
class OrderBook:
    """کتاب سفارشات"""
    symbol: str
    bids: Tuple[Tuple[Decimal, Decimal], ...]
    asks: Tuple[Tuple[Decimal, Decimal], ...]
    timestamp: datetime
    spread: Decimal = field(init=False)
    
    def __post_init__(self):
        if self.bids and self.asks:
            best_bid = self.bids[0][0]
            best_ask = self.asks[0][0]
            object.__setattr__(self, 'spread', best_ask - best_bid)
        else:
            object.__setattr__(self, 'spread', Decimal('0'))

@dataclass(frozen=True)
class OrderResult:
    """نتیجه سفارش"""
    order_id: str
    symbol: str
    side: OrderSide
    type: OrderType
    price: Decimal
    amount: Decimal
    filled: Decimal
    status: OrderStatus
    fee: Decimal
    fee_currency: str
    timestamp: datetime
    average_price: Decimal = Decimal('0')

@dataclass(frozen=True)
class TechnicalIndicators:
    """اندیکاتورهای تکنیکال"""
    timestamp: datetime
    rsi: float
    rsi_7: float
    rsi_21: float
    macd: float
    macd_signal: float
    macd_histogram: float
    sma_7: float
    sma_25: float
    sma_50: float
    sma_200: float
    ema_9: float
    ema_21: float
    ema_50: float
    ema_200: float
    bb_upper: float
    bb_middle: float
    bb_lower: float
    bb_position: float
    stoch_k: float
    stoch_d: float
    mfi: float
    adx: float
    plus_di: float
    minus_di: float
    atr: float
    cci: float
    williams_r: float
    obv: float
    vwap: float
    supertrend: float
    supertrend_direction: int

# ============================================================
# EXCHANGE BASE
# ============================================================

class BaseExchange:
    """کلاس پایه برای تمام صرافی‌ها"""
    
    def __init__(self, exchange_type: ExchangeType):
        self.exchange_type = exchange_type
        self._session: Optional[aiohttp.ClientSession] = None
        self._semaphore = asyncio.Semaphore(20)
        self._cache = TTLCache(maxsize=1000, ttl=30)
        self._kline_cache = TTLCache(maxsize=500, ttl=60)
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """ایجاد یا بازیابی نشست HTTP"""
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(limit=50, limit_per_host=20)
            timeout = aiohttp.ClientTimeout(total=30)
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={"User-Agent": "CryptoPulseAI/3.5"}
            )
        return self._session
    
    async def close(self):
        """بستن نشست"""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
    
    async def _rate_limit(self):
        """کنترل نرخ درخواست با Semaphore"""
        async with self._semaphore:
            await asyncio.sleep(0.01)
    
    @staticmethod
    def _safe_decimal(value: Any, default: Decimal = Decimal('0')) -> Decimal:
        """تبدیل ایمن به Decimal"""
        try:
            return Decimal(str(value))
        except:
            return default

# ============================================================
# COINEX EXCHANGE - نسخه نهایی
# ============================================================

class CoinExExchange(BaseExchange):
    """اتصال به صرافی CoinEx با API v2"""
    
    def __init__(self):
        super().__init__(ExchangeType.COINEX)
        
        # خواندن کلیدها از متغیرهای محیطی (امنیت بالا)
        self.api_key = os.getenv("COINEX_API_KEY", "")
        self.secret_key = os.getenv("COINEX_SECRET_KEY", "")
        
        # API v2 endpoints
        self.base_url = "https://api.coinex.com/v2"
        
        # تنظیمات
        self.timeout = 30
        self.max_retries = 3
        self.retry_delay = 1
        
        # نقشه ارزها (ترتیب صحیح)
        self.coin_map = self._create_coin_map()
        self.supported_coins = list(self.coin_map.keys())
        
        # بازارهای فیوچرز
        self.futures_markets = self._create_futures_map()
    
    def _create_coin_map(self) -> Dict[str, str]:
        """ایجاد نقشه ارزها"""
        return {
            "BTC": "BTCUSDT", "ETH": "ETHUSDT", "BNB": "BNBUSDT",
            "SOL": "SOLUSDT", "XRP": "XRPUSDT", "ADA": "ADAUSDT",
            "DOGE": "DOGEUSDT", "DOT": "DOTUSDT", "MATIC": "MATICUSDT",
            "SHIB": "SHIBUSDT", "AVAX": "AVAXUSDT", "LINK": "LINKUSDT",
            "UNI": "UNIUSDT", "ATOM": "ATOMUSDT", "LTC": "LTCUSDT",
            "BCH": "BCHUSDT", "NEAR": "NEARUSDT", "VET": "VETUSDT",
            "ALGO": "ALGOUSDT", "FTM": "FTMUSDT", "EOS": "EOSUSDT",
            "TRX": "TRXUSDT", "XLM": "XLMUSDT", "ICP": "ICPUSDT",
            "HBAR": "HBARUSDT", "FIL": "FILUSDT", "APT": "APTUSDT",
            "ARB": "ARBUSDT", "OP": "OPUSDT", "MKR": "MKRUSDT",
            "AAVE": "AAVEUSDT", "INJ": "INJUSDT", "TON": "TONUSDT",
            "SUI": "SUIUSDT", "PEPE": "PEPEUSDT", "BONK": "BONKUSDT",
            "FLOKI": "FLOKIUSDT", "WIF": "WIFUSDT", "JUP": "JUPUSDT",
            "JASMY": "JASMYUSDT", "KAS": "KASUSDT", "RNDR": "RNDRUSDT",
            "THETA": "THETAUSDT", "FET": "FETUSDT", "AGIX": "AGIXUSDT",
            "OCEAN": "OCEANUSDT", "IMX": "IMXUSDT", "SEI": "SEIUSDT",
            "TIA": "TIAUSDT", "STRK": "STRKUSDT", "ENA": "ENAUSDT"
        }
    
    def _create_futures_map(self) -> Dict[str, str]:
        """ایجاد نقشه بازارهای فیوچرز"""
        return {k: v.replace("USDT", "USDT_PERP") for k, v in self.coin_map.items()}
    
    def _normalize_symbol(self, symbol: str, market_type: MarketType = MarketType.SPOT) -> str:
        """نرمال‌سازی نماد"""
        symbol = symbol.upper().strip()
        
        if market_type == MarketType.FUTURES and symbol in self.futures_markets:
            return self.futures_markets[symbol]
        
        if symbol in self.coin_map:
            return self.coin_map[symbol]
        
        if not symbol.endswith("USDT"):
            return f"{symbol}USDT"
        
        return symbol
    
    def _sign_request(self, method: str, path: str, body: str = "") -> Dict[str, str]:
        """امضای درخواست برای API v2"""
        if not self.api_key or not self.secret_key:
            return {}
        
        timestamp = str(int(time.time() * 1000))
        message = f"{method}{path}{timestamp}{body}"
        
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest().lower()
        
        return {
            "X-COINEX-KEY": self.api_key,
            "X-COINEX-SIGN": signature,
            "X-COINEX-TIMESTAMP": timestamp,
            "Content-Type": "application/json"
        }
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Dict[str, Any] = None,
        body: Dict[str, Any] = None,
        signed: bool = False
    ) -> Dict[str, Any]:
        """درخواست HTTP با مدیریت خطا"""
        await self._rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        body_str = json.dumps(body) if body else ""
        headers = {}
        
        if signed:
            headers.update(self._sign_request(method, endpoint, body_str))
        else:
            headers["Content-Type"] = "application/json"
        
        session = await self._get_session()
        
        for attempt in range(self.max_retries):
            try:
                if method == "GET":
                    async with session.get(url, params=params, headers=headers) as response:
                        data = await response.json()
                else:
                    async with session.post(url, params=params, json=body, headers=headers) as response:
                        data = await response.json()
                
                if data.get("code") == 0:
                    return data.get("data", {})
                
                error_msg = data.get("message", "Unknown error")
                
                if "rate limit" in error_msg.lower():
                    await asyncio.sleep(2 ** attempt)
                    continue
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    continue
                
                return {"error": error_msg}
                
            except asyncio.TimeoutError:
                if attempt == self.max_retries - 1:
                    return {"error": "Request timeout"}
                await asyncio.sleep(self.retry_delay)
            
            except aiohttp.ClientError as e:
                if attempt == self.max_retries - 1:
                    return {"error": f"Connection error: {str(e)}"}
                await asyncio.sleep(self.retry_delay)
            
            except Exception as e:
                logger.error(f"Unexpected error in request: {e}")
                return {"error": f"Unexpected error: {str(e)}"}
        
        return {"error": "Max retries exceeded"}
    
    # ==================== قیمت‌ها ====================
    
    async def get_ticker(self, symbol: str) -> Optional[MarketData]:
        """دریافت تیکر با کش"""
        symbol = self._normalize_symbol(symbol)
        
        cache_key = f"ticker_{symbol}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        result = await self._request("GET", "/market/ticker", {"market": symbol})
        
        if "error" in result:
            return None
        
        try:
            data = MarketData(
                symbol=symbol,
                price=self._safe_decimal(result.get("last")),
                change_24h=self._safe_decimal(result.get("change")),
                volume_24h=self._safe_decimal(result.get("vol")),
                high_24h=self._safe_decimal(result.get("high")),
                low_24h=self._safe_decimal(result.get("low")),
                open_24h=self._safe_decimal(result.get("open")),
                close_24h=self._safe_decimal(result.get("last")),
                bid=self._safe_decimal(result.get("buy")),
                ask=self._safe_decimal(result.get("sell")),
                timestamp=datetime.now()
            )
            
            self._cache[cache_key] = data
            return data
        except Exception as e:
            logger.error(f"Error parsing ticker for {symbol}: {e}")
            return None
    
    async def get_all_tickers(self) -> Dict[str, MarketData]:
        """دریافت تمام تیکرها"""
        result = await self._request("GET", "/market/ticker/all")
        
        if "error" in result:
            return {}
        
        tickers = {}
        for symbol, data in result.items():
            if not symbol.endswith("USDT"):
                continue
            
            try:
                tickers[symbol] = MarketData(
                    symbol=symbol,
                    price=self._safe_decimal(data.get("last")),
                    change_24h=self._safe_decimal(data.get("change")),
                    volume_24h=self._safe_decimal(data.get("vol")),
                    high_24h=self._safe_decimal(data.get("high")),
                    low_24h=self._safe_decimal(data.get("low")),
                    open_24h=self._safe_decimal(data.get("open")),
                    close_24h=self._safe_decimal(data.get("last")),
                    bid=self._safe_decimal(data.get("buy")),
                    ask=self._safe_decimal(data.get("sell")),
                    timestamp=datetime.now()
                )
            except Exception as e:
                logger.error(f"Error parsing ticker for {symbol}: {e}")
                continue
        
        return tickers
    
    async def get_top_gainers(self, limit: int = 20) -> List[MarketData]:
        """دریافت بیشترین رشدها"""
        tickers = await self.get_all_tickers()
        
        sorted_tickers = sorted(
            tickers.values(),
            key=lambda x: x.change_24h,
            reverse=True
        )
        
        return sorted_tickers[:limit]
    
    async def get_top_losers(self, limit: int = 20) -> List[MarketData]:
        """دریافت بیشترین افت‌ها"""
        tickers = await self.get_all_tickers()
        
        sorted_tickers = sorted(
            tickers.values(),
            key=lambda x: x.change_24h
        )
        
        return sorted_tickers[:limit]
    
    # ==================== تاریخچه قیمت ====================
    
    async def get_kline(
        self,
        symbol: str,
        interval: str = "4h",
        limit: int = 200
    ) -> Optional[pd.DataFrame]:
        """دریافت کندل‌ها با کش"""
        symbol = self._normalize_symbol(symbol)
        
        cache_key = f"kline_{symbol}_{interval}_{limit}"
        if cache_key in self._kline_cache:
            return self._kline_cache[cache_key]
        
        result = await self._request(
            "GET",
            "/market/kline",
            {
                "market": symbol,
                "type": interval,
                "limit": limit
            }
        )
        
        if "error" in result or not result:
            return None
        
        try:
            df = pd.DataFrame(
                result,
                columns=['timestamp', 'open', 'close', 'high', 'low', 'volume', 'amount']
            )
            
            for col in ['open', 'close', 'high', 'low', 'volume', 'amount']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            df.set_index('timestamp', inplace=True)
            df.dropna(inplace=True)
            
            if df.empty:
                return None
            
            self._kline_cache[cache_key] = df
            return df
            
        except Exception as e:
            logger.error(f"Error parsing kline for {symbol}: {e}")
            return None
    
    async def get_price_history(
        self,
        symbol: str,
        interval: str = "4h",
        limit: int = 100
    ) -> List[float]:
        """دریافت تاریخچه قیمت"""
        df = await self.get_kline(symbol, interval, limit)
        if df is not None and not df.empty:
            return df['close'].tolist()
        return []
    
    # ==================== کتاب سفارشات ====================
    
    async def get_order_book(self, symbol: str, limit: int = 20) -> Optional[OrderBook]:
        """دریافت کتاب سفارشات"""
        symbol = self._normalize_symbol(symbol)
        
        result = await self._request(
            "GET",
            "/market/depth",
            {"market": symbol, "limit": limit}
        )
        
        if "error" in result:
            return None
        
        try:
            bids = tuple(
                (self._safe_decimal(b[0]), self._safe_decimal(b[1]))
                for b in result.get("bids", [])
            )
            asks = tuple(
                (self._safe_decimal(a[0]), self._safe_decimal(a[1]))
                for a in result.get("asks", [])
            )
            
            return OrderBook(
                symbol=symbol,
                bids=bids,
                asks=asks,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error parsing order book for {symbol}: {e}")
            return None
    
    # ==================== سفارشات ====================
    
    async def place_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        amount: Decimal,
        price: Decimal = None,
        stop_price: Decimal = None
    ) -> Optional[OrderResult]:
        """ثبت سفارش"""
        if not self.api_key:
            return None
        
        symbol = self._normalize_symbol(symbol)
        
        body = {
            "market": symbol,
            "side": side.value,
            "type": order_type.value,
            "amount": str(amount)
        }
        
        if price and order_type != OrderType.MARKET:
            body["price"] = str(price)
        if stop_price:
            body["stop_price"] = str(stop_price)
        
        result = await self._request("POST", "/order/limit", body=body, signed=True)
        
        if "error" in result:
            return None
        
        try:
            return OrderResult(
                order_id=str(result.get("id", "")),
                symbol=symbol,
                side=side,
                type=order_type,
                price=self._safe_decimal(result.get("price")),
                amount=self._safe_decimal(result.get("amount")),
                filled=self._safe_decimal(result.get("deal_amount")),
                status=OrderStatus(result.get("status", "pending")),
                fee=self._safe_decimal(result.get("fee")),
                fee_currency=result.get("fee_coin", "USDT"),
                timestamp=datetime.now(),
                average_price=self._safe_decimal(result.get("avg_price"))
            )
        except Exception as e:
            logger.error(f"Error parsing order result: {e}")
            return None
    
    async def cancel_order(self, order_id: str) -> bool:
        """لغو سفارش"""
        if not self.api_key:
            return False
        
        result = await self._request(
            "POST",
            "/order/cancel",
            body={"id": order_id},
            signed=True
        )
        return "error" not in result
    
    async def get_order(self, order_id: str) -> Optional[OrderResult]:
        """دریافت وضعیت سفارش"""
        if not self.api_key:
            return None
        
        result = await self._request(
            "GET",
            "/order/status",
            params={"id": order_id},
            signed=True
        )
        
        if "error" in result:
            return None
        
        try:
            return OrderResult(
                order_id=str(result.get("id", "")),
                symbol=result.get("market", ""),
                side=OrderSide(result.get("side", "buy")),
                type=OrderType(result.get("type", "limit")),
                price=self._safe_decimal(result.get("price")),
                amount=self._safe_decimal(result.get("amount")),
                filled=self._safe_decimal(result.get("deal_amount")),
                status=OrderStatus(result.get("status", "pending")),
                fee=self._safe_decimal(result.get("fee")),
                fee_currency=result.get("fee_coin", "USDT"),
                timestamp=datetime.now(),
                average_price=self._safe_decimal(result.get("avg_price"))
            )
        except Exception as e:
            logger.error(f"Error parsing order: {e}")
            return None
    
    async def get_open_orders(self, symbol: str = None) -> List[OrderResult]:
        """دریافت سفارشات باز"""
        if not self.api_key:
            return []
        
        params = {}
        if symbol:
            params["market"] = self._normalize_symbol(symbol)
        
        result = await self._request("GET", "/order/pending", params=params, signed=True)
        
        if "error" in result:
            return []
        
        orders = []
        for order in result.get("data", []):
            try:
                orders.append(OrderResult(
                    order_id=str(order.get("id", "")),
                    symbol=order.get("market", ""),
                    side=OrderSide(order.get("side", "buy")),
                    type=OrderType(order.get("type", "limit")),
                    price=self._safe_decimal(order.get("price")),
                    amount=self._safe_decimal(order.get("amount")),
                    filled=self._safe_decimal(order.get("deal_amount")),
                    status=OrderStatus(order.get("status", "pending")),
                    fee=self._safe_decimal(order.get("fee")),
                    fee_currency=order.get("fee_coin", "USDT"),
                    timestamp=datetime.now()
                ))
            except Exception as e:
                logger.error(f"Error parsing open order: {e}")
                continue
        
        return orders
    
    # ==================== موجودی ====================
    
    async def get_balance(self, coin: str = None) -> Dict[str, Decimal]:
        """دریافت موجودی"""
        if not self.api_key:
            return {}
        
        result = await self._request("GET", "/balance/info", signed=True)
        
        if "error" in result:
            return {}
        
        balances = {}
        for coin_name, data in result.items():
            if isinstance(data, dict):
                available = self._safe_decimal(data.get("available"))
                frozen = self._safe_decimal(data.get("frozen"))
                balances[coin_name] = available + frozen
        
        if coin:
            coin = coin.upper()
            return {coin: balances.get(coin, Decimal('0'))}
        
        return balances
    
    async def get_total_balance_usdt(self) -> Decimal:
        """محاسبه موجودی کل به USDT"""
        balances = await self.get_balance()
        total = Decimal('0')
        
        for coin, amount in balances.items():
            if amount == Decimal('0'):
                continue
            
            if coin == "USDT":
                total += amount
                continue
            
            try:
                ticker = await self.get_ticker(coin)
                if ticker:
                    total += amount * ticker.price
            except Exception:
                continue
        
        return total
    
    # ==================== تحلیل تکنیکال پیشرفته ====================
    
    @staticmethod
    def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        محاسبه تمام اندیکاتورهای تکنیکال
        نسخه نهایی با ۵۰+ اندیکاتور
        """
        if df is None or df.empty or len(df) < 200:
            return df
        
        df = df.copy()
        
        # ===== میانگین‌های متحرک =====
        # SMA
        for period in [7, 14, 21, 25, 50, 99, 100, 200]:
            df[f'sma_{period}'] = df['close'].rolling(window=period).mean()
        
        # EMA (استاندارد)
        for period in [9, 12, 21, 26, 50, 200]:
            df[f'ema_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
        
        # HMA (Hull Moving Average)
        for period in [9, 21]:
            wma_half = df['close'].rolling(window=period // 2).mean()
            wma_full = df['close'].rolling(window=period).mean()
            hma_input = 2 * wma_half - wma_full
            df[f'hma_{period}'] = hma_input.rolling(window=int(np.sqrt(period))).mean()
        
        # ===== RSI (فرمول استاندارد با EMA) =====
        for period in [7, 14, 21]:
            delta = df['close'].diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            
            avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
            avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
            
            rs = avg_gain / avg_loss.replace(0, np.nan)
            df[f'rsi_{period}'] = 100 - (100 / (1 + rs))
        
        # ===== MACD =====
        ema_12 = df['close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        df['macd_histogram_2x'] = df['macd_histogram'] * 2
        
        # ===== Bollinger Bands =====
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        df['bb_width'] = df['bb_upper'] - df['bb_lower']
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_width'].replace(0, np.nan))
        df['bb_squeeze'] = df['bb_width'] / df['bb_middle']
        
        # ===== Stochastic =====
        for k_period, d_period in [(14, 3), (5, 3)]:
            low_min = df['low'].rolling(window=k_period).min()
            high_max = df['high'].rolling(window=k_period).max()
            df[f'stoch_k_{k_period}'] = 100 * ((df['close'] - low_min) / (high_max - low_min).replace(0, np.nan))
            df[f'stoch_d_{k_period}'] = df[f'stoch_k_{k_period}'].rolling(window=d_period).mean()
        
        # ===== MFI (Money Flow Index) =====
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        money_flow = typical_price * df['volume']
        
        positive_flow = money_flow.where(typical_price > typical_price.shift(), 0)
        negative_flow = money_flow.where(typical_price < typical_price.shift(), 0)
        
        positive_sum = positive_flow.rolling(window=14).sum()
        negative_sum = negative_flow.rolling(window=14).sum()
        
        money_ratio = positive_sum / negative_sum.replace(0, np.nan)
        df['mfi'] = 100 - (100 / (1 + money_ratio))
        
        # ===== ATR (Average True Range - Wilder's Method) =====
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = true_range.ewm(alpha=1/14, adjust=False).mean()
        
        # ===== ADX (Average Directional Index) =====
        plus_dm = df['high'].diff()
        minus_dm = df['low'].diff().abs() * -1
        
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        minus_dm = minus_dm.abs()
        
        plus_dm[plus_dm < minus_dm] = 0
        minus_dm[minus_dm < plus_dm] = 0
        
        atr_14 = true_range.ewm(alpha=1/14, adjust=False).mean()
        
        plus_di = 100 * (plus_dm.ewm(alpha=1/14, adjust=False).mean() / atr_14.replace(0, np.nan))
        minus_di = 100 * (minus_dm.ewm(alpha=1/14, adjust=False).mean() / atr_14.replace(0, np.nan))
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di).replace(0, np.nan)
        df['adx'] = dx.ewm(alpha=1/14, adjust=False).mean()
        df['plus_di'] = plus_di
        df['minus_di'] = minus_di
        
        # ===== CCI (Commodity Channel Index) =====
        tp = (df['high'] + df['low'] + df['close']) / 3
        sma_tp = tp.rolling(window=20).mean()
        mad = tp.rolling(window=20).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=True)
        df['cci'] = (tp - sma_tp) / (0.015 * mad)
        
        # ===== Williams %R =====
        df['williams_r'] = -100 * ((df['high'].rolling(14).max() - df['close']) / 
                                   (df['high'].rolling(14).max() - df['low'].rolling(14).min()).replace(0, np.nan))
        
        # ===== OBV (On-Balance Volume) =====
        df['obv'] = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
        
        # ===== VWAP (Volume Weighted Average Price) =====
        df['vwap'] = (df['volume'] * (df['high'] + df['low'] + df['close']) / 3).cumsum() / df['volume'].cumsum().replace(0, np.nan)
        
        # ===== Ichimoku Cloud =====
        df['tenkan_sen'] = (df['high'].rolling(9).max() + df['low'].rolling(9).min()) / 2
        df['kijun_sen'] = (df['high'].rolling(26).max() + df['low'].rolling(26).min()) / 2
        df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)
        df['senkou_span_b'] = ((df['high'].rolling(52).max() + df['low'].rolling(52).min()) / 2).shift(26)
        df['chikou_span'] = df['close'].shift(-26)
        
        # ===== SuperTrend =====
        atr_super = df['atr']
        multiplier = 3
        
        basic_upper = (df['high'] + df['low']) / 2 + multiplier * atr_super
        basic_lower = (df['high'] + df['low']) / 2 - multiplier * atr_super
        
        final_upper = basic_upper.copy()
        final_lower = basic_lower.copy()
        supertrend = pd.Series(0.0, index=df.index)
        
        for i in range(1, len(df)):
            if df['close'].iloc[i] <= final_upper.iloc[i-1]:
                final_upper.iloc[i] = min(basic_upper.iloc[i], final_upper.iloc[i-1])
            else:
                final_upper.iloc[i] = basic_upper.iloc[i]
            
            if df['close'].iloc[i] >= final_lower.iloc[i-1]:
                final_lower.iloc[i] = max(basic_lower.iloc[i], final_lower.iloc[i-1])
            else:
                final_lower.iloc[i] = basic_lower.iloc[i]
            
            if df['close'].iloc[i] <= final_upper.iloc[i]:
                supertrend.iloc[i] = final_upper.iloc[i]
            else:
                supertrend.iloc[i] = final_lower.iloc[i]
        
        df['supertrend'] = supertrend
        df['supertrend_direction'] = np.where(df['close'] > df['supertrend'], 1, -1)
        
        # ===== Keltner Channel =====
        df['kc_middle'] = df['close'].ewm(span=20, adjust=False).mean()
        df['kc_upper'] = df['kc_middle'] + (df['atr'] * 2)
        df['kc_lower'] = df['kc_middle'] - (df['atr'] * 2)
        
        # ===== Donchian Channel =====
        df['dc_upper'] = df['high'].rolling(window=20).max()
        df['dc_lower'] = df['low'].rolling(window=20).min()
        df['dc_middle'] = (df['dc_upper'] + df['dc_lower']) / 2
        
        # ===== Parabolic SAR =====
        df['psar'] = df['close'].copy()
        df['psar_direction'] = 0
        
        acceleration = 0.02
        maximum = 0.2
        
        bull = True
        af = acceleration
        ep = df['low'].iloc[0]
        sar = df['high'].iloc[0]
        
        for i in range(1, len(df)):
            prev_sar = sar
            
            if bull:
                sar = prev_sar + af * (ep - prev_sar)
                sar = min(sar, df['low'].iloc[i-1], df['low'].iloc[i-2] if i >= 2 else sar)
                
                if df['high'].iloc[i] > ep:
                    ep = df['high'].iloc[i]
                    af = min(af + acceleration, maximum)
                
                if df['close'].iloc[i] < sar:
                    bull = False
                    af = acceleration
                    sar = ep
                    ep = df['low'].iloc[i]
            else:
                sar = prev_sar + af * (ep - prev_sar)
                sar = max(sar, df['high'].iloc[i-1], df['high'].iloc[i-2] if i >= 2 else sar)
                
                if df['low'].iloc[i] < ep:
                    ep = df['low'].iloc[i]
                    af = min(af + acceleration, maximum)
                
                if df['close'].iloc[i] > sar:
                    bull = True
                    af = acceleration
                    sar = ep
                    ep = df['high'].iloc[i]
            
            df['psar'].iloc[i] = sar
            df['psar_direction'].iloc[i] = 1 if bull else -1
        
        # ===== Pivot Points =====
        df['pivot'] = (df['high'] + df['low'] + df['close']) / 3
        df['r1'] = 2 * df['pivot'] - df['low']
        df['r2'] = df['pivot'] + (df['high'] - df['low'])
        df['r3'] = df['high'] + 2 * (df['pivot'] - df['low'])
        df['s1'] = 2 * df['pivot'] - df['high']
        df['s2'] = df['pivot'] - (df['high'] - df['low'])
        df['s3'] = df['low'] - 2 * (df['high'] - df['pivot'])
        
        # ===== Fibonacci Retracement =====
        high_50 = df['high'].rolling(window=50).max()
        low_50 = df['low'].rolling(window=50).min()
        diff_50 = high_50 - low_50
        
        for level in [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]:
            df[f'fib_{level}'] = high_50 - diff_50 * level
        
        # ===== Chaikin Money Flow =====
        mfm = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low']).replace(0, np.nan)
        mfv = mfm * df['volume']
        df['cmf'] = mfv.rolling(window=20).sum() / df['volume'].rolling(window=20).sum().replace(0, np.nan)
        
        # ===== Ultimate Oscillator =====
        bp = df['close'] - pd.concat([df['low'], df['close'].shift()], axis=1).min(axis=1)
        tr_uo = pd.concat([df['high'] - df['low'], 
                          abs(df['high'] - df['close'].shift()), 
                          abs(df['low'] - df['close'].shift())], axis=1).max(axis=1)
        
        avg7 = bp.rolling(7).sum() / tr_uo.rolling(7).sum().replace(0, np.nan)
        avg14 = bp.rolling(14).sum() / tr_uo.rolling(14).sum().replace(0, np.nan)
        avg28 = bp.rolling(28).sum() / tr_uo.rolling(28).sum().replace(0, np.nan)
        
        df['ultimate_oscillator'] = 100 * (4 * avg7 + 2 * avg14 + avg28) / 7
        
        # ===== TSI (True Strength Index) =====
        momentum = df['close'].diff()
        abs_momentum = momentum.abs()
        
        smoothed_momentum = momentum.ewm(span=25, adjust=False).mean().ewm(span=13, adjust=False).mean()
        smoothed_abs_momentum = abs_momentum.ewm(span=25, adjust=False).mean().ewm(span=13, adjust=False).mean()
        
        df['tsi'] = 100 * smoothed_momentum / smoothed_abs_momentum.replace(0, np.nan)
        df['tsi_signal'] = df['tsi'].ewm(span=7, adjust=False).mean()
        
        # ===== Fisher Transform =====
        high_low_range = df['high'] - df['low']
        mid_point = (df['high'] + df['low']) / 2
        
        price_normalized = 2 * ((mid_point - df['low'].rolling(10).min()) / 
                               (high_low_range.rolling(10).max()).replace(0, np.nan)) - 1
        price_normalized = price_normalized.clip(-0.999, 0.999)
        
        df['fisher_transform'] = 0.5 * np.log((1 + price_normalized) / (1 - price_normalized))
        df['fisher_signal'] = df['fisher_transform'].shift(1)
        
        # ===== DPO (Detrended Price Oscillator) =====
        df['dpo'] = df['close'].shift(-11) - df['close'].rolling(window=21).mean().shift(-11)
        
        return df
    
    async def get_technical_analysis(self, symbol: str, interval: str = "4h") -> Optional[TechnicalIndicators]:
        """دریافت تحلیل تکنیکال کامل"""
        df = await self.get_kline(symbol, interval, 200)
        
        if df is None or df.empty:
            return None
        
        df = self.calculate_all_indicators(df)
        last = df.iloc[-1]
        
        try:
            return TechnicalIndicators(
                timestamp=datetime.now(),
                rsi=float(last.get('rsi_14', 50)),
                rsi_7=float(last.get('rsi_7', 50)),
                rsi_21=float(last.get('rsi_21', 50)),
                macd=float(last.get('macd', 0)),
                macd_signal=float(last.get('macd_signal', 0)),
                macd_histogram=float(last.get('macd_histogram', 0)),
                sma_7=float(last.get('sma_7', 0)),
                sma_25=float(last.get('sma_25', 0)),
                sma_50=float(last.get('sma_50', 0)),
                sma_200=float(last.get('sma_200', 0)),
                ema_9=float(last.get('ema_9', 0)),
                ema_21=float(last.get('ema_21', 0)),
                ema_50=float(last.get('ema_50', 0)),
                ema_200=float(last.get('ema_200', 0)),
                bb_upper=float(last.get('bb_upper', 0)),
                bb_middle=float(last.get('bb_middle', 0)),
                bb_lower=float(last.get('bb_lower', 0)),
                bb_position=float(last.get('bb_position', 0.5)),
                stoch_k=float(last.get('stoch_k_14', 50)),
                stoch_d=float(last.get('stoch_d_14', 50)),
                mfi=float(last.get('mfi', 50)),
                adx=float(last.get('adx', 25)),
                plus_di=float(last.get('plus_di', 25)),
                minus_di=float(last.get('minus_di', 25)),
                atr=float(last.get('atr', 0)),
                cci=float(last.get('cci', 0)),
                williams_r=float(last.get('williams_r', -50)),
                obv=float(last.get('obv', 0)),
                vwap=float(last.get('vwap', 0)),
                supertrend=float(last.get('supertrend', 0)),
                supertrend_direction=int(last.get('supertrend_direction', 0))
            )
        except Exception as e:
            logger.error(f"Error creating technical indicators: {e}")
            return None

# ============================================================
# SINGLETON INSTANCE
# ============================================================

# ایجاد نمونه سراسری
exchange = CoinExExchange()

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

async def get_price(symbol: str) -> Optional[Decimal]:
    """دریافت قیمت سریع"""
    ticker = await exchange.get_ticker(symbol)
    return ticker.price if ticker else None

async def get_prices(symbols: List[str]) -> Dict[str, Decimal]:
    """دریافت قیمت چند ارز"""
    tasks = [get_price(s) for s in symbols]
    results = await asyncio.gather(*tasks)
    return {s: r for s, r in zip(symbols, results) if r is not None}

async def get_top_movers(limit: int = 10) -> Tuple[List[MarketData], List[MarketData]]:
    """دریافت بیشترین رشد و افت"""
    gainers = await exchange.get_top_gainers(limit)
    losers = await exchange.get_top_losers(limit)
    return gainers, losers

# ============================================================
# MAIN - تست
# ============================================================

async def main():
    """تست ماژول"""
    print("=" * 60)
    print("  CryptoPulse AI v3.5 - Exchange Module Test")
    print("=" * 60)
    
    # تست قیمت
    btc_price = await get_price("BTC")
    if btc_price:
        print(f"✅ BTC Price: ${btc_price:,.2f}")
    
    # تست تحلیل تکنیکال
    analysis = await exchange.get_technical_analysis("BTC", "4h")
    if analysis:
        print(f"✅ RSI(14): {analysis.rsi:.2f}")
        print(f"✅ MACD: {analysis.macd:.2f}")
        print(f"✅ ADX: {analysis.adx:.2f}")
        print(f"✅ SuperTrend Direction: {analysis.supertrend_direction}")
    
    print("=" * 60)
    print("  Test completed!")
    print("=" * 60)
    
    await exchange.close()

if __name__ == "__main__":
    asyncio.run(main())
