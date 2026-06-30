#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - Market & Exchange Module
ماژول اتصال به صرافی CoinEx، دریافت قیمت‌ها، سفارشات، تاریخچه
پشتیبانی کامل از تمام ارزها با تحلیل تکنیکال پیشرفته
"""

import os
import sys
import json
import time
import hmac
import hashlib
import base64
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import pandas as pd
import numpy as np
from decimal import Decimal, ROUND_DOWN, ROUND_UP

# ==================== تنظیمات صرافی ====================

class ExchangeType(Enum):
    COINEX = "coinex"
    BINANCE = "binance"
    KUCOIN = "kucoin"
    BYBIT = "bybit"
    OKX = "okx"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"

class OrderStatus(Enum):
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    CANCELLED = "cancelled"
    FAILED = "failed"
    EXPIRED = "expired"

@dataclass
class MarketData:
    symbol: str
    price: float
    change_24h: float
    volume_24h: float
    high_24h: float
    low_24h: float
    open_24h: float
    close_24h: float
    bid: float
    ask: float
    spread: float
    timestamp: datetime

@dataclass
class OrderBook:
    symbol: str
    bids: List[Tuple[float, float]]
    asks: List[Tuple[float, float]]
    timestamp: datetime

@dataclass
class OrderResult:
    order_id: str
    symbol: str
    side: OrderSide
    type: OrderType
    price: float
    amount: float
    filled: float
    status: OrderStatus
    fee: float
    fee_currency: str
    timestamp: datetime

# ==================== کلاس اصلی CoinEx ====================

class CoinExExchange:
    """اتصال به صرافی CoinEx با پشتیبانی کامل"""
    
    def __init__(self, api_key: str, secret_key: str, base_url: str = "https://api.coinex.com/v1"):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url
        self._session = None
        self._rate_limiter = defaultdict(list)
        self._cache = {}
        self._cache_ttl = 30
        
        self.timeout = 30
        self.max_retries = 3
        self.retry_delay = 1
        
        self.supported_coins = self._get_supported_coins()
        self.coin_map = self._create_coin_map()
    
    def _create_coin_map(self) -> Dict[str, str]:
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
            "OCEAN": "OCEANUSDT"
        }
    
    def _get_supported_coins(self) -> List[str]:
        return list(self.coin_map.keys())
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                headers={"User-Agent": "CryptoPulseBot/3.0"}
            )
        return self._session
    
    async def close(self):
        if self._session:
            await self._session.close()
            self._session = None
    
    def _sign_request(self, params: Dict[str, Any]) -> Dict[str, str]:
        if not self.api_key or not self.secret_key:
            return {}
        
        sorted_params = sorted(params.items())
        query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
        
        signature = hmac.new(
            self.secret_key.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return {
            "X-COINEX-KEY": self.api_key,
            "X-COINEX-SIGN": signature
        }
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Dict[str, Any] = None,
        signed: bool = False
    ) -> Dict[str, Any]:
        now = time.time()
        self._rate_limiter["global"] = [t for t in self._rate_limiter["global"] if now - t < 60]
        if len(self._rate_limiter["global"]) >= 100:
            await asyncio.sleep(1)
        
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if signed:
            headers.update(self._sign_request(params or {}))
        
        session = await self._get_session()
        
        for attempt in range(self.max_retries):
            try:
                async with session.request(method, url, params=params, headers=headers) as response:
                    self._rate_limiter["global"].append(time.time())
                    data = await response.json()
                    
                    if data.get("code") == 0:
                        return data.get("data", {})
                    else:
                        error_msg = data.get("message", "Unknown error")
                        if "rate limit" in error_msg.lower():
                            await asyncio.sleep(2 ** attempt)
                            continue
                        return {"error": error_msg}
                        
            except Exception:
                if attempt == self.max_retries - 1:
                    return {"error": "Max retries exceeded"}
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
        
        return {"error": "Max retries exceeded"}
    
    # ==================== قیمت‌ها ====================
    
    async def get_ticker(self, symbol: str) -> Optional[MarketData]:
        if symbol not in self.coin_map:
            symbol = f"{symbol}USDT"
        
        cache_key = f"ticker_{symbol}"
        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            if (datetime.now() - timestamp).seconds < self._cache_ttl:
                return data
        
        result = await self._request("GET", "/market/ticker", {"market": symbol})
        
        if "error" in result:
            return None
        
        try:
            data = MarketData(
                symbol=symbol,
                price=float(result.get("last", 0)),
                change_24h=float(result.get("change", 0)),
                volume_24h=float(result.get("vol", 0)),
                high_24h=float(result.get("high", 0)),
                low_24h=float(result.get("low", 0)),
                open_24h=float(result.get("open", 0)),
                close_24h=float(result.get("last", 0)),
                bid=float(result.get("buy", 0)),
                ask=float(result.get("sell", 0)),
                spread=0,
                timestamp=datetime.now()
            )
            data.spread = data.ask - data.bid
            self._cache[cache_key] = (data, datetime.now())
            return data
        except:
            return None
    
    async def get_all_tickers(self) -> Dict[str, MarketData]:
        result = await self._request("GET", "/market/ticker/all")
        
        if "error" in result:
            return {}
        
        tickers = {}
        for symbol, data in result.items():
            try:
                if not symbol.endswith("USDT"):
                    continue
                tickers[symbol] = MarketData(
                    symbol=symbol,
                    price=float(data.get("last", 0)),
                    change_24h=float(data.get("change", 0)),
                    volume_24h=float(data.get("vol", 0)),
                    high_24h=float(data.get("high", 0)),
                    low_24h=float(data.get("low", 0)),
                    open_24h=float(data.get("open", 0)),
                    close_24h=float(data.get("last", 0)),
                    bid=float(data.get("buy", 0)),
                    ask=float(data.get("sell", 0)),
                    spread=0,
                    timestamp=datetime.now()
                )
                tickers[symbol].spread = tickers[symbol].ask - tickers[symbol].bid
            except:
                continue
        
        return tickers
    
    # ==================== تاریخچه قیمت ====================
    
    async def get_kline(
        self,
        symbol: str,
        interval: str = "4h",
        limit: int = 100
    ) -> Optional[pd.DataFrame]:
        if symbol not in self.coin_map:
            symbol = f"{symbol}USDT"
        
        cache_key = f"kline_{symbol}_{interval}_{limit}"
        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            if (datetime.now() - timestamp).seconds < 60:
                return data
        
        result = await self._request(
            "GET",
            "/market/kline",
            {
                "market": symbol,
                "type": interval,
                "limit": limit
            }
        )
        
        if "error" in result:
            return None
        
        try:
            df = pd.DataFrame(result, columns=[
                'timestamp', 'open', 'close', 'high', 'low', 'volume', 'amount'
            ])
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            df.set_index('timestamp', inplace=True)
            
            for col in ['open', 'close', 'high', 'low', 'volume', 'amount']:
                df[col] = df[col].astype(float)
            
            self._cache[cache_key] = (df, datetime.now())
            return df
        except:
            return None
    
    async def get_price_history(
        self,
        symbol: str,
        interval: str = "4h",
        limit: int = 100
    ) -> Optional[List[float]]:
        df = await self.get_kline(symbol, interval, limit)
        if df is not None and not df.empty:
            return df['close'].tolist()
        return None
    
    # ==================== کتاب سفارشات ====================
    
    async def get_order_book(self, symbol: str, limit: int = 10) -> Optional[OrderBook]:
        if symbol not in self.coin_map:
            symbol = f"{symbol}USDT"
        
        result = await self._request(
            "GET",
            "/market/depth",
            {"market": symbol, "limit": limit}
        )
        
        if "error" in result:
            return None
        
        try:
            return OrderBook(
                symbol=symbol,
                bids=[(float(b[0]), float(b[1])) for b in result.get("bids", [])],
                asks=[(float(a[0]), float(a[1])) for a in result.get("asks", [])],
                timestamp=datetime.now()
            )
        except:
            return None
    
    # ==================== سفارشات ====================
    
    async def place_order(
        self,
        symbol: str,
        side: OrderSide,
        type: OrderType,
        amount: float,
        price: float = None,
        stop_price: float = None
    ) -> Optional[OrderResult]:
        if symbol not in self.coin_map:
            symbol = f"{symbol}USDT"
        
        params = {
            "market": symbol,
            "side": side.value,
            "type": type.value,
            "amount": str(amount)
        }
        
        if price:
            params["price"] = str(price)
        if stop_price:
            params["stop_price"] = str(stop_price)
        
        result = await self._request("POST", "/order/limit", params, signed=True)
        
        if "error" in result:
            return None
        
        try:
            return OrderResult(
                order_id=result.get("id", ""),
                symbol=symbol,
                side=side,
                type=type,
                price=float(result.get("price", 0)),
                amount=float(result.get("amount", 0)),
                filled=float(result.get("deal_amount", 0)),
                status=OrderStatus(result.get("status", "pending")),
                fee=float(result.get("fee", 0)),
                fee_currency=result.get("fee_coin", "USDT"),
                timestamp=datetime.now()
            )
        except:
            return None
    
    async def cancel_order(self, order_id: str) -> bool:
        result = await self._request(
            "POST",
            "/order/cancel",
            {"id": order_id},
            signed=True
        )
        return "error" not in result
    
    async def get_order(self, order_id: str) -> Optional[OrderResult]:
        result = await self._request(
            "GET",
            "/order/status",
            {"id": order_id},
            signed=True
        )
        
        if "error" in result:
            return None
        
        try:
            return OrderResult(
                order_id=result.get("id", ""),
                symbol=result.get("market", ""),
                side=OrderSide(result.get("side", "buy")),
                type=OrderType(result.get("type", "limit")),
                price=float(result.get("price", 0)),
                amount=float(result.get("amount", 0)),
                filled=float(result.get("deal_amount", 0)),
                status=OrderStatus(result.get("status", "pending")),
                fee=float(result.get("fee", 0)),
                fee_currency=result.get("fee_coin", "USDT"),
                timestamp=datetime.now()
            )
        except:
            return None
    
    async def get_open_orders(self, symbol: str = None) -> List[OrderResult]:
        params = {}
        if symbol:
            params["market"] = symbol
        
        result = await self._request("GET", "/order/pending", params, signed=True)
        
        if "error" in result:
            return []
        
        orders = []
        for order in result.get("data", []):
            try:
                orders.append(OrderResult(
                    order_id=order.get("id", ""),
                    symbol=order.get("market", ""),
                    side=OrderSide(order.get("side", "buy")),
                    type=OrderType(order.get("type", "limit")),
                    price=float(order.get("price", 0)),
                    amount=float(order.get("amount", 0)),
                    filled=float(order.get("deal_amount", 0)),
                    status=OrderStatus(order.get("status", "pending")),
                    fee=float(order.get("fee", 0)),
                    fee_currency=order.get("fee_coin", "USDT"),
                    timestamp=datetime.now()
                ))
            except:
                continue
        
        return orders
    
    # ==================== موجودی ====================
    
    async def get_balance(self, coin: str = None) -> Dict[str, float]:
        result = await self._request("GET", "/balance/info", {}, signed=True)
        
        if "error" in result:
            return {}
        
        balances = {}
        for coin_name, data in result.get("data", {}).items():
            balances[coin_name] = float(data.get("available", 0))
        
        if coin and coin in balances:
            return {coin: balances[coin]}
        
        return balances
    
    # ==================== اندیکاتورهای تکنیکال ====================
    
    @staticmethod
    def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        # SMA
        df['sma_7'] = df['close'].rolling(window=7).mean()
        df['sma_25'] = df['close'].rolling(window=25).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['sma_99'] = df['close'].rolling(window=99).mean()
        df['sma_200'] = df['close'].rolling(window=200).mean()
        
        # EMA
        df['ema_9'] = df['close'].ewm(span=9, adjust=False).mean()
        df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema_21'] = df['close'].ewm(span=21, adjust=False).mean()
        df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
        df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['ema_200'] = df['close'].ewm(span=200, adjust=False).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        df['rsi_7'] = 100 - (100 / (1 + (gain.rolling(7).mean() / loss.rolling(7).mean())))
        df['rsi_21'] = 100 - (100 / (1 + (gain.rolling(21).mean() / loss.rolling(21).mean())))
        
        # MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        df['bb_width'] = df['bb_upper'] - df['bb_lower']
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # Stochastic
        low_14 = df['low'].rolling(window=14).min()
        high_14 = df['high'].rolling(window=14).max()
        df['stoch_k'] = 100 * ((df['close'] - low_14) / (high_14 - low_14))
        df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()
        
        # MFI
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        money_flow = typical_price * df['volume']
        positive_flow = money_flow.where(typical_price > typical_price.shift(), 0)
        negative_flow = money_flow.where(typical_price < typical_price.shift(), 0)
        df['mfi'] = 100 - (100 / (1 + (positive_flow.rolling(14).sum() / negative_flow.rolling(14).sum())))
        
        # ADX
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = tr.rolling(window=14).mean()
        
        # OBV
        df['obv'] = (df['volume'] * np.where(df['close'] > df['close'].shift(), 1, -1)).cumsum()
        
        # Williams %R
        df['williams_r'] = -100 * ((high_14 - df['close']) / (high_14 - low_14))
        
        # CCI
        tp = (df['high'] + df['low'] + df['close']) / 3
        sma_tp = tp.rolling(window=20).mean()
        mad = tp.rolling(window=20).apply(lambda x: np.mean(np.abs(x - np.mean(x))))
        df['cci'] = (tp - sma_tp) / (0.015 * mad)
        
        # Ichimoku
        df['tenkan_sen'] = (df['high'].rolling(9).max() + df['low'].rolling(9).min()) / 2
        df['kijun_sen'] = (df['high'].rolling(26).max() + df['low'].rolling(26).min()) / 2
        df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)
        df['senkou_span_b'] = ((df['high'].rolling(52).max() + df['low'].rolling(52).min()) / 2).shift(26)
        
        # HMA
        wma = df['close'].rolling(window=10).apply(lambda x: np.average(x, weights=range(1, len(x)+1)))
        df['hma'] = wma.rolling(window=7).apply(lambda x: np.average(x, weights=range(1, len(x)+1)))
        
        # Chandelier Exit
        df['ce_long'] = df['high'].rolling(22).max() - (df['atr'] * 3)
        df['ce_short'] = df['low'].rolling(22).min() + (df['atr'] * 3)
        
        # Keltner Channel
        df['kc_middle'] = df['close'].rolling(20).mean()
        kc_range = df['atr'] * 1.5
        df['kc_upper'] = df['kc_middle'] + kc_range
        df['kc_lower'] = df['kc_middle'] - kc_range
        
        return df
    
    # ==================== تحلیل سیگنال ====================
    
    @staticmethod
    def get_signal_analysis(df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty or len(df) < 50:
            return {'signal': 'hold', 'confidence': 0, 'reasons': ['داده‌های کافی نیست']}
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        signals = []
        confidence = 50
        reasons = []
        
        # SMA Analysis
        if latest['sma_7'] > latest['sma_25']:
            signals.append('buy')
            reasons.append('✅ SMA7 > SMA25 (روند صعودی کوتاه‌مدت)')
            confidence += 10
        else:
            signals.append('sell')
            reasons.append('❌ SMA7 < SMA25 (روند نزولی کوتاه‌مدت)')
            confidence -= 10
        
        if latest['sma_25'] > latest['sma_50']:
            reasons.append('✅ SMA25 > SMA50 (روند صعودی میان‌مدت)')
            confidence += 8
        else:
            reasons.append('❌ SMA25 < SMA50 (روند نزولی میان‌مدت)')
            confidence -= 8
        
        if latest['sma_50'] > latest['sma_200']:
            reasons.append('✅ SMA50 > SMA200 (روند صعودی بلندمدت)')
            confidence += 10
        else:
            reasons.append('❌ SMA50 < SMA200 (روند نزولی بلندمدت)')
            confidence -= 10
        
        # EMA Analysis
        if latest['ema_9'] > latest['ema_21']:
            reasons.append('✅ EMA9 > EMA21 (سیگنال خرید کوتاه‌مدت)')
            confidence += 5
        
        if latest['ema_12'] > latest['ema_26']:
            reasons.append('✅ EMA12 > EMA26 (سیگنال خرید)')
            confidence += 8
            if 'sell' in signals:
                signals.remove('sell')
            signals.append('buy')
        else:
            reasons.append('❌ EMA12 < EMA26 (سیگنال فروش)')
            confidence -= 8
            if 'buy' in signals:
                signals.remove('buy')
            signals.append('sell')
        
        # RSI Analysis
        rsi = latest['rsi']
        if rsi < 30:
            reasons.append(f'✅ RSI: {rsi:.1f} (اشباع فروش - سیگنال خرید قوی)')
            confidence += 15
            signals.append('buy')
        elif rsi < 40:
            reasons.append(f'✅ RSI: {rsi:.1f} (نزدیک اشباع فروش - سیگنال خرید)')
            confidence += 8
            signals.append('buy')
        elif rsi > 70:
            reasons.append(f'❌ RSI: {rsi:.1f} (اشباع خرید - سیگنال فروش قوی)')
            confidence -= 15
            signals.append('sell')
        elif rsi > 60:
            reasons.append(f'❌ RSI: {rsi:.1f} (نزدیک اشباع خرید - سیگنال فروش)')
            confidence -= 8
            signals.append('sell')
        else:
            reasons.append(f'➖ RSI: {rsi:.1f} (منطقه خنثی)')
        
        # MACD Analysis
        if latest['macd'] > latest['macd_signal']:
            reasons.append('✅ MACD > سیگنال (سیگنال خرید)')
            confidence += 10
            signals.append('buy')
        else:
            reasons.append('❌ MACD < سیگنال (سیگنال فروش)')
            confidence -= 10
            signals.append('sell')
        
        # Bollinger Bands
        bb_position = latest['bb_position']
        if bb_position < 0.1:
            reasons.append('✅ قیمت پایین‌تر از باند پایین (فرصت خرید عالی)')
            confidence += 15
            signals.append('buy')
        elif bb_position < 0.3:
            reasons.append('✅ قیمت نزدیک باند پایین (منطقه خرید)')
            confidence += 8
            signals.append('buy')
        elif bb_position > 0.9:
            reasons.append('❌ قیمت بالاتر از باند بالا (منطقه فروش)')
            confidence -= 15
            signals.append('sell')
        elif bb_position > 0.7:
            reasons.append('❌ قیمت نزدیک باند بالا (منطقه فروش)')
            confidence -= 8
            signals.append('sell')
        else:
            reasons.append(f'➖ قیمت در محدوده میانی باند ({bb_position:.2f})')
        
        # Stochastic
        if latest['stoch_k'] < 20 and prev['stoch_k'] < latest['stoch_k']:
            reasons.append('✅ Stochastic در اشباع فروش و در حال افزایش (خرید)')
            confidence += 10
            signals.append('buy')
        elif latest['stoch_k'] > 80 and prev['stoch_k'] > latest['stoch_k']:
            reasons.append('❌ Stochastic در اشباع خرید و در حال کاهش (فروش)')
            confidence -= 10
            signals.append('sell')
        
        # MFI
        if latest['mfi'] < 20:
            reasons.append(f'✅ MFI: {latest["mfi"]:.1f} (اشباع فروش - خرید)')
            confidence += 10
            signals.append('buy')
        elif latest['mfi'] > 80:
            reasons.append(f'❌ MFI: {latest["mfi"]:.1f} (اشباع خرید - فروش)')
            confidence -= 10
            signals.append('sell')
        
        # CCI
        if latest['cci'] < -100:
            reasons.append(f'✅ CCI: {latest["cci"]:.1f} (اشباع فروش)')
            confidence += 8
            signals.append('buy')
        elif latest['cci'] > 100:
            reasons.append(f'❌ CCI: {latest["cci"]:.1f} (اشباع خرید)')
            confidence -= 8
            signals.append('sell')
        
        # Williams %R
        if latest['williams_r'] < -80:
            reasons.append(f'✅ Williams %R: {latest["williams_r"]:.1f} (اشباع فروش)')
            confidence += 8
            signals.append('buy')
        elif latest['williams_r'] > -20:
            reasons.append(f'❌ Williams %R: {latest["williams_r"]:.1f} (اشباع خرید)')
            confidence -= 8
            signals.append('sell')
        
        # ADX
        if latest['adx'] > 25:
            reasons.append(f'✅ ADX: {latest["adx"]:.1f} (روند قوی)')
            confidence += 5
        else:
            reasons.append(f'➖ ADX: {latest["adx"]:.1f} (روند ضعیف)')
        
        # Ichimoku
        if latest['close'] > latest['senkou_span_a'] and latest['close'] > latest['senkou_span_b']:
            reasons.append('✅ قیمت بالای ابر ایچیموکو (روند صعودی)')
            confidence += 8
            signals.append('buy')
        elif latest['close'] < latest['senkou_span_a'] and latest['close'] < latest['senkou_span_b']:
            reasons.append('❌ قیمت پایین ابر ایچیموکو (روند نزولی)')
            confidence -= 8
            signals.append('sell')
        
        # Chandelier Exit
        if latest['close'] > latest['ce_long']:
            reasons.append('✅ قیمت بالای CE Long (سیگنال خرید)')
            confidence += 5
            signals.append('buy')
        elif latest['close'] < latest['ce_short']:
            reasons.append('❌ قیمت پایین CE Short (سیگنال فروش)')
            confidence -= 5
            signals.append('sell')
        
        # تصمیم نهایی
        buy_count = signals.count('buy')
        sell_count = signals.count('sell')
        
        if buy_count > sell_count:
            final_signal = 'buy'
        elif sell_count > buy_count:
            final_signal = 'sell'
        else:
            final_signal = 'hold'
        
        confidence = max(0, min(100, confidence))
        
        # سطوح حمایت و مقاومت
        recent_high = df['high'].rolling(20).max()
        recent_low = df['low'].rolling(20).min()
        
        support = recent_low.iloc[-1]
        resistance = recent_high.iloc[-1]
        
        # اهداف
        current_price = latest['close']
        targets = []
        
        if final_signal == 'buy':
            target1 = current_price * 1.02
            target2 = current_price * 1.05
            target3 = current_price * 1.10
            stop_loss = current_price * 0.97
        elif final_signal == 'sell':
            target1 = current_price * 0.98
            target2 = current_price * 0.95
            target3 = current_price * 0.90
            stop_loss = current_price * 1.03
        else:
            target1 = current_price
            target2 = current_price
            target3 = current_price
            stop_loss = current_price
        
        return {
            'signal': final_signal,
            'confidence': confidence,
            'reasons': reasons,
            'current_price': current_price,
            'support': support,
            'resistance': resistance,
            'targets': [target1, target2, target3],
            'stop_loss': stop_loss,
            'rsi': latest['rsi'],
            'macd': latest['macd'],
            'macd_signal': latest['macd_signal'],
            'bb_position': latest['bb_position'],
            'adx': latest['adx'],
            'buy_signals': buy_count,
            'sell_signals': sell_count,
            'total_indicators': len(reasons)
        }
    
    # ==================== تحلیل چند تایم‌فریم ====================
    
    async def analyze_multi_timeframe(
        self,
        symbol: str,
        timeframes: List[str] = None
    ) -> Dict[str, Any]:
        if timeframes is None:
            timeframes = ['1h', '4h', '1d', '1w']
        
        analysis = {
            'symbol': symbol,
            'timeframes': {},
            'overall_signal': 'hold',
            'overall_confidence': 0
        }
        
        signals = []
        confidences = []
        
        for tf in timeframes:
            df = await self.get_kline(symbol, tf, 200)
            if df is not None and not df.empty:
                result = self.get_signal_analysis(df)
                analysis['timeframes'][tf] = result
                signals.append(result['signal'])
                confidences.append(result['confidence'])
        
        buy_count = signals.count('buy')
        sell_count = signals.count('sell')
        
        if buy_count > sell_count:
            analysis['overall_signal'] = 'buy'
        elif sell_count > buy_count:
            analysis['overall_signal'] = 'sell'
        else:
            analysis['overall_signal'] = 'hold'
        
        if confidences:
            analysis['overall_confidence'] = int(sum(confidences) / len(confidences))
        
        return analysis
    
    # ==================== تحلیل فاندامنتال ====================
    
    @staticmethod
    def fundamental_analysis(coin: str, market_data: MarketData) -> Dict[str, Any]:
        analysis = {
            'coin': coin,
            'score': 0,
            'signals': [],
            'reasons': []
        }
        
        if market_data.volume_24h > 1_000_000:
            analysis['score'] += 20
            analysis['reasons'].append('✅ حجم معاملات بالا (نقدینگی خوب)')
        elif market_data.volume_24h > 100_000:
            analysis['score'] += 10
            analysis['reasons'].append('➖ حجم معاملات متوسط')
        else:
            analysis['score'] -= 10
            analysis['reasons'].append('❌ حجم معاملات پایین')
        
        if market_data.change_24h > 5:
            analysis['score'] += 15
            analysis['reasons'].append('✅ رشد قیمتی قوی (۵%+)')
        elif market_data.change_24h > 2:
            analysis['score'] += 10
            analysis['reasons'].append('✅ رشد قیمتی مثبت')
        elif market_data.change_24h > -2:
            analysis['score'] += 0
            analysis['reasons'].append('➖ قیمت تقریباً ثابت')
        elif market_data.change_24h > -5:
            analysis['score'] -= 10
            analysis['reasons'].append('❌ افت قیمتی')
        else:
            analysis['score'] -= 15
            analysis['reasons'].append('❌ افت قیمتی شدید (۵%-)')
        
        if market_data.price > market_data.high_24h * 0.9:
            analysis['score'] += 10
            analysis['reasons'].append('✅ قیمت نزدیک به بالاترین ۲۴ ساعت')
        elif market_data.price < market_data.low_24h * 1.1:
            analysis['score'] -= 10
            analysis['reasons'].append('❌ قیمت نزدیک به پایین‌ترین ۲۴ ساعت')
        
        if market_data.spread / market_data.price < 0.001:
            analysis['score'] += 10
            analysis['reasons'].append('✅ اسپرد بسیار کم (نقدشوندگی عالی)')
        elif market_data.spread / market_data.price < 0.002:
            analysis['score'] += 5
            analysis['reasons'].append('➖ اسپرد مناسب')
        else:
            analysis['score'] -= 10
            analysis['reasons'].append('❌ اسپرد بالا')
        
        if analysis['score'] >= 50:
            analysis['level'] = 'قوی (خرید)'
            analysis['signals'].append('buy')
        elif analysis['score'] >= 30:
            analysis['level'] = 'متوسط (خرید ملایم)'
            analysis['signals'].append('buy')
        elif analysis['score'] >= 10:
            analysis['level'] = 'خنثی (نگهداری)'
            analysis['signals'].append('hold')
        elif analysis['score'] >= -10:
            analysis['level'] = 'خنثی (نگهداری)'
            analysis['signals'].append('hold')
        elif analysis['score'] >= -30:
            analysis['level'] = 'متوسط (فروش ملایم)'
            analysis['signals'].append('sell')
        else:
            analysis['level'] = 'قوی (فروش)'
            analysis['signals'].append('sell')
        
        return analysis

# ==================== کلاس مدیریت بازار ====================

class MarketManager:
    def __init__(self):
        from bot2 import get_config
        config = get_config()
        
        self.coinex = CoinExExchange(
            api_key=config.get('coinex_api_key', ''),
            secret_key=config.get('coinex_secret_key', ''),
            base_url=config.get('coinex_base_url', 'https://api.coinex.com/v1')
        )
        
        self._cache = {}
        self._cache_ttl = 30
    
    async def get_price(self, symbol: str) -> Optional[float]:
        ticker = await self.coinex.get_ticker(symbol)
        if ticker:
            return ticker.price
        return None
    
    async def get_all_prices(self) -> Dict[str, float]:
        tickers = await self.coinex.get_all_tickers()
        return {k: v.price for k, v in tickers.items()}
    
    async def get_market_data(self, symbol: str) -> Optional[MarketData]:
        return await self.coinex.get_ticker(symbol)
    
    async def get_historical_data(
        self,
        symbol: str,
        timeframe: str = "4h",
        limit: int = 100
    ) -> Optional[pd.DataFrame]:
        return await self.coinex.get_kline(symbol, timeframe, limit)
    
    async def get_signal(
        self,
        symbol: str,
        timeframe: str = "4h"
    ) -> Dict[str, Any]:
        df = await self.coinex.get_kline(symbol, timeframe, 200)
        if df is None or df.empty:
            return {
                'signal': 'hold',
                'confidence': 0,
                'error': 'خطا در دریافت داده'
            }
        
        df = self.coinex.calculate_indicators(df)
        technical = self.coinex.get_signal_analysis(df)
        
        ticker = await self.coinex.get_ticker(symbol)
        fundamental = {}
        if ticker:
            fundamental = self.coinex.fundamental_analysis(symbol, ticker)
        
        signal_weights = {'buy': 0, 'sell': 0, 'hold': 0}
        
        if technical['signal'] == 'buy':
            signal_weights['buy'] += technical['confidence'] * 1.0
        elif technical['signal'] == 'sell':
            signal_weights['sell'] += technical['confidence'] * 1.0
        else:
            signal_weights['hold'] += technical['confidence'] * 0.5
        
        if fundamental.get('signals'):
            for sig in fundamental['signals']:
                if sig == 'buy':
                    signal_weights['buy'] += 20
                elif sig == 'sell':
                    signal_weights['sell'] += 20
        
        final_signal = max(signal_weights, key=signal_weights.get)
        max_weight = signal_weights[final_signal]
        
        total_weight = sum(signal_weights.values())
        if total_weight > 0:
            confidence = int((max_weight / total_weight) * 100)
        else:
            confidence = 50
        
        confidence = max(0, min(100, confidence))
        
        return {
            'signal': final_signal,
            'confidence': confidence,
            'technical': technical,
            'fundamental': fundamental,
            'weights': signal_weights,
            'timeframe': timeframe,
            'symbol': symbol
        }
    
    async def get_multi_timeframe_signal(self, symbol: str) -> Dict[str, Any]:
        return await self.coinex.analyze_multi_timeframe(
            symbol,
            ['1h', '4h', '1d', '1w']
        )
    
    async def close(self):
        await self.coinex.close()

# ==================== Export ====================

import sys
import os

class SafeMarketInstance:
    """ایمن‌ساز ایجاد نمونه از کلاس‌های بازار"""
    
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

# ۱. MarketManager - اصلی‌ترین
market_manager = SafeMarketInstance.create(
    "MarketManager",
    api_key=os.environ.get("COINEX_API_KEY", ""),
    secret_key=os.environ.get("COINEX_SECRET_KEY", "")
)

# ۲. CoinExExchange - از داخل MarketManager گرفته میشود
def get_coinex_instance():
    """دریافت نمونه CoinExExchange از داخل MarketManager"""
    if market_manager and hasattr(market_manager, 'coinex'):
        return market_manager.coinex
    return None

# ==================== توابع دسترسی ====================

def get_market():
    """دریافت نمونه MarketManager"""
    return market_manager

def get_coinex():
    """دریافت نمونه CoinExExchange"""
    return get_coinex_instance()

# ==================== تابع کمکی برای دیباگ ====================

def check_market_instances():
    """بررسی سلامت نمونه‌های بازار"""
    result = {
        "market_manager": "✅ OK" if market_manager else "❌ FAILED",
        "coinex": "✅ OK" if get_coinex() else "❌ FAILED"
    }
    return result
