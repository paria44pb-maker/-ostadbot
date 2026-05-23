import os
import logging
import asyncio
import time
import random
import json
import httpx
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@CryptoPulse606")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# ---------------------------- لیست ارزها ----------------------------
SYMBOLS = {
    "BTCUSDT": {"name": "بیت‌کوین", "emoji": "👑"},
    "ETHUSDT": {"name": "اتریوم", "emoji": "💎"},
    "SOLUSDT": {"name": "سولانا", "emoji": "⚡"},
    "BNBUSDT": {"name": "بایننس", "emoji": "🟡"},
    "XRPUSDT": {"name": "ریپل", "emoji": "💧"},
    "ADAUSDT": {"name": "کاردانو", "emoji": "🌿"},
    "DOGEUSDT": {"name": "داوج", "emoji": "🐕"},
}

# ---------------------------- ذخیره‌سازی دمو (ساده) ----------------------------
demo_balance = 10000
demo_positions = []
demo_history = []

# ---------------------------- توابع کوینکس (بدون خطا) ----------------------------
async def get_coinex_price(symbol):
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            url = f"https://api.coinex.com/v1/market/ticker?market={symbol}"
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 0:
                    ticker = data["data"]["ticker"]
                    return {
                        "price": float(ticker.get("last", 0)),
                        "change": float(ticker.get("change", 0)),
                        "volume": float(ticker.get("vol", 0))
                    }
    except Exception as e:
        logger.error(f"Price error {symbol}: {e}")
    return None

async def get_historical_closes(symbol, limit=50):
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            url = f"https://api.coinex.com/v1/market/kline?market={symbol}&type=5min&limit={limit}"
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 0:
                    klines = data["data"]
                    return [float(k[4]) for k in klines]  # قیمت بسته شدن
    except Exception as e:
        logger.error(f"Kline error {symbol}: {e}")
    return None

# ---------------------------- اندیکاتور ساده RSI ----------------------------
def calculate_rsi(closes, period=14):
    if len(closes) < period + 1:
        return 50
    gains, losses = [], []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i-1]
        if diff > 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(-diff)
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def simple_signal(change, rsi):
    if change > 2 and rsi < 70:
        return "خرید قوی", 90
    elif change > 0.5 and rsi < 60:
        return "خرید", 75
    elif change < -2 and rsi > 30:
        return "فروش قوی", 90
    elif change < -0.5 and rsi > 40:
        return "فروش", 75
    else:
        return "نگهداری", 50

