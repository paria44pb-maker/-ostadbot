# ═══════════════════════════════════════════════════════════
# PART 2: AI ENGINE, COINEX EXCHANGE, TECHNICAL ANALYSIS
# ═══════════════════════════════════════════════════════════

from typing import Optional, Dict, Any, List, Tuple
from collections import OrderedDict, deque
from part1 import *

# ════════════════════════════════════════
# GROQ AI ENGINE (ADVANCED)
# ════════════════════════════════════════
class GroqAIEngine:
    """Advanced Groq AI with caching and rate limiting"""
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key or cfg.GROQ_API_KEY
        self.client = None
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
                logger.info("Groq AI initialized")
            except Exception as e:
                logger.error(f"Groq init error: {e}")
        
        self._request_times = deque(maxlen=100)
        self._daily_tokens = 0
        self._daily_reset = ""
        self._response_cache = OrderedDict()
        self._cache_max_size = 200
        self._total_requests = 0
        self._total_errors = 0
        self._system_prompts = self._build_prompts()
    
    def _build_prompts(self) -> Dict[str, str]:
        return {
            "default": """شما یک دستیار حرفه‌ای تحلیل بازار کریپتو به زبان فارسی هستید.
تحلیل دقیق، عملی و با ذکر ریسک بدهید. از شکلک استفاده کنید. وعده سود ندهید.""",
            "technical": """شما یک تحلیلگر تکنیکال حرفه‌ای هستید.
RSI، MACD، بولینگر، فیبوناچی، حمایت/مقاومت، روند و حجم را تحلیل کن.""",
            "signal": """شما یک سیگنال‌دهنده حرفه‌ای هستید.
سیگنال باید شامل: جهت معامله، قیمت ورود، حد ضرر، اهداف، اطمینان و نسبت ریسک به ریوارد باشد.""",
        }
    
    def _get_cache_key(self, prompt: str, system_type: str) -> str:
        content = f"{system_type}:{prompt}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _check_rate_limit(self) -> bool:
        now = time.time()
        while self._request_times and now - self._request_times[0] >= 60:
            self._request_times.popleft()
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        if today != self._daily_reset:
            self._daily_tokens = 0
            self._daily_reset = today
        return len(self._request_times) < cfg.GROQ_RPM
    
    async def ask(self, prompt: str, context: str = "", system_type: str = "default",
                 temperature: float = 0.3, max_tokens: int = 1024, use_cache: bool = True) -> str:
        if not self.client:
            return "❌ کلید API تنظیم نشده است."
        
        cache_key = self._get_cache_key(prompt, system_type)
        if use_cache and cache_key in self._response_cache:
            return self._response_cache[cache_key]
        
        if not self._check_rate_limit():
            await asyncio.sleep(2)
        
        system_prompt = self._system_prompts.get(system_type, self._system_prompts["default"])
        messages = [{"role": "system", "content": system_prompt}]
        if context:
            messages.append({"role": "system", "content": f"اطلاعات بازار:\n{context}"})
        messages.append({"role": "user", "content": prompt})
        
        self._total_requests += 1
        
        for attempt in range(3):
            try:
                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(None, lambda: self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile", messages=messages,
                    temperature=temperature, max_tokens=max_tokens, top_p=0.9
                ))
                self._request_times.append(time.time())
                if response.usage:
                    self._daily_tokens += response.usage.total_tokens
                answer = response.choices[0].message.content.strip()
                if use_cache:
                    if len(self._response_cache) >= self._cache_max_size:
                        self._response_cache.popitem(last=False)
                    self._response_cache[cache_key] = answer
                return answer
            except GroqRateLimitError:
                if attempt < 2:
                    await asyncio.sleep((attempt + 1) * 3)
                    continue
                return "⏳ سیستم مشغول است."
            except Exception as e:
                self._total_errors += 1
                if attempt < 2:
                    await asyncio.sleep(2)
                    continue
                return f"⚠️ خطا: {str(e)[:100]}"
        return "⚠️ پاسخی دریافت نشد."
    
    async def analyze_technically(self, symbol: str, market_data: str = "") -> str:
        return await self.ask(f"تحلیل تکنیکال کامل برای {symbol}", market_data, "technical")
    
    async def generate_signal(self, symbol: str, market_data: str = "") -> str:
        return await self.ask(f"سیگنال معاملاتی برای {symbol}", market_data, "signal")
    
    def clear_cache(self):
        self._response_cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "provider": "Groq", "model": "llama-3.3-70b-versatile",
            "requests_minute": len(self._request_times), "tokens_today": self._daily_tokens,
            "cache_size": len(self._response_cache), "total_requests": self._total_requests,
            "total_errors": self._total_errors, "status": "active" if self.client else "inactive"
        }

