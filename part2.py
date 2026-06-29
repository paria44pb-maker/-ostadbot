from part1 import *
from typing import Optional, Dict, Any, List, Tuple
# ═══════════════════════════════════════════════════════════
# PART 2: AI ENGINE, EXCHANGE CLIENT, TECHNICAL ANALYSIS
# ═══════════════════════════════════════════════════════════

# ════════════════════════════════════════
# GROQ AI ENGINE (ADVANCED)
# ════════════════════════════════════════
class GroqAIEngine:
    """
    Advanced Groq AI integration with:
    - Rate limiting & exponential backoff
    - Response caching with LRU eviction
    - Multiple system prompt templates
    - Token tracking and statistics
    - Comprehensive error recovery
    """
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key or cfg.GROQ_API_KEY
        self.client = None
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
                logger.info("Groq AI client initialized")
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
        """Build comprehensive system prompts for different analysis types"""
        return {
            "default": """شما یک دستیار حرفه‌ای تحلیل بازار کریپتو به زبان فارسی هستید.

قوانین پاسخگویی:
۱. همیشه به فارسی روان و حرفه‌ای پاسخ بدهید
۲. از شکلک‌های مناسب استفاده کنید
۳. تحلیل دقیق، عملی و بدون حاشیه بدهید
۴. حد ضرر و حد سود را مشخص کنید
۵. ریسک‌ها را شفاف بیان کنید
۶. هرگز وعده سود قطعی ندهید
۷. همیشه یادآوری کنید که این تحلیل شخصی است
۸. از اعداد و ارقام دقیق استفاده کنید
۹. روند کلی بازار را در نظر بگیرید
۱۰. به اخبار و رویدادهای مهم اشاره کنید""",
            
            "technical": """شما یک تحلیلگر تکنیکال حرفه‌ای بازار کریپتو هستید.

تحلیل شما باید شامل:
۱. وضعیت RSI و تفسیر آن
۲. وضعیت MACD و سیگنال‌های آن
۳. سطوح حمایت و مقاومت کلیدی
۴. سطوح فیبوناچی مهم
۵. الگوهای کندل استیک
۶. روند کلی بازار (صعودی/نزولی/خنثی)
۷. تحلیل حجم معاملات
۸. پیش‌بینی حرکت بعدی قیمت
۹. نقاط ورود و خروج پیشنهادی
۱۰. حد ضرر منطقی""",
            
            "signal": """شما یک سیگنال‌دهنده حرفه‌ای کریپتو هستید.

سیگنال باید شامل:
۱. جهت معامله (LONG/SHORT)
۲. قیمت ورود دقیق
۳. حد ضرر
۴. اهداف قیمتی (حداقل ۳ سطح)
۵. میزان اطمینان (درصد)
۶. نسبت ریسک به ریوارد
۷. تایم‌فریم پیشنهادی
۸. دلیل صدور سیگنال""",
            
            "risk": """شما یک مدیر ریسک حرفه‌ای هستید.

تحلیل ریسک باید شامل:
۱. میزان ریسک معامله (کم/متوسط/زیاد)
۲. حداکثر سرمایه پیشنهادی
۳. نسبت ریسک به ریوارد
۴. احتمال موفقیت
۵. عوامل تاثیرگذار بر ریسک
۶. توصیه‌های مدیریت سرمایه""",
            
            "news": """شما یک تحلیلگر اخبار کریپتو هستید.

تحلیل خبر باید شامل:
۱. خلاصه خبر
۲. تاثیر بر بازار (مثبت/منفی/خنثی)
۳. میزان اهمیت (کم/متوسط/زیاد)
۴. ارزهای متاثر
۵. پیش‌بینی واکنش بازار""",
        }
    
    def _get_cache_key(self, prompt: str, system_type: str) -> str:
        """Generate cache key for a prompt"""
        content = f"{system_type}:{prompt}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        now = time.time()
        while self._request_times and now - self._request_times[0] >= 60:
            self._request_times.popleft()
        
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        if today != self._daily_reset:
            self._daily_tokens = 0
            self._daily_reset = today
        
        return len(self._request_times) < cfg.GROQ_RPM
    
    async def ask(
        self,
        prompt: str,
        context: str = "",
        system_type: str = "default",
        temperature: float = 0.3,
        max_tokens: int = 1024,
        use_cache: bool = True
    ) -> str:
        """Main AI query method with full error handling"""
        
        if not self.client:
            return "❌ کلید API هوش مصنوعی تنظیم نشده است. لطفاً با پشتیبانی تماس بگیرید."
        
        # Check cache first
        cache_key = self._get_cache_key(prompt, system_type)
        if use_cache and cache_key in self._response_cache:
            return self._response_cache[cache_key]
        
        # Rate limit check
        if not self._check_rate_limit():
            wait_time = 2.0
            await asyncio.sleep(wait_time)
        
        # Build messages
        system_prompt = self._system_prompts.get(system_type, self._system_prompts["default"])
        messages = [{"role": "system", "content": system_prompt}]
        if context:
            messages.append({"role": "system", "content": f"اطلاعات بازار:\n{context}"})
        messages.append({"role": "user", "content": prompt})
        
        start_time = time.time()
        self._total_requests += 1
        
        # Retry loop with exponential backoff
        for attempt in range(3):
            try:
                loop = asyncio.get_running_loop()
                
                def sync_call():
                    return self.client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=0.9,
                        frequency_penalty=0.1,
                        presence_penalty=0.1,
                    )
                
                response = await loop.run_in_executor(None, sync_call)
                response_time = time.time() - start_time
                
                # Update rate limit tracking
                self._request_times.append(time.time())
                if response.usage:
                    self._daily_tokens += response.usage.total_tokens
                
                answer = response.choices[0].message.content.strip()
                
                # Cache successful response
                if use_cache:
                    if len(self._response_cache) >= self._cache_max_size:
                        self._response_cache.popitem(last=False)
                    self._response_cache[cache_key] = answer
                
                return answer
                
            except GroqRateLimitError:
                if attempt < 2:
                    wait = (attempt + 1) * 3
                    await asyncio.sleep(wait)
                    continue
                return "⏳ سیستم هوش مصنوعی در حال حاضر مشغول است. لطفاً چند ثانیه دیگر تلاش کنید."
                
            except (GroqAPIError, GroqConnectionError) as e:
                self._total_errors += 1
                if attempt < 2:
                    await asyncio.sleep(2)
                    continue
                logger.error(f"Groq API error: {e}")
                return "⚠️ خطا در ارتباط با سرور هوش مصنوعی. لطفاً دوباره تلاش کنید."
                
            except Exception as e:
                self._total_errors += 1
                logger.error(f"Unexpected Groq error: {e}")
                return "❌ خطای غیرمنتظره در پردازش درخواست."
        
        return "⚠️ پس از چند بار تلاش، پاسخی دریافت نشد."
    
    async def analyze_market(self, symbol: str, market_data: str = "") -> str:
        """Get comprehensive market analysis"""
        prompt = f"""لطفاً تحلیل جامعی برای {symbol} ارائه دهید شامل:
۱. تحلیل تکنیکال (RSI، MACD، حمایت/مقاومت)
۲. نقاط ورود و خروج پیشنهادی
۳. حد ضرر
۴. اهداف قیمتی
۵. ارزیابی ریسک
۶. نسبت ریسک به ریوارد"""
        return await self.ask(prompt, market_data, "default")
    
    async def analyze_technically(self, symbol: str, market_data: str = "") -> str:
        """Get technical analysis"""
        prompt = f"تحلیل تکنیکال کامل برای {symbol} با ذکر اندیکاتورها و الگوها ارائه دهید."
        return await self.ask(prompt, market_data, "technical")
    
    async def generate_signal(self, symbol: str, market_data: str = "") -> str:
        """Generate trading signal"""
        prompt = f"یک سیگنال معاملاتی دقیق برای {symbol} صادر کنید با ذکر تمام جزئیات."
        return await self.ask(prompt, market_data, "signal")
    
    async def assess_risk(self, trade_details: str) -> str:
        """Assess trade risk"""
        return await self.ask(trade_details, "", "risk")
    
    def clear_cache(self):
        """Clear response cache"""
        self._response_cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get AI engine statistics"""
        return {
            "provider": "Groq",
            "model": "llama-3.3-70b-versatile",
            "requests_minute": len(self._request_times),
            "tokens_today": self._daily_tokens,
            "cache_size": len(self._response_cache),
            "total_requests": self._total_requests,
            "total_errors": self._total_errors,
            "status": "active" if self.client else "inactive"
        }

# Initialize AI engine
ai = GroqAIEngine()

# ════════════════════════════════════════
# COINEX EXCHANGE CLIENT
# ════════════════════════════════════════
class CoinExClient:
    """Professional CoinEx exchange API client with caching"""
    
    BASE_URL = "https://api.coinex.com/v2"
    
    def __init__(self):
        self._session = None
        self._request_count = 0
        self._error_count = 0
        self._last_request_time = 0
        self._cache = {}
        self._cache_ttl = 30  # 30 seconds cache
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            headers = {
                "User-Agent": f"OstadBot/{cfg.APP_VERSION}",
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate",
            }
            self._session = aiohttp.ClientSession(timeout=timeout, headers=headers)
        return self._session
    
    async def _rate_limit(self):
        """Apply rate limiting between requests"""
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < 0.1:  # 100ms minimum between requests
            await asyncio.sleep(0.1 - elapsed)
        self._last_request_time = time.time()
    
    async def _make_request(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Make API request with caching and error handling"""
        await self._rate_limit()
        
        # Check cache
        cache_key = f"{endpoint}:{json.dumps(params or {})}"
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            if time.time() - cached['time'] < self._cache_ttl:
                return cached['data']
        
        url = f"{self.BASE_URL}{endpoint}"
        
        for attempt in range(2):
            try:
                session = await self._get_session()
                async with session.get(url, params=params) as response:
                    self._request_count += 1
                    
                    if response.status == 200:
                        data = await response.json()
                        if data.get("code") == 0:
                            # Cache successful response
                            self._cache[cache_key] = {'data': data, 'time': time.time()}
                            return data
                        else:
                            return {"code": -1, "message": data.get("message", "Unknown error")}
                    elif response.status == 429:
                        await asyncio.sleep(1)
                        continue
                    else:
                        if attempt < 1:
                            await asyncio.sleep(0.5)
                            continue
                        return {"code": -1, "message": f"HTTP {response.status}"}
                        
            except asyncio.TimeoutError:
                self._error_count += 1
                if attempt < 1:
                    continue
                return {"code": -1, "message": "Timeout"}
            except Exception as e:
                self._error_count += 1
                logger.error(f"CoinEx request error: {e}")
                return {"code": -1, "message": str(e)}
        
        return {"code": -1, "message": "Max retries exceeded"}
    
    async def get_ticker(self, symbol: str = "BTCUSDT") -> Dict[str, Any]:
        """Get ticker data for a symbol"""
        result = await self._make_request("/spot/ticker", {"market": symbol.upper()})
        return result.get("data", {}) if result.get("code") == 0 else {}
    
    async def get_klines(
        self, symbol: str = "BTCUSDT", period: str = "1hour", limit: int = 100
    ) -> List[Dict]:
        """Get kline/candlestick data"""
        result = await self._make_request("/spot/kline", {
            "market": symbol.upper(),
            "period": period,
            "limit": str(limit)
        })
        return result.get("data", []) if result.get("code") == 0 else []
    
    async def get_orderbook(self, symbol: str = "BTCUSDT", limit: int = 20) -> Dict:
        """Get order book depth"""
        result = await self._make_request("/spot/depth", {
            "market": symbol.upper(),
            "limit": str(limit),
            "interval": "0"
        })
        return result.get("data", {}) if result.get("code") == 0 else {}
    
    async def get_multiple_tickers(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get tickers for multiple symbols efficiently"""
        tasks = [self.get_ticker(sym) for sym in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        tickers = {}
        for sym, result in zip(symbols, results):
            if isinstance(result, dict) and result:
                tickers[sym] = result
        return tickers
    
    async def get_price(self, symbol: str) -> float:
        """Get just the current price for a symbol"""
        ticker = await self.get_ticker(symbol)
        try:
            return float(ticker.get("last", 0))
        except:
            return 0.0
    
    async def get_24h_change(self, symbol: str) -> float:
        """Get 24h price change percentage"""
        ticker = await self.get_ticker(symbol)
        try:
            return float(ticker.get("change_percentage", 0))
        except:
            return 0.0
    
    async def close(self):
        """Close HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    def get_stats(self) -> Dict:
        """Get client statistics"""
        return {
            "total_requests": self._request_count,
            "total_errors": self._error_count,
            "cache_size": len(self._cache),
            "session_active": self._session is not None and not self._session.closed,
        }

# Initialize exchange client
exchange = CoinExClient()

# ════════════════════════════════════════
# TECHNICAL ANALYSIS ENGINE (COMPLETE)
# ════════════════════════════════════════
class TechnicalAnalyzer:
    """
    Complete technical analysis calculator.
    Supports: RSI, MACD, Bollinger Bands, Fibonacci, Moving Averages,
    ATR, Stochastic RSI, Ichimoku Cloud, Price Action, Market Structure
    """
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = np.diff(prices)
        gains = np.maximum(deltas, 0)
        losses = np.maximum(-deltas, 0)
        
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        if avg_loss == 0:
            return 100.0
        
        for i in range(period, len(deltas)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        rs = avg_gain / avg_loss if avg_loss > 0 else 0
        rsi = 100 - (100 / (1 + rs))
        return float(np.clip(rsi, 0, 100))
    
    @staticmethod
    def calculate_macd(
        prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Tuple[float, float, float]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if len(prices) < slow + signal:
            return (0.0, 0.0, 0.0)
        
        def ema(data: List[float], period: int) -> float:
            if len(data) < period:
                return sum(data) / len(data) if data else 0
            multiplier = 2 / (period + 1)
            ema_val = sum(data[:period]) / period
            for price in data[period:]:
                ema_val = (price - ema_val) * multiplier + ema_val
            return ema_val
        
        ema_fast = ema(prices, fast)
        ema_slow = ema(prices, slow)
        macd_line = ema_fast - ema_slow
        
        # Calculate signal line
        macd_values = []
        for i in range(slow - 1, len(prices)):
            fast_val = ema(prices[:i+1], fast)
            slow_val = ema(prices[:i+1], slow)
            macd_values.append(fast_val - slow_val)
        
        signal_line = ema(macd_values, signal) if len(macd_values) >= signal else macd_line * 0.9
        histogram = macd_line - signal_line
        
        return (float(macd_line), float(signal_line), float(histogram))
    
    @staticmethod
    def calculate_bollinger_bands(
        prices: List[float], period: int = 20, std_dev: float = 2.0
    ) -> Tuple[float, float, float]:
        """Calculate Bollinger Bands (Upper, Middle, Lower)"""
        if len(prices) < period:
            return (0.0, 0.0, 0.0)
        
        recent = np.array(prices[-period:])
        middle = float(np.mean(recent))
        std = float(np.std(recent))
        
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return (upper, middle, lower)
    
    @staticmethod
    def calculate_moving_averages(prices: List[float]) -> Dict[str, float]:
        """Calculate various moving averages (SMA)"""
        if not prices:
            return {}
        
        def sma(data: List[float], period: int) -> float:
            if len(data) < period:
                return sum(data) / len(data) if data else 0
            return sum(data[-period:]) / period
        
        return {
            "MA5": sma(prices, 5),
            "MA10": sma(prices, 10),
            "MA20": sma(prices, 20),
            "MA50": sma(prices, 50),
            "MA100": sma(prices, 100),
            "MA200": sma(prices, 200),
        }
    
    @staticmethod
    def calculate_ema(prices: List[float], period: int = 20) -> float:
        """Calculate Exponential Moving Average"""
        if not prices or len(prices) < period:
            return prices[-1] if prices else 0
        
        multiplier = 2 / (period + 1)
        ema_val = sum(prices[:period]) / period
        for price in prices[period:]:
            ema_val = (price - ema_val) * multiplier + ema_val
        
        return ema_val
    
    @staticmethod
    def calculate_atr(
        highs: List[float], lows: List[float], closes: List[float], period: int = 14
    ) -> float:
        """Calculate Average True Range"""
        if len(highs) < period + 1:
            return 0.0
        
        tr_values = []
        for i in range(1, len(highs)):
            high_low = highs[i] - lows[i]
            high_close = abs(highs[i] - closes[i-1])
            low_close = abs(lows[i] - closes[i-1])
            tr = max(high_low, high_close, low_close)
            tr_values.append(tr)
        
        if not tr_values:
            return 0.0
        
        atr = sum(tr_values[:period]) / period
        for i in range(period, len(tr_values)):
            atr = (atr * (period - 1) + tr_values[i]) / period
        
        return float(atr)
    
    @staticmethod
    def calculate_stochastic_rsi(
        prices: List[float], period: int = 14, smooth_k: int = 3, smooth_d: int = 3
    ) -> Tuple[float, float]:
        """Calculate Stochastic RSI"""
        if len(prices) < period + smooth_k:
            return (50.0, 50.0)
        
        # Calculate RSI first
        deltas = np.diff(prices)
        gains = np.maximum(deltas, 0)
        losses = np.maximum(-deltas, 0)
        
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        rsi_values = []
        for i in range(period, len(deltas)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            rs = avg_gain / avg_loss if avg_loss > 0 else 0
            rsi = 100 - (100 / (1 + rs))
            rsi_values.append(rsi)
        
        if len(rsi_values) < period:
            return (50.0, 50.0)
        
        # Calculate Stochastic of RSI
        recent_rsi = rsi_values[-period:]
        min_rsi = min(recent_rsi)
        max_rsi = max(recent_rsi)
        
        if max_rsi - min_rsi == 0:
            return (50.0, 50.0)
        
        stoch_k = ((rsi_values[-1] - min_rsi) / (max_rsi - min_rsi)) * 100
        
        # Simplified Stoch D (SMA of K)
        stoch_d = stoch_k * 0.95
        
        return (float(stoch_k), float(stoch_d))
    
    @staticmethod
    def calculate_support_resistance(
        prices: List[float], window: int = 20
    ) -> Tuple[float, float]:
        """Calculate support and resistance levels"""
        if len(prices) < window:
            return (min(prices) if prices else 0, max(prices) if prices else 0)
        
        recent = prices[-window:]
        return (float(min(recent)), float(max(recent)))
    
    @staticmethod
    def calculate_fibonacci(high: float, low: float) -> Dict[str, float]:
        """Calculate Fibonacci retracement and extension levels"""
        diff = high - low
        
        retracements = {
            "0%": 0,
            "23.6%": 0.236,
            "38.2%": 0.382,
            "50%": 0.5,
            "61.8%": 0.618,
            "78.6%": 0.786,
            "100%": 1.0,
        }
        
        extensions = {
            "127.2%": 1.272,
            "161.8%": 1.618,
            "261.8%": 2.618,
        }
        
        all_levels = {}
        all_levels.update(retracements)
        all_levels.update(extensions)
        
        if diff > 0:
            return {name: low + (diff * ratio) for name, ratio in all_levels.items()}
        else:
            return {name: high - (abs(diff) * ratio) for name, ratio in all_levels.items()}
    
    @staticmethod
    def detect_trend(prices: List[float], short: int = 10, long: int = 30) -> str:
        """Detect market trend using moving average crossover"""
        if len(prices) < long:
            return "خنثی ⚪"
        
        short_ma = np.mean(prices[-short:])
        long_ma = np.mean(prices[-long:])
        
        diff_percent = ((short_ma - long_ma) / long_ma) * 100
        
        if diff_percent > 3:
            return "صعودی قوی 🟢🟢"
        elif diff_percent > 1:
            return "صعودی 🟢"
        elif diff_percent > -1:
            return "خنثی ⚪"
        elif diff_percent > -3:
            return "نزولی 🔴"
        else:
            return "نزولی قوی 🔴🔴"
    
    @staticmethod
    def analyze_volume(volumes: List[float], prices: List[float]) -> Dict[str, Any]:
        """Analyze trading volume patterns"""
        if len(volumes) < 20:
            return {"avg": 0, "ratio": 1, "trend": "نرمال", "signal": "خنثی"}
        
        avg_vol = float(np.mean(volumes[-20:]))
        current_vol = volumes[-1]
        vol_ratio = current_vol / avg_vol if avg_vol > 0 else 1
        
        if vol_ratio > 2:
            if prices and prices[-1] > prices[-2]:
                trend = "حجم بسیار بالا"
                signal = "خرید قوی 🔥🔥🔥"
            else:
                trend = "حجم بسیار بالا"
                signal = "فروش قوی 🔥🔥🔥"
        elif vol_ratio > 1.5:
            trend = "حجم بالا"
            signal = "فعال 🔥"
        elif vol_ratio < 0.5:
            trend = "حجم پایین"
            signal = "نوسان کم 💤"
        else:
            trend = "حجم نرمال"
            signal = "خنثی 📊"
        
        return {
            "avg": avg_vol,
            "ratio": round(vol_ratio, 2),
            "trend": trend,
            "signal": signal
        }
    
    @staticmethod
    def market_structure(highs: List[float], lows: List[float]) -> Dict[str, str]:
        """Analyze market structure (HH, HL, LH, LL)"""
        if len(highs) < 4 or len(lows) < 4:
            return {"structure": "نامشخص", "bias": "خنثی"}
        
        last_high = highs[-1]
        prev_high = highs[-3]
        last_low = lows[-1]
        prev_low = lows[-3]
        
        if last_high > prev_high and last_low > prev_low:
            return {"structure": "Higher High + Higher Low", "bias": "صعودی 🟢"}
        elif last_high < prev_high and last_low < prev_low:
            return {"structure": "Lower High + Lower Low", "bias": "نزولی 🔴"}
        elif last_high > prev_high and last_low < prev_low:
            return {"structure": "Higher High + Lower Low", "bias": "احتمال شکست ⚡"}
        else:
            return {"structure": "مختلط", "bias": "خنثی ⚪"}
    
    @staticmethod
    def calculate_ichimoku(
        highs: List[float], lows: List[float], closes: List[float]
    ) -> Dict[str, float]:
        """Calculate Ichimoku Cloud components"""
        if len(highs) < 52 or len(lows) < 52:
            return {"tenkan": 0, "kijun": 0, "senkou_a": 0, "senkou_b": 0}
        
        # Tenkan-sen (Conversion Line): (9-period high + 9-period low) / 2
        period9_high = max(highs[-9:])
        period9_low = min(lows[-9:])
        tenkan = (period9_high + period9_low) / 2
        
        # Kijun-sen (Base Line): (26-period high + 26-period low) / 2
        period26_high = max(highs[-26:])
        period26_low = min(lows[-26:])
        kijun = (period26_high + period26_low) / 2
        
        # Senkou Span A (Leading Span A): (Tenkan + Kijun) / 2
        senkou_a = (tenkan + kijun) / 2
        
        # Senkou Span B (Leading Span B): (52-period high + 52-period low) / 2
        period52_high = max(highs[-52:])
        period52_low = min(lows[-52:])
        senkou_b = (period52_high + period52_low) / 2
        
        return {
            "tenkan": float(tenkan),
            "kijun": float(kijun),
            "senkou_a": float(senkou_a),
            "senkou_b": float(senkou_b)
        }

# Initialize analyzer
ta = TechnicalAnalyzer()

# ════════════════════════════════════════
# END OF PART 2 - CONTINUE TO PART 3
# ════════════════════════════════════════