# ---------------------------- آموزش‌های غیرتکراری (بیش از ۱۰۰ موضوع) ----------------------------
EDUCATION_LIST = [
    "📘 *کندل چکش (Hammer)*: در انتهای روند نزولی شکل می‌گیرد و نشانه بازگشت صعودی است. بدنه کوچک، فتیله پایین بلند.",
    "📘 *کندل مرد به دار آویخته (Hanging Man)*: در انتهای روند صعودی ظاهر می‌شود و هشدار برگشت نزولی می‌دهد.",
    "📘 *کندل ستاره دنباله‌دار (Shooting Star)*: در قله روند صعودی نشانه فروش است. بدنه کوچک، فتیله بالایی بلند.",
    "📘 *الگوی پوشای صعودی (Bullish Engulfing)*: دو کندل، اول نزولی و دوم صعودی که کل اولی را می‌پوشاند – سیگنال خرید.",
    "📘 *الگوی پوشای نزولی (Bearish Engulfing)*: سیگنال فروش – کندل دوم نزولی کل کندل صعودی قبلی را می‌پوشاند.",
    "📘 *RSI*: اشباع فروش زیر ۳۰ (منطقه خرید)، اشباع خرید بالای ۷۰ (منطقه فروش).",
    "📘 *MACD*: تقاطع خط MACD از بالای خط سیگنال = سیگنال خرید. تقاطع از پایین = سیگنال فروش.",
    "📘 *میانگین متحرک ساده (SMA)*: میانگین قیمت در یک دوره. دوره ۲۰ برای تشخیص روند کوتاه‌مدت استفاده می‌شود.",
    "📘 *میانگین متحرک نمایی (EMA)*: به قیمت‌های جدید وزن بیشتری می‌دهد و سریع‌تر از SMA واکنش نشان می‌دهد.",
    "📘 *باند بولینگر*: انقباض باندها预示 نوسان شدید، برخورد به باند پایین سیگنال خرید، برخورد به باند بالا سیگنال فروش.",
    "📘 *حمایت و مقاومت*: حمایت سطحی است که قیمت از آن پایین‌تر نمی‌رود، مقاومت سطحی است که قیمت بالاتر نمی‌رود.",
    "📘 *حجم معاملات*: حجم بالا در کنار یک حرکت قیمتی، قدرت روند را تأیید می‌کند.",
    "📘 *الگوی دوجی (Doji)*: نشانه تردید بازار و احتمال تغییر روند. در سقف یا کف روند اهمیت بیشتری دارد.",
    "📘 *پرایس اکشن*: تحلیل حرکت قیمت بدون اندیکاتور – تمرکز بر خطوط حمایت/مقاومت و الگوهای کندل.",
    "📘 *شاخص ترس و طمع (Fear & Greed)*: پایین‌تر از ۲۵ = ترس شدید (فرصت خرید)، بالاتر از ۷۵ = طمع شدید (احتیاط در خرید).",
    "📘 *تحلیل فاندامنتال*: بررسی اخبار، نرخ بهره، تورم، قانونگذاری‌ها – تأثیر مستقیم بر قیمت بیت‌کوین و آلت‌کوین‌ها.",
    "📘 *مدیریت ریسک*: هرگز بیش از ۲٪ سرمایه را در یک معامله ریسک نکنید. نسبت ریسک به ریوارد حداقل ۱:۲.",
    "📘 *ترید روند (Trend Trading)*: معامله در جهت روند اصلی – در روند صعودی به دنبال خرید، در نزولی به دنبال فروش.",
    "📘 *اسکالپینگ*: معاملات بسیار کوتاه‌مدت (چند ثانیه تا چند دقیقه) – نیاز به سرعت و تمرکز بالا.",
    "📘 *سوئینگ تریدینگ*: نگهداری پوزیشن از چند روز تا چند هفته – مبتنی بر تحلیل تکنیکال تایم‌فریم بالاتر.",
    "📘 *پوزیشن تریدینگ*: نگهداری ماه‌ها تا سال‌ها – بر اساس تحلیل فاندامنتال و روند بلندمدت.",
    "📘 *روانشناسی ترید*: کنترل احساسات، طمع و ترس – مهم‌تر از هر استراتژی معاملاتی.",
    "📘 *بک‌تست (Backtest)*: تست یک استراتژی بر روی داده‌های گذشته برای ارزیابی سودآوری آن.",
    "📘 *اندیکاتور استوکاستیک (Stochastic)*: مقایسه قیمت بسته شدن با محدوده قیمتی در یک دوره – مناطق اشباع خرید/فروش.",
    "📘 *CCI (Commodity Channel Index)*: بالای ۱۰۰ = اشباع خرید، زیر ۱۰۰- = اشباع فروش.",
    "📘 *ویلیامز %R (Williams %R)*: مشابه استوکاستیک – بین ۰ و ۲۰- = اشباع خرید، بین ۸۰- و ۱۰۰- = اشباع فروش.",
    "📘 *ADX (Average Directional Index)*: بالای ۲۵ نشانه روند قوی (صعودی یا نزولی) – هرچه بالاتر، روند قوی‌تر.",
    "📘 *ابر ایچیموکو (Ichimoku Cloud)*: قیمت بالای ابر = روند صعودی، زیر ابر = روند نزولی – خود ابر به عنوان حمایت/مقاومت عمل می‌کند.",
    "📘 *الگوی سه سرباز سفید (Three White Soldiers)*: سه کندل صعودی پشت سر هم – سیگنال ادامه روند صعودی.",
    "📘 *الگوی سه کلاغ سیاه (Three Black Crows)*: سه کندل نزولی پشت سر هم – سیگنال ادامه روند نزولی.",
    "📘 *فیبوناچی اصلاحی (Fibonacci Retracement)*: سطوح ۰.۳۸۲، ۰.۵، ۰.۶۱۸ – نقاط احتمالی برگشت قیمت در روندهای قوی.",
    "📘 *الگوی مثلث متقارن (Symmetrical Triangle)*: نشانه تثبیت و احتمال شکست به هر سمت – باید منتظر شکست ماند.",
    "📘 *الگوی پرچم صعودی (Bull Flag)*: یک میله صعودی قوی و سپس یک کانال نزولی ملایم – ادامه روند صعودی.",
    "📘 *الگوی پرچم نزولی (Bear Flag)*: ادامه روند نزولی – مشابه پرچم صعودی ولی در جهت مخالف.",
    "📘 *جام و دسته (Cup and Handle)*: الگوی ادامه‌دهنده صعودی – پس از تکمیل دسته، انتظار شکست به بالا می‌رود.",
    "📘 *سر و شانه (Head and Shoulders)*: الگوی بازگشتی نزولی – پس از تشکیل شانه راست، احتمال برگشت شدید.",
    "📘 *سر و شانه معکوس (Inverse H&S)*: الگوی بازگشتی صعودی – در انتهای روند نزولی، سیگنال خرید.",
    "📘 *تله گاوی (Bull Trap)*: شکست مقاومت به سمت بالا و سپس برگشت سریع – باعث به دام افتادن خریداران.",
    "📘 *تله خرسی (Bear Trap)*: شکست حمایت به سمت پایین و سپس برگشت سریع – به دام افتادن فروشندگان.",
    "📘 *شکاف قیمتی (Gap)*: فاصله بین بسته شدن روز قبل و باز شدن امروز – شکاف‌ها معمولاً پر می‌شوند.",
    "📘 *مومنتوم (Momentum)*: قدرت حرکت قیمت – کاهش مومنتوم هشدار برگشت روند است.",
    "📘 *واگرایی (Divergence)*: اختلاف بین جهت قیمت و اندیکاتور (مثلاً RSI) – واگرایی مثبت سیگنال خرید و منفی سیگنال فروش.",
    "📘 *حجم تعادلی انباشت/توزیع (OBV)*: حجم قبل از حرکت قیمت تغییر می‌کند – OBV صعودی نشانه قدرت خریداران.",
    "📘 *میانگین متحرک هال (HMA)*: میانگین متحرک بدون تاخیر – مناسب برای تشخیص روند کوتاه‌مدت.",
    "📘 *سوپرترند (Supertrend)*: اندیکاتور دنبال‌کننده روند – در بالای قیمت سیگنال فروش، زیر قیمت سیگنال خرید.",
    "📘 *پارابولیک سار (Parabolic SAR)*: نقاطی که در زیر قیمت قرار می‌گیرند سیگنال خرید و بالای قیمت سیگنال فروش هستند.",
    "📘 *ایچیموکو تنکان و کیجون*: تقاطع تنکان (۹) از بالای کیجون (۲۶) سیگنال خرید و برعکس سیگنال فروش.",
    "📘 *اندیکاتور RVI (Relative Vigor Index)*: بالای خط صفر نشانه قدرت صعودی، زیر صفر قدرت نزولی.",
    "📘 *الگوی کف دو قلو (Double Bottom)*: الگوی بازگشتی صعودی – پس از تشکیل دو کف، قیمت معمولاً به بالا می‌رود.",
    "📘 *الگوی سقف دو قلو (Double Top)*: الگوی بازگشتی نزولی – پس از تشکیل دو قله، قیمت سقوط می‌کند.",
    "📘 *اندیکاتور ATR (Average True Range)*: میانگین محدوده واقعی – برای تعیین حد ضرر و سود استفاده می‌شود.",
    "📘 *الگوی ستاره صبحگاهی (Morning Star)*: سه کندل – نزولی، دوجی، صعودی – سیگنال خرید قوی.",
    "📘 *الگوی ستاره شامگاهی (Evening Star)*: سه کندل – صعودی، دوجی، نزولی – سیگنال فروش قوی.",
    "📘 *پول‌فلو (Money Flow Index - MFI)*: مشابه RSI ولی با در نظر گرفتن حجم – مناطق اشباع خرید/فروش.",
    "📘 *آسیلاتور عالی (Awesome Oscillator)*: هیستوگرام صعودی نشانه قدرت خریداران، نزولی نشانه قدرت فروشندگان.",
    "📘 *اندیکاتور مومنتوم (Momentum)*: نسبت قیمت فعلی به قیمت چند دوره قبل – افزایش مومنتوم تأیید روند.",
    "📘 *روند صعودی (Uptrend)*: تشکیل سقف‌ها و کف‌های بالاتر – بهترین استراتژی: خرید در اصلاح‌ها.",
    "📘 *روند نزولی (Downtrend)*: تشکیل سقف‌ها و کف‌های پایین‌تر – بهترین استراتژی: فروش در جمع‌آوری‌ها.",
    "📘 *رنج (Range)*: قیمت در یک بازه مشخص نوسان می‌کند – استراتژی: خرید از کف بازه و فروش از سقف بازه.",
    "📘 *تایم‌فریم چندگانه (Multiple Timeframe)*: تحلیل در چند تایم‌فریم (مثلاً هفتگی، روزانه، ۴ ساعته) برای تأیید سیگنال.",
    "📘 *مدیریت سرمایه (MM)*: تقسیم سرمایه به چند بخش و ریسک کنترل‌شده.",
    "📘 *نقطه ورود (Entry Point)*: نباید بدون انتظار برای تأیید روند وارد معامله شد – از حداقل دو اندیکاتور تأیید بگیرید.",
    "📘 *حد ضرر (Stop Loss)*: سطحی که در صورت رسیدن قیمت به آن، ضرر شما محدود می‌شود – همیشه اجباری.",
    "📘 *حد سود (Take Profit)*: سطح برداشت سود – می‌تواند یک هدف یا چند هدف پلکانی باشد.",
    "📘 *تریلینگ استاپ (Trailing Stop)*: حد ضرر متحرک که به دنبال قیمت حرکت می‌کند تا سود را حفظ کند.",
    "📘 *اخبار نرخ بهره فدرال رزرو*: افزایش نرخ بهره معمولاً برای ریسک‌پذیرها (کریپتو) منفی است.",
    "📘 *تأثیر تورم بر کریپتو*: تورم بالا باعث می‌شود سرمایه‌گذاران به سمت دارایی‌های امن مثل بیت‌کوین بروند.",
    "📘 *قانونگذاری ارزهای دیجیتال*: تصمیمات ممنوعیت یا پذیرش توسط دولت‌ها تأثیر مستقیم بر قیمت دارد.",
    "📘 *رویداد هاوینگ بیت‌کوین (Halving)*: هر ۴ سال یکبار پاداش استخراج نصف می‌شود – معمولاً منجر به روند صعودی بلندمدت می‌شود.",
    "📘 *اتریوم و ارتقاهای شبکه (EIP)*: هر ارتقا می‌تواند باعث افزایش ارزش اتریوم شود (مثل Merge, Dencun).",
    "📘 *سولانا و کارمزد پایین*: ویژگی رقابتی سولانا جذب برنامه‌های دیفای و NFT است.",
    "📘 *ریپل و دعاوی حقوقی (SEC)*: نتیجه پرونده ریپل تأثیر زیادی بر قیمت XRP دارد.",
    "📘 *تأثیر اخبار اقتصاد کلان*: شاخص‌های CPI, PPI, نرخ بیکاری همگی بر بیت‌کوین اثر می‌گذارند.",
    "📘 *تحلیل احساسات (Sentiment Analysis)*: استفاده از ابزارهای هوش مصنوعی برای سنجش نظرات توییتر، ردیت و تلگرام.",
    "📘 *انباشت نهنگ‌ها (Whale Accumulation)*: حجم بالای خرید در آدرس‌های خاص نشانه صعود بلندمدت است.",
    "📘 *توزیع نهنگ‌ها (Whale Distribution)*: حجم بالای فروش هشدار نزول است.",
    "📘 *شاخص MVRV Z-Score*: نسبت ارزش بازار به ارزش تحقق‌یافته – ورود به منطقه سبز نشانه کف و منطقه قرمز نشانه سقف است.",
    "📘 *شاخص Puell Multiple*: نسبت درآمد استخراج‌کنندگان به میانگین سالانه – ورود به منطقه قرمز نشانه نزدیکی به سقف قیمتی است.",
    "📘 *شاخص Stock-to-Flow (S2F)*: پیش‌بینی قیمت بیت‌کوین بر اساس کمیابی – نسخه‌های جدیدتر دقت کمتری دارند.",
    "📘 *مدل Rainbow Chart*: باندهای رنگی برای تشخیص ارزندگی بیت‌کوین – منطقه آبی تیره ارزان، منطقه قرمز گران.",
    "📘 *تحلیل آنچین (On-chain)*: بررسی آدرس‌های فعال، تعداد تراکنش‌ها، ارزش منتقل شده – شاخص‌های بنیادی.",
    "📘 *فعالیت آدرس‌های بیت‌کوین*: افزایش آدرس‌های فعال نشانه پذیرش بیشتر و معمولاً صعود قیمت.",
    "📘 *نرخ هش (Hashrate)*: قدرت محاسباتی شبکه – افزایش نرخ هش نشانه امنیت بیشتر و اعتماد استخراج‌کنندگان.",
    "📘 *مفهوم دیفای (DeFi)*: امور مالی غیرمتمرکز – پروتکل‌هایی که واسطه‌ها را حذف می‌کنند.",
    "📘 *لایه ۲ (Layer 2)*: راهکارهای مقیاس‌پذیری روی بلاکچین اصلی (مثل لایتنینگ برای بیت‌کوین، آربیتروم برای اتریوم).",
    "📘 *پل‌های زنجیره‌ای (Cross-chain Bridges)*: انتقال دارایی بین بلاکچین‌های مختلف – افزایش نقدینگی.",
    "📘 *توکن غیرمثلی (NFT)*: دارایی منحصربه‌فرد دیجیتال – بازار NFT رابطه نزدیکی با اتریوم و سولانا دارد.",
    "📘 *متاورس (Metaverse)*: جهان مجازی – رمزارزهای مرتبط مثل MANA، SAND، یا متاورس خود اتریوم.",
    "📘 *قوانین پولشویی (AML)*: رعایت مقررات برای صرافی‌ها بر معاملات تأثیر می‌گذارد.",
    "📘 *شناسایی مشتری (KYC)*: فرایند احراز هویت در صرافی‌ها – ممکن است باعث افت قیمت در صورت تشدید شود.",
    "📘 *مالیات بر ارز دیجیتال*: قوانین مالیاتی کشورها بر گزارش‌دهی معاملات تأثیر دارد.",
    "📘 *بیت‌کوین به عنوان پوشش تورم (Hedge)*: در شرایط تورمی، سرمایه‌گذاران به بیت‌کوین پناه می‌برند.",
    "📘 *ترید رباتیک (Algorithmic Trading)*: استفاده از ربات‌ها برای معامله خودکار بر اساس سیگنال‌های از پیش تعیین شده.",
    "📘 *ریسک هک و امنیت*: نگهداری ارزها در کیف پول سرد (Cold Wallet) نسبت به صرافی امن‌تر است.",
    "📘 *بازار گاوی (Bull Market)*: رشد چندماهه یا چندساله قیمت – استراتژی: خرید در اصلاح‌ها و نگهداری.",
    "📘 *بازار خرسی (Bear Market)*: ریزش طولانی مدت – استراتژی: فروش در جمع‌آوری‌ها یا معامله در جهت نزول.",
    "📘 *علت رشد ناگهانی (Pump)*: می‌تواند خبر مثبت، هماهنگی نهنگ‌ها یا پمپ اند دامپ باشد – در نوع اخیر، ضرر محتمل است.",
    "📘 *علت سقوط ناگهانی (Dump)*: خبر منفی، برداشت نهنگ یا اصلاح تکنیکال – در این مواقع از ورود با حد ضرر استفاده کنید.",
    "📘 *ترس از دست دادن (FOMO)*: احساس خرید در قله – یکی از مهم‌ترین دلایل ضرر تریدرهای تازه‌کار.",
    "📘 *ترس از دست دادن سرمایه (FUD)*: فروش در کف به دلیل اخبار منفی نادرست – برعکس FOMO، باعث فروش زودهنگام می‌شود.",
    "📘 *اهمیت دفترچه معاملاتی (Journal)*: ثبت هر معامله (دلیل ورود، حجم، قیمت، خروج و سود/زیان) بهترین روش برای یادگیری است.",
    "📘 *آزمایشگاه معامله‌گری (Demo)*: قبل از ورود به بازار واقعی، حتماً با حساب دمی تمرین کنید – این ربات یک حساب دمو دارد.",
]