ai = GroqAIEngine()


# ════════════════════════════════════════
# COINEX EXCHANGE CLIENT - COMPLETE
# ════════════════════════════════════════
class CoinExClient:
    """
    Complete CoinEx exchange API client.
    Supports: tickers, klines, orderbook, multi-symbol fetch, caching.
    """
    
    BASE_URL = "https://api.coinex.com/v2"
    
    def __init__(self):
        self._session = None
        self._request_count = 0
        self._error_count = 0
        self._last_request_time = 0
        self._cache = {}
        self._cache_ttl = 30
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            headers = {"User-Agent": f"OstadBot/{cfg.APP_VERSION}", "Accept": "application/json"}
            self._session = aiohttp.ClientSession(timeout=timeout, headers=headers)
        return self._session
    
    async def _rate_limit(self):
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < 0.1:
            await asyncio.sleep(0.1 - elapsed)
        self._last_request_time = time.time()
    
    async def _make_request(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        await self._rate_limit()
        cache_key = f"{endpoint}:{json.dumps(params or {})}"
        if cache_key in self._cache and time.time() - self._cache[cache_key]['time'] < self._cache_ttl:
            return self._cache[cache_key]['data']
        
        url = f"{self.BASE_URL}{endpoint}"
        for attempt in range(2):
            try:
                session = await self._get_session()
                async with session.get(url, params=params) as response:
                    self._request_count += 1
                    if response.status == 200:
                        data = await response.json()
                        if data.get("code") == 0:
                            self._cache[cache_key] = {'data': data, 'time': time.time()}
                            return data
                        return {"code": -1, "message": data.get("message", "Error")}
                    if attempt < 1:
                        await asyncio.sleep(0.5)
                        continue
                    return {"code": -1, "message": f"HTTP {response.status}"}
            except asyncio.TimeoutError:
                self._error_count += 1
                if attempt < 1: continue
                return {"code": -1, "message": "Timeout"}
            except Exception as e:
                self._error_count += 1
                return {"code": -1, "message": str(e)}
        return {"code": -1, "message": "Max retries"}
    
    async def get_ticker(self, symbol: str = "BTCUSDT") -> Dict[str, Any]:
        result = await self._make_request("/spot/ticker", {"market": symbol.upper()})
        if result.get("code") == 0:
            data = result.get("data", {})
            if isinstance(data, list) and len(data) > 0:
                return data[0]
            elif isinstance(data, dict):
                return data
        return {}
    
    async def get_klines(self, symbol: str = "BTCUSDT", period: str = "1hour", limit: int = 100) -> List[Dict]:
        result = await self._make_request("/spot/kline", {
            "market": symbol.upper(), "period": period, "limit": str(limit)
        })
        return result.get("data", []) if result.get("code") == 0 else []
    
    async def get_orderbook(self, symbol: str = "BTCUSDT", limit: int = 20) -> Dict:
        result = await self._make_request("/spot/depth", {
            "market": symbol.upper(), "limit": str(limit), "interval": "0"
        })
        return result.get("data", {}) if result.get("code") == 0 else {}
    
    async def get_price(self, symbol: str) -> float:
        try:
            ticker = await self.get_ticker(symbol)
            if ticker:
                price = float(ticker.get("last", 0))
                if price > 0: return price
        except: pass
        return 0.0
    
    async def get_24h_change(self, symbol: str) -> float:
        try:
            ticker = await self.get_ticker(symbol)
            if ticker: return float(ticker.get("change_percentage", 0))
        except: pass
        return 0.0
    
    async def get_multiple_tickers(self, symbols: List[str]) -> Dict[str, Dict]:
        if not symbols: return {}
        tasks = [self.get_ticker(s) for s in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        tickers = {}
        for sym, result in zip(symbols, results):
            if isinstance(result, dict) and result: tickers[sym] = result
        return tickers
    
    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
        self._cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_requests": self._request_count,
            "total_errors": self._error_count,
            "cache_size": len(self._cache),
            "session_active": self._session is not None and not self._session.closed,
        }

exchange = CoinExClient()


# ════════════════════════════════════════
# TECHNICAL ANALYSIS ENGINE - COMPLETE
# ════════════════════════════════════════
class TechnicalAnalyzer:
    """
    Complete technical analysis engine.
    Supports: RSI, MACD, Bollinger, Fibonacci, Moving Averages,
    ATR, Stochastic RSI, Ichimoku, Price Action, Market Structure,
    Volume Profile, Trend Detection, Support/Resistance.
    """
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        if len(prices) < period + 1: return 50.0
        deltas = np.diff(prices)
        gains = np.maximum(deltas, 0)
        losses = np.maximum(-deltas, 0)
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        if avg_loss == 0: return 100.0
        for i in range(period, len(deltas)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        rs = avg_gain / avg_loss if avg_loss > 0 else 0
        return float(np.clip(100 - 100 / (1 + rs), 0, 100))
    
    @staticmethod
    def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float, float]:
        if len(prices) < slow + signal: return (0.0, 0.0, 0.0)
        def ema(data, period):
            if len(data) < period: return sum(data)/len(data) if data else 0
            m = 2/(period+1)
            e = sum(data[:period])/period
            for x in data[period:]: e = (x-e)*m + e
            return e
        ema_fast = ema(prices, fast)
        ema_slow = ema(prices, slow)
        macd_line = ema_fast - ema_slow
        macd_values = []
        for i in range(slow-1, len(prices)):
            macd_values.append(ema(prices[:i+1], fast) - ema(prices[:i+1], slow))
        signal_line = ema(macd_values, signal) if len(macd_values) >= signal else macd_line * 0.9
        histogram = macd_line - signal_line
        return (float(macd_line), float(signal_line), float(histogram))
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2.0) -> Tuple[float, float, float]:
        if len(prices) < period: return (0.0, 0.0, 0.0)
        recent = np.array(prices[-period:])
        middle = float(np.mean(recent))
        std = float(np.std(recent))
        return (middle + std * std_dev, middle, middle - std * std_dev)
    
    @staticmethod
    def calculate_moving_averages(prices: List[float]) -> Dict[str, float]:
        if not prices: return {}
        def sma(data, period):
            if len(data) < period: return sum(data)/len(data) if data else 0
            return sum(data[-period:])/period
        return {"MA5": sma(prices,5), "MA10": sma(prices,10), "MA20": sma(prices,20),
                "MA50": sma(prices,50), "MA100": sma(prices,100), "MA200": sma(prices,200)}
    
    @staticmethod
    def calculate_ema(prices: List[float], period: int = 20) -> float:
        if not prices or len(prices) < period: return prices[-1] if prices else 0
        m = 2/(period+1)
        e = sum(prices[:period])/period
        for x in prices[period:]: e = (x-e)*m + e
        return e
    
    @staticmethod
    def calculate_atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
        if len(highs) < period + 1: return 0.0
        tr_values = []
        for i in range(1, len(highs)):
            tr = max(highs[i]-lows[i], abs(highs[i]-closes[i-1]), abs(lows[i]-closes[i-1]))
            tr_values.append(tr)
        if not tr_values: return 0.0
        atr = sum(tr_values[:period])/period
        for i in range(period, len(tr_values)):
            atr = (atr*(period-1)+tr_values[i])/period
        return float(atr)
    
    @staticmethod
    def calculate_stochastic_rsi(prices: List[float], period: int = 14) -> Tuple[float, float]:
        if len(prices) < period + 3: return (50.0, 50.0)
        rsi_values = []
        for i in range(period, len(prices)):
            sub = prices[i-period+1:i+1]
            deltas = np.diff(sub)
            gains = np.maximum(deltas, 0)
            losses = np.maximum(-deltas, 0)
            avg_gain = np.mean(gains) if len(gains) > 0 else 0
            avg_loss = np.mean(losses) if len(losses) > 0 else 0.0001
            rs = avg_gain / avg_loss
            rsi = 100 - 100/(1+rs)
            rsi_values.append(rsi)
        if len(rsi_values) < period: return (50.0, 50.0)
        recent_rsi = rsi_values[-period:]
        min_rsi, max_rsi = min(recent_rsi), max(recent_rsi)
        if max_rsi == min_rsi: return (50.0, 50.0)
        stoch_k = ((rsi_values[-1] - min_rsi) / (max_rsi - min_rsi)) * 100
        stoch_d = sum(rsi_values[-3:]) / 3 if len(rsi_values) >= 3 else stoch_k
        return (float(stoch_k), float(stoch_d))
    
    @staticmethod
    def calculate_support_resistance(prices: List[float], window: int = 20) -> Tuple[float, float]:
        if len(prices) < window: return (min(prices) if prices else 0, max(prices) if prices else 0)
        recent = prices[-window:]
        return (float(min(recent)), float(max(recent)))
    
    @staticmethod
    def calculate_fibonacci(high: float, low: float) -> Dict[str, float]:
        diff = high - low
        levels = {"0%": 0, "23.6%": 0.236, "38.2%": 0.382, "50%": 0.5,
                  "61.8%": 0.618, "78.6%": 0.786, "100%": 1.0,
                  "127.2%": 1.272, "161.8%": 1.618, "261.8%": 2.618}
        if diff > 0: return {n: low + diff*r for n, r in levels.items()}
        return {n: high - abs(diff)*r for n, r in levels.items()}
    
    @staticmethod
    def detect_trend(prices: List[float], short: int = 10, long: int = 30) -> str:
        if len(prices) < long: return "خنثی ⚪"
        short_ma = np.mean(prices[-short:])
        long_ma = np.mean(prices[-long:])
        diff_pct = ((short_ma - long_ma) / long_ma) * 100
        if diff_pct > 3: return "صعودی قوی 🟢🟢"
        if diff_pct > 1: return "صعودی 🟢"
        if diff_pct > -1: return "خنثی ⚪"
        if diff_pct > -3: return "نزولی 🔴"
        return "نزولی قوی 🔴🔴"
    
    @staticmethod
    def analyze_volume(volumes: List[float], prices: List[float]) -> Dict[str, Any]:
        if len(volumes) < 20: return {"avg": 0, "ratio": 1, "trend": "نرمال", "signal": "خنثی"}
        avg_vol = float(np.mean(volumes[-20:]))
        current_vol = volumes[-1]
        vol_ratio = current_vol / avg_vol if avg_vol > 0 else 1
        if vol_ratio > 2:
            signal = "خرید قوی 🔥🔥🔥" if prices and prices[-1] > prices[-2] else "فروش قوی 🔥🔥🔥"
            trend = "حجم بسیار بالا"
        elif vol_ratio > 1.5: signal, trend = "فعال 🔥", "حجم بالا"
        elif vol_ratio < 0.5: signal, trend = "نوسان کم 💤", "حجم پایین"
        else: signal, trend = "خنثی 📊", "حجم نرمال"
        return {"avg": avg_vol, "ratio": round(vol_ratio, 2), "trend": trend, "signal": signal}
    
    @staticmethod
    def market_structure(highs: List[float], lows: List[float]) -> Dict[str, str]:
        if len(highs) < 4 or len(lows) < 4: return {"structure": "نامشخص", "bias": "خنثی"}
        lh, ph = highs[-1], highs[-3]
        ll, pl = lows[-1], lows[-3]
        if lh > ph and ll > pl: return {"structure": "HH + HL", "bias": "صعودی 🟢"}
        if lh < ph and ll < pl: return {"structure": "LH + LL", "bias": "نزولی 🔴"}
        if lh > ph and ll < pl: return {"structure": "HH + LL", "bias": "احتمال شکست ⚡"}
        return {"structure": "مختلط", "bias": "خنثی ⚪"}
    
    @staticmethod
    def calculate_ichimoku(highs: List[float], lows: List[float]) -> Dict[str, float]:
        if len(highs) < 52 or len(lows) < 52: return {"tenkan": 0, "kijun": 0, "senkou_a": 0, "senkou_b": 0}
        tenkan = (max(highs[-9:]) + min(lows[-9:])) / 2
        kijun = (max(highs[-26:]) + min(lows[-26:])) / 2
        senkou_a = (tenkan + kijun) / 2
        senkou_b = (max(highs[-52:]) + min(lows[-52:])) / 2
        return {"tenkan": float(tenkan), "kijun": float(kijun), "senkou_a": float(senkou_a), "senkou_b": float(senkou_b)}
    
    @staticmethod
    def generate_signal_from_analysis(symbol: str, price: float, rsi: float, macd_line: float,
                                      macd_signal: float, trend: str, support: float,
                                      resistance: float, volume_signal: str) -> Dict[str, Any]:
        """Generate trading signal based on technical analysis"""
        signal = {"symbol": symbol, "direction": "NEUTRAL", "confidence": 0.0,
                  "entry": price, "stop_loss": 0, "take_profit": 0, "reasons": []}
        
        reasons = []
        bullish_score = 0
        bearish_score = 0
        
        # RSI analysis
        if rsi < 30:
            bullish_score += 2
            reasons.append("RSI در ناحیه اشباع فروش")
        elif rsi > 70:
            bearish_score += 2
            reasons.append("RSI در ناحیه اشباع خرید")
        elif rsi > 50:
            bullish_score += 1
        else:
            bearish_score += 1
        
        # MACD analysis
        if macd_line > macd_signal:
            bullish_score += 2
            reasons.append("MACD بالای خط سیگنال")
        else:
            bearish_score += 2
            reasons.append("MACD پایین خط سیگنال")
        
        # Trend analysis
        if "صعودی" in trend:
            bullish_score += 3
            reasons.append(f"روند {trend}")
        elif "نزولی" in trend:
            bearish_score += 3
            reasons.append(f"روند {trend}")
        
        # Volume analysis
        if "خرید" in volume_signal:
            bullish_score += 2
            reasons.append("حجم خرید بالا")
        elif "فروش" in volume_signal:
            bearish_score += 2
            reasons.append("حجم فروش بالا")
        
        # Price position
        price_range = resistance - support
        if price_range > 0:
            price_position = (price - support) / price_range
            if price_position < 0.3:
                bullish_score += 2
                reasons.append("قیمت نزدیک حمایت")
            elif price_position > 0.7:
                bearish_score += 2
                reasons.append("قیمت نزدیک مقاومت")
        
        # Final decision
        if bullish_score > bearish_score:
            signal["direction"] = "LONG"
            signal["confidence"] = min(0.9, bullish_score / (bullish_score + bearish_score))
            signal["stop_loss"] = support * 0.99
            signal["take_profit"] = resistance
        elif bearish_score > bullish_score:
            signal["direction"] = "SHORT"
            signal["confidence"] = min(0.9, bearish_score / (bullish_score + bearish_score))
            signal["stop_loss"] = resistance * 1.01
            signal["take_profit"] = support
        else:
            signal["direction"] = "NEUTRAL"
            signal["confidence"] = 0.3
        
        signal["reasons"] = reasons
        return signal

ta = TechnicalAnalyzer()

# ════════════════════════════════════════
# END OF PART 2
# ════════════════════════════════════════