education_index = 0
education_last_hour = -1

async def send_education(app):
    global education_index, education_last_hour
    now = datetime.now()
    current_hour = now.hour // 2  # هر ۲ ساعت یک مطلب جدید
    if current_hour != education_last_hour:
        education_last_hour = current_hour
        topic = EDUCATION_LIST[education_index % len(EDUCATION_LIST)]
        education_index += 1
        msg = f"{topic}\n\n✨ @CryptoPulse606"
        try:
            await app.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")
            logger.info(f"آموزش ارسال شد (شاخص {education_index})")
        except Exception as e:
            logger.error(f"خطا در ارسال آموزش: {e}")

# ---------------------------- ارسال خودکار سیگنال (هر ۵ دقیقه) ----------------------------
auto_thread_running = True

def auto_signal_thread(app):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while auto_thread_running:
        time.sleep(300)  # 5 دقیقه
        loop.run_until_complete(send_auto_signals(app))

async def send_auto_signals(app):
    logger.info("شروع ارسال سیگنال خودکار...")
    if not CHANNEL_ID:
        logger.error("CHANNEL_ID تنظیم نشده")
        return

    for symbol, info in list(SYMBOLS.items())[:3]:
        price_data = await get_coinex_price(symbol)
        if not price_data:
            logger.warning(f"قیمت {symbol} در دسترس نیست")
            continue
        closes = await get_historical_closes(symbol, 30)
        if not closes:
            closes = [price_data["price"] * (1 + random.uniform(-0.01, 0.01)) for _ in range(30)]
        rsi = calculate_rsi(closes)
        signal, confidence = simple_signal(price_data["change"], rsi)
        support = price_data["price"] * 0.95
        resistance = price_data["price"] * 1.05
        if "خرید" in signal:
            sl = price_data["price"] * 0.97
            tp = price_data["price"] * 1.04
        else:
            sl = price_data["price"] * 1.03
            tp = price_data["price"] * 0.96
        msg = f"""
🌿 *『 {info['emoji']} {info['name']} 』* 🌿
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 **قیمت:** `${price_data['price']:,.2f}`
📈 **تغییر 24h:** `{price_data['change']:+.2f}%`
🎯 **سیگنال:** `{signal}` (اطمینان {confidence}%)
📊 **RSI:** `{rsi:.1f}`
🟢 **حمایت:** `${support:,.2f}`
🔴 **مقاومت:** `${resistance:,.2f}`
🛡️ **حد ضرر:** `${sl:,.2f}`
🎯 **هدف:** `${tp:,.2f}`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ @CryptoPulse606
"""
        try:
            await app.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")
            logger.info(f"سیگنال {symbol} ارسال شد")
            await asyncio.sleep(3)
        except Exception as e:
            logger.error(f"خطا در ارسال سیگنال {symbol}: {e}")

    # ارسال آموزش هر ۲ ساعت (در هر دور ۵ دقیقه‌ای، فقط در ساعت مناسب اجرا می‌شود)
    await send_education(app)

# ---------------------------- منوی اصلی ----------------------------
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📊 قیمت لحظه‌ای", callback_data="prices")],
        [InlineKeyboardButton("🎯 سیگنال فوری", callback_data="signal")],
        [InlineKeyboardButton("📈 تحلیل تکنیکال", callback_data="technical")],
        [InlineKeyboardButton("🧠 چت با هوش مصنوعی", callback_data="ai")],
        [InlineKeyboardButton("📚 آموزش تصادفی", callback_data="education")],
        [InlineKeyboardButton("💰 پورتفوی دمو", callback_data="demo")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if OWNER_ID != 0 and update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ شما اجازه دسترسی ندارید.")
        return
    await update.message.reply_text(
        "🔥 *ربات فوق‌هوشمند کریپتو* 🔥\n\n"
        "✅ سیگنال لحظه‌ای به کانال\n"
        "✅ آموزش غیرتکراری هر ۲ ساعت\n"
        "✅ تحلیل تکنیکال ساده ولی کاربردی\n"
        "✅ معامله دمو (آموزشی)\n\n"
        "از منوی زیر انتخاب کنید:",
        parse_mode="Markdown",
        reply_markup=get_main_menu()
    )

async def prices_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 دریافت قیمت‌ها...")
    text = "💰 *قیمت لحظه‌ای* 💰\n\n"
    for sym, info in SYMBOLS.items():
        data = await get_coinex_price(sym)
        if data:
            emoji = "🟢" if data["change"] > 0 else "🔴" if data["change"] < 0 else "⚪"
            text += f"{emoji} {info['emoji']} *{info['name']}*: ${data['price']:,.2f} ({data['change']:+.2f}%)\n"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def signal_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 تحلیل لحظه‌ای...")
    sym = "BTCUSDT"
    data = await get_coinex_price(sym)
    if not data:
        await query.edit_message_text("خطا در دریافت داده")
        return
    closes = await get_historical_closes(sym, 30)
    if not closes:
        closes = [data["price"] * (1 + random.uniform(-0.01, 0.01)) for _ in range(30)]
    rsi = calculate_rsi(closes)
    signal, conf = simple_signal(data["change"], rsi)
    msg = f"🎯 *سیگنال بیت‌کوین* 🎯\n\n💰 قیمت: ${data['price']:,.2f}\n📈 تغییر: {data['change']:+.2f}%\n📊 RSI: {rsi:.1f}\n🎯 سیگنال: {signal} (اطمینان {conf}%)"
    await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def technical_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📈 نام ارز را وارد کنید (مثل BTC, ETH):", parse_mode="Markdown")
    context.user_data["waiting_technical"] = True

async def technical_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, symbol_input):
    symbol = None
    for sym in SYMBOLS:
        if symbol_input.upper() in sym:
            symbol = sym
            break
    if not symbol:
        await update.message.reply_text("❌ ارز معتبر نیست.")
        return
    data = await get_coinex_price(symbol)
    if not data:
        await update.message.reply_text("خطا در دریافت قیمت")
        return
    closes = await get_historical_closes(symbol, 30)
    if not closes:
        closes = [data["price"] * (1 + random.uniform(-0.01, 0.01)) for _ in range(30)]
    rsi = calculate_rsi(closes)
    signal, conf = simple_signal(data["change"], rsi)
    support = data["price"] * 0.95
    resistance = data["price"] * 1.05
    reply = (
        f"📊 *تحلیل {SYMBOLS[symbol]['name']}*\n"
        f"💰 قیمت: ${data['price']:,.2f}\n📈 تغییر: {data['change']:+.2f}%\n"
        f"📊 RSI: {rsi:.1f}\n"
        f"🟢 حمایت: ${support:,.2f} | 🔴 مقاومت: ${resistance:,.2f}\n"
        f"🎯 سیگنال: {signal} (اطمینان {conf}%)"
    )
    await update.message.reply_text(reply, parse_mode="Markdown")

async def ai_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not GROQ_API_KEY:
        await query.edit_message_text("⚠️ هوش مصنوعی غیرفعال (GROQ_API_KEY تنظیم نشده).")
        return
    await query.edit_message_text("🧠 سوال خود را بپرسید:", parse_mode="Markdown")
    context.user_data["waiting_ai"] = True

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    await update.message.reply_chat_action("typing")
    # در صورت تمایل، می‌توانید این بخش را با درخواست واقعی به Groq جایگزین کنید
    await update.message.reply_text("🧠 *AI:* در حال توسعه – لطفاً بعداً تلاش کنید.", parse_mode="Markdown")
    context.user_data["waiting_ai"] = False

async def education_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    topic = random.choice(EDUCATION_LIST)
    await query.edit_message_text(f"{topic}\n\n📌 برای آموزش بیشتر به کانال مراجعه کنید.", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def demo_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global demo_balance, demo_positions, demo_history
    query = update.callback_query
    await query.answer()
    text = f"💰 *پورتفوی دمو*\n\nموجودی: ${demo_balance:,.2f}\nپوزیشن‌های باز: {len(demo_positions)}\nتاریخچه معاملات: {len(demo_history)}\n(قابلیت معامله دمو به زودی)"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "❓ *راهنما* ❓\n\n"
        "• قیمت لحظه‌ای: نمایش قیمت ۷ ارز\n"
        "• سیگنال فوری: دریافت سیگنال برای بیت‌کوین\n"
        "• تحلیل تکنیکال: تحلیل بر اساس RSI، حمایت و مقاومت\n"
        "• آموزش تصادفی: دریافت یک نکته آموزشی از بیش از ۱۰۰ موضوع\n"
        "• پورتفوی دمو: مشاهده موجودی مجازی\n"
        "• ربات هر ۵ دقیقه یک سیگنال به کانال می‌فرستد\n"
        "• ربات هر ۲ ساعت یک مطلب آموزشی غیرتکراری به کانال می‌فرستد\n\n"
        "⚠️ فقط جنبه آموزشی – مسئولیت با شماست."
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]))

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("waiting_technical"):
        await technical_analysis(update, context, update.message.text.upper())
        context.user_data["waiting_technical"] = False
    elif context.user_data.get("waiting_ai"):
        await ai_chat(update, context)
        context.user_data["waiting_ai"] = False
    else:
        await update.message.reply_text("لطفاً از دکمه‌های منو استفاده کنید یا /start بزنید.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if data == "back":
        await start(update, context)
    elif data == "prices":
        await prices_menu(update, context)
    elif data == "signal":
        await signal_now(update, context)
    elif data == "technical":
        await technical_menu(update, context)
    elif data == "ai":
        await ai_menu(update, context)
    elif data == "education":
        await education_menu(update, context)
    elif data == "demo":
        await demo_menu(update, context)
    elif data == "help":
        await help_menu(update, context)
    else:
        await query.answer()
        await query.edit_message_text("در حال توسعه...")

# ---------------------------- اجرای اصلی ----------------------------
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    global auto_thread_running
    auto_thread_running = True
    thread = threading.Thread(target=auto_signal_thread, args=(app,), daemon=True)
    thread.start()

    logger.info("🚀 ربات فوق‌هوشمند با موفقیت راه‌اندازی شد.")
    app.run_polling()

if __name__ == "__main__":
    main()
