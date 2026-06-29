from part1 import *
from part2 import *
from typing import Optional, Dict, Any, List, Tuple
# ═══════════════════════════════════════════════════════════
# PART 3: HANDLERS, KEYBOARDS, MESSAGES
# ═══════════════════════════════════════════════════════════

# ════════════════════════════════════════
# FSM STATES
# ════════════════════════════════════════
class BotStates(StatesGroup):
    """Finite State Machine states"""
    waiting_for_ai_question = State()
    waiting_for_payment_receipt = State()
    waiting_for_custom_symbol = State()
    waiting_for_alert_symbol = State()
    waiting_for_alert_price = State()
    waiting_for_alert_type = State()
    waiting_for_feedback = State()
    waiting_for_broadcast = State()

# ════════════════════════════════════════
# KEYBOARD FACTORY (COMPLETE)
# ════════════════════════════════════════
class KeyboardFactory:
    """Professional keyboard builder for all bot menus"""
    
    @staticmethod
    def main_menu(plan: str = "free") -> InlineKeyboardMarkup:
        """Build main menu based on user plan"""
        builder = InlineKeyboardBuilder()
        builder.button(text=f"{E.SEARCH} بازار", callback_data="market")
        builder.button(text=f"{E.BRAIN} هوش مصنوعی", callback_data="ai")
        builder.button(text=f"{E.CHART} تحلیل تکنیکال", callback_data="analysis")
        builder.button(text=f"{E.BELL} هشدار قیمت", callback_data="alerts")
        builder.button(text=f"{E.STAR} واچ‌لیست", callback_data="watchlist")
        builder.button(text=f"{E.CLOCK} زمان تهران", callback_data="time")
        
        if plan == "free":
            builder.button(text=f"{E.CROWN} ارتقا به VIP", callback_data="vip")
        
        builder.button(text=f"{E.ROBOT} درباره", callback_data="about")
        builder.button(text=f"{E.ENVELOPE} پشتیبانی", callback_data="support")
        builder.adjust(3, 2, 2, 2)
        return builder.as_markup()
    
    @staticmethod
    def vip_plans() -> InlineKeyboardMarkup:
        """Build VIP subscription plans"""
        builder = InlineKeyboardBuilder()
        builder.button(
            text=f"{E.CROWN} VIP - {cfg.PLANS['vip']['price']:,} تومان",
            callback_data="buy_vip"
        )
        builder.button(
            text=f"{E.DIAMOND} PRO - {cfg.PLANS['pro']['price']:,} تومان",
            callback_data="buy_pro"
        )
        builder.button(
            text=f"{E.CROWN}{E.DIAMOND} ELITE - {cfg.PLANS['elite']['price']:,} تومان",
            callback_data="buy_elite"
        )
        builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
        builder.adjust(1)
        return builder.as_markup()
    
    @staticmethod
    def analysis_symbols() -> InlineKeyboardMarkup:
        """Build symbol selection for analysis"""
        builder = InlineKeyboardBuilder()
        for sym in cfg.SYMBOLS[:8]:
            name = sym.replace("USDT", "")
            persian = cfg.SYMBOL_NAMES.get(name, name)
            builder.button(
                text=f"{E.CHART} {name} ({persian})",
                callback_data=f"analyze_{sym}"
            )
        builder.button(text=f"{E.SEARCH} نماد دلخواه", callback_data="custom_symbol")
        builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
        builder.adjust(2)
        return builder.as_markup()
    
    @staticmethod
    def timeframes() -> InlineKeyboardMarkup:
        """Build timeframe selection"""
        builder = InlineKeyboardBuilder()
        for tf, name in cfg.TIMEFRAMES.items():
            builder.button(text=f"{E.CLOCK} {name}", callback_data=f"tf_{tf}")
        builder.button(text=f"{E.BACK} بازگشت", callback_data="analysis")
        builder.adjust(2)
        return builder.as_markup()
    
    @staticmethod
    def back_to_main() -> InlineKeyboardMarkup:
        """Simple back to main menu"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{E.BACK} بازگشت", callback_data="main_menu")]
        ])
    
    @staticmethod
    def confirm_payment(plan: str) -> InlineKeyboardMarkup:
        """Build payment confirmation"""
        builder = InlineKeyboardBuilder()
        builder.button(text=f"{E.CHECK} پرداخت کردم", callback_data=f"paid_{plan}")
        builder.button(text=f"{E.BACK} بازگشت", callback_data="vip")
        return builder.as_markup()
    
    @staticmethod
    def admin_payment_actions(payment_id: int) -> InlineKeyboardMarkup:
        """Build admin payment actions"""
        builder = InlineKeyboardBuilder()
        builder.button(text=f"{E.CHECK} تایید", callback_data=f"approve_{payment_id}")
        builder.button(text=f"{E.CROSS} رد", callback_data=f"reject_{payment_id}")
        return builder.as_markup()
    
    @staticmethod
    def alert_types(symbol: str) -> InlineKeyboardMarkup:
        """Build alert type selection"""
        builder = InlineKeyboardBuilder()
        builder.button(text=f"{E.CHART_UP} بالاتر از", callback_data=f"alert_above_{symbol}")
        builder.button(text=f"{E.CHART_DOWN} پایین‌تر از", callback_data=f"alert_below_{symbol}")
        builder.button(text=f"{E.BACK} بازگشت", callback_data="alerts")
        return builder.as_markup()
    
    @staticmethod
    def analysis_actions(symbol: str) -> InlineKeyboardMarkup:
        """Build actions after analysis"""
        builder = InlineKeyboardBuilder()
        builder.button(text=f"{E.BELL} هشدار", callback_data=f"alert_{symbol}")
        builder.button(text=f"{E.STAR} واچ‌لیست", callback_data=f"watch_add_{symbol}")
        builder.button(text=f"{E.ROBOT} تحلیل AI", callback_data=f"ai_analyze_{symbol}")
        builder.button(text=f"{E.BACK} بازگشت", callback_data="analysis")
        builder.adjust(2, 1, 1)
        return builder.as_markup()
    
    @staticmethod
    def about_buttons() -> InlineKeyboardMarkup:
        """Build about section buttons"""
        builder = InlineKeyboardBuilder()
        builder.button(text=f"{E.PHONE} کانال تلگرام", url=cfg.CHANNEL_URL)
        builder.button(text=f"{E.ENVELOPE} ارتباط با سازنده", url=cfg.CREATOR_URL)
        builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
        builder.adjust(1)
        return builder.as_markup()
    
    @staticmethod
    def support_buttons() -> InlineKeyboardMarkup:
        """Build support section buttons"""
        builder = InlineKeyboardBuilder()
        builder.button(text=f"{E.ENVELOPE} پیام به پشتیبان", url=cfg.CREATOR_URL)
        builder.button(text=f"{E.PHONE} کانال", url=cfg.CHANNEL_URL)
        builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
        builder.adjust(2, 1)
        return builder.as_markup()

KB = KeyboardFactory()

# ════════════════════════════════════════
# MESSAGE TEMPLATES (COMPLETE)
# ════════════════════════════════════════
class Messages:
    """Professional message templates for all bot responses"""
    
    @staticmethod
    def welcome(name: str, plan: str, days: int, ai_left: int) -> str:
        """Build welcome message with plan info"""
        now = TT.now()
        plan_icon = E.plan_icon(plan)
        plan_name = {"free": "رایگان", "vip": "VIP", "pro": "PRO", "elite": "ELITE"}.get(plan, "رایگان")
        greeting = TT.greeting()
        
        return f"""
{E.ROCKET}{E.FIRE}{E.ROCKET} *{cfg.APP_NAME}* {E.ROCKET}{E.FIRE}{E.ROCKET}
{E.SPARKLES} نسخه {cfg.APP_VERSION}

{E.ROBOT} {greeting} *{name}* عزیز!
{E.WAVE} به پیشرفته‌ترین ربات تحلیل کریپتو ایران خوش آمدید!

{E.CLOCK} *زمان تهران:* {TT.format(now, 'full')}
{E.GLOBE} *فصل:* {TT.season(now)}
{E.CHART} *سشن معاملاتی:* {TT.session(now)}

{E.DIAMOND}{'━'*20}{E.DIAMOND}
{plan_icon} *پلن فعلی:* {plan_name}
{E.CALENDAR} *اعتبار:* {days} روز
{E.BRAIN} *سوالات AI باقی‌مانده:* {ai_left} عدد
{E.DIAMOND}{'━'*20}{E.DIAMOND}

{E.POINT_DOWN} *منوی اصلی:*
"""
    
    @staticmethod
    def free_ai_limit_warning(used: int, limit: int) -> str:
        """Build warning when free AI limit reached"""
        return f"""
{E.WARNING} *محدودیت هوش مصنوعی*

{E.HOURGLASS} شما *{used}* از *{limit}* سوال رایگان خود را استفاده کرده‌اید.

{E.LOCK} برای دسترسی نامحدود به تحلیل‌های هوش مصنوعی، یکی از پلن‌های VIP را تهیه کنید:

{E.CROWN} *VIP:* ۵۰ تحلیل در روز - *{cfg.PLANS['vip']['price']:,} تومان*
{E.DIAMOND} *PRO:* ۲۰۰ تحلیل در روز - *{cfg.PLANS['pro']['price']:,} تومان*

{E.POINT_DOWN} *برای ارتقا کلیک کنید:*
"""
    
    @staticmethod
    def market_overview(tickers: Dict[str, Dict]) -> str:
        """Build market overview message"""
        now = TT.now()
        text = f"""{E.GLOBE} *خلاصه بازار ارزهای دیجیتال*
{E.CLOCK} {TT.format(now, 'time')} | {TT.format(now, 'date')}
{E.CHART} سشن: {TT.session(now)}

"""
        for symbol, data in tickers.items():
            try:
                price = float(data.get('last', 0))
                change = float(data.get('change_percentage', 0))
                volume = float(data.get('volume', 0))
                emoji = E.change_icon(change)
                name = symbol.replace("USDT", "")
                persian = cfg.SYMBOL_NAMES.get(name, name)
                
                text += f"{emoji} *{name}* ({persian})\n"
                text += f"  {E.MONEY} قیمت: {T.format_price(price)}\n"
                text += f"  {E.CHART} تغییر: {T.format_percent(change)}\n"
                if volume > 0:
                    text += f"  {E.WIND} حجم: {volume:,.0f}\n"
                text += "\n"
            except:
                text += f"{E.CROSS} {symbol}: خطا در دریافت\n\n"
        
        return text
    
    @staticmethod
    def technical_analysis_card(
        symbol: str, price: float, change: float,
        rsi: float, macd_line: float, macd_signal: float, macd_hist: float,
        bb_upper: float, bb_middle: float, bb_lower: float,
        support: float, resistance: float,
        fib_levels: Dict[str, float], moving_averages: Dict[str, float],
        atr: float, stoch_k: float, stoch_d: float,
        ichimoku: Dict[str, float],
        trend: str, volume_analysis: Dict, market_structure: Dict,
        ai_analysis: str = ""
    ) -> str:
        """Build comprehensive technical analysis card"""
        
        change_emoji = E.change_icon(change)
        rsi_status = E.rsi_status(rsi)
        trend_icon = E.trend_icon(trend)
        
        # Fibonacci text
        fib_text = "\n".join([
            f"  {E.POINT_RIGHT} {name}: {value:.4f}"
            for name, value in list(fib_levels.items())[:7]
        ])
        
        # Moving averages text
        ma_text = "\n".join([
            f"  {E.POINT_RIGHT} {name}: {value:.4f}"
            for name, value in list(moving_averages.items())[:4]
        ])
        
        # Ichimoku text
        ichi_text = f"  {E.POINT_RIGHT} Tenkan: {ichimoku.get('tenkan', 0):.4f}\n"
        ichi_text += f"  {E.POINT_RIGHT} Kijun: {ichimoku.get('kijun', 0):.4f}\n"
        ichi_text += f"  {E.POINT_RIGHT} Senkou A: {ichimoku.get('senkou_a', 0):.4f}\n"
        ichi_text += f"  {E.POINT_RIGHT} Senkou B: {ichimoku.get('senkou_b', 0):.4f}"
        
        text = f"""
{E.CHART}{E.CHART}{E.CHART} *تحلیل تکنیکال {symbol}* {E.CHART}{E.CHART}{E.CHART}

{E.MONEY} *قیمت فعلی:* {T.format_price(price)}
{change_emoji} *تغییر ۲۴ ساعته:* {T.format_percent(change)}

{E.THERMOMETER} *اندیکاتورهای اصلی:*
{E.POINT_RIGHT} RSI (14): {rsi_status}
{E.POINT_RIGHT} MACD: {macd_line:.4f} | سیگنال: {macd_signal:.4f} | هیستوگرام: {macd_hist:.4f}
{E.POINT_RIGHT} Stochastic RSI: K={stoch_k:.1f} | D={stoch_d:.1f}
{E.POINT_RIGHT} ATR (14): {atr:.4f}

{E.CHART} *بولینگر باند:*
{E.POINT_RIGHT} بالا: {bb_upper:.4f}
{E.POINT_RIGHT} میانه: {bb_middle:.4f}
{E.POINT_RIGHT} پایین: {bb_lower:.4f}

{E.SHIELD} *سطوح کلیدی:*
{E.POINT_RIGHT} حمایت: ${support:,.4f}
{E.POINT_RIGHT} مقاومت: ${resistance:,.4f}

{E.CRYSTAL} *سطوح فیبوناچی:*
{fib_text}

{E.MAGNET} *میانگین‌های متحرک:*
{ma_text}

{E.SATELLITE} *ایچیموکو:*
{ichi_text}

{E.MOUNTAIN} *تحلیل ساختار بازار:*
{E.POINT_RIGHT} روند: {trend_icon} {trend}
{E.POINT_RIGHT} ساختار: {market_structure.get('structure', 'نامشخص')}
{E.POINT_RIGHT} بایاس: {market_structure.get('bias', 'خنثی')}

{E.WIND} *تحلیل حجم:*
{E.POINT_RIGHT} وضعیت: {volume_analysis.get('trend', 'نرمال')}
{E.POINT_RIGHT} سیگنال: {volume_analysis.get('signal', 'خنثی')}
{E.POINT_RIGHT} نسبت: {volume_analysis.get('ratio', 1)}x

{E.CLOCK} *زمان تحلیل:* {TT.format(TT.now(), 'full')}
{E.INFO} *وضعیت بازار:* {'بازار تعطیل 🕌' if TT.is_weekend() else 'بازار فعال ✅'}
"""
        
        if ai_analysis:
            text += f"""
{E.DIAMOND}{'━'*20}{E.DIAMOND}
{E.ROBOT} *تحلیل هوش مصنوعی:*
{ai_analysis}
{E.DIAMOND}{'━'*20}{E.DIAMOND}
"""
        
        text += f"""
{E.WARNING} *سلب مسئولیت:* این تحلیل صرفاً جنبه اطلاع‌رسانی دارد و سیگنال خرید و فروش نمی‌باشد.
"""
        
        return text
    
    @staticmethod
    def vip_plans_info() -> str:
        """Build VIP plans information"""
        text = f"""
{E.CROWN}{E.CROWN}{E.CROWN} *پلن‌های اشتراک VIP* {E.CROWN}{E.CROWN}{E.CROWN}

"""
        for plan_key in ["vip", "pro", "elite"]:
            plan = cfg.PLANS[plan_key]
            text += f"""
{E.plan_icon(plan_key)} *{plan['name']}*
{E.MONEY} قیمت: *{plan['price']:,} تومان*
{E.CALENDAR} مدت: *{plan['days']} روز*
{E.BRAIN} سوالات AI: *{plan['ai_limit']} در روز*
{E.BELL} هشدارها: *{plan['alerts']} عدد*
{E.STAR} واچ‌لیست: *{plan['watchlist']} عدد*

*امکانات:*
"""
            for feature in plan['features']:
                text += f"  {E.CHECK} {feature}\n"
            text += "\n" + "─" * 30 + "\n"
        
        text += f"""
{E.GIFT} *تخفیف ویژه:* پرداخت سالانه = ۲۰٪ تخفیف
{E.CARD} *شماره کارت:* `{cfg.CARD_NUMBER}`
{E.PERSON} *به نام:* {cfg.CARD_HOLDER}

{E.POINT_DOWN} *برای خرید روی پلن مورد نظر کلیک کنید:*
"""
        return text
    
    @staticmethod
    def payment_instruction(plan_key: str) -> str:
        """Build payment instruction"""
        plan = cfg.PLANS.get(plan_key, cfg.PLANS["vip"])
        
        return f"""
{E.CARD} *پرداخت اشتراک {plan['name']}*

{E.MONEY} *مبلغ قابل پرداخت:* {plan['price']:,} تومان
{E.CALENDAR} *مدت اشتراک:* {plan['days']} روز

{E.BANK} *اطلاعات کارت بانکی:*
{E.POINT_RIGHT} شماره کارت: `{cfg.CARD_NUMBER}`
{E.POINT_RIGHT} به نام: {cfg.CARD_HOLDER}

{E.WARNING} *نکات مهم:*
{E.POINT_RIGHT} مبلغ را دقیقاً به شماره کارت فوق واریز نمایید
{E.POINT_RIGHT} پس از واریز، *رسید پرداخت* را همینجا ارسال کنید
{E.POINT_RIGHT} آیدی تلگرام خود را در توضیحات پرداخت ذکر کنید
{E.POINT_RIGHT} زمان تأیید: ۵ تا ۱۵ دقیقه

{E.ENVELOPE} *پشتیبانی:* {cfg.SUPPORT_CONTACT}

{E.POINT_DOWN} *پس از پرداخت روی دکمه زیر کلیک کنید:*
"""
    
    @staticmethod
    def about_bot() -> str:
        """Build about bot message"""
        return f"""
{E.ROBOT} *{cfg.APP_NAME}*
{E.SPARKLES} نسخه {cfg.APP_VERSION} (Build {cfg.APP_BUILD})

{E.LIGHTNING} پیشرفته‌ترین ربات تحلیل کریپتو ایران

{E.BRAIN} *مشخصات فنی:*
{E.POINT_RIGHT} هوش مصنوعی: Groq (Llama 3.3 70B)
{E.POINT_RIGHT} صرافی: CoinEx
{E.POINT_RIGHT} تحلیل تکنیکال: RSI، MACD، بولینگر، فیبوناچی، MA
{E.POINT_RIGHT} ATR، Stochastic RSI، Ichimoku Cloud
{E.POINT_RIGHT} پرایس اکشن و ساختار بازار
{E.POINT_RIGHT} هشدار هوشمند قیمت
{E.POINT_RIGHT} سیستم اشتراک VIP
{E.POINT_RIGHT} واچ‌لیست و مدیریت سبد
{E.POINT_RIGHT} پشتیبانی ۲۴/۷

{E.CROWN} *تیم توسعه:*
{E.POINT_RIGHT} سازنده: {cfg.CREATOR_USERNAME}
{E.POINT_RIGHT} کانال رسمی: {cfg.CHANNEL_USERNAME}
{E.POINT_RIGHT} پشتیبانی: {cfg.SUPPORT_CONTACT}

{E.CLOCK} *زمان سرور:* {TT.format(TT.now(), 'full')}
{E.GLOBE} *وضعیت:* آنلاین و فعال 🟢
"""
    
    @staticmethod
    def support_info() -> str:
        """Build support information"""
        return f"""
{E.ENVELOPE} *پشتیبانی {cfg.APP_NAME}*

{E.PERSON} *راه‌های ارتباطی:*
{E.POINT_RIGHT} تلگرام: {cfg.SUPPORT_CONTACT}
{E.POINT_RIGHT} کانال: {cfg.CHANNEL_USERNAME}

{E.CLOCK} *ساعات پاسخگویی:*
{E.POINT_RIGHT} همه روزه: ۸ صبح تا ۱۲ شب
{E.POINT_RIGHT} کاربران VIP: پاسخگویی سریع (کمتر از ۱ ساعت)
{E.POINT_RIGHT} کاربران عادی: ۲ تا ۴ ساعت کاری

{E.CARD} *اطلاعات بانکی:*
{E.POINT_RIGHT} شماره کارت: `{cfg.CARD_NUMBER}`
{E.POINT_RIGHT} به نام: {cfg.CARD_HOLDER}

{E.WARNING} لطفاً قبل از تماس، توضیحات کامل مشکل را آماده کنید.
"""
    
    @staticmethod
    def time_info() -> str:
        """Build time information"""
        now = TT.now()
        session = TT.session_details(now)
        
        return f"""
{E.CLOCK} *اطلاعات زمان و تاریخ تهران*

{E.CALENDAR} *تاریخ امروز:*
{E.POINT_RIGHT} {TT.format(now, 'date')}
{E.POINT_RIGHT} {TT.DAYS[now.weekday()]}

{E.WATCH} *ساعت فعلی:* {TT.format(now, 'time')}

{E.GLOBE} *اطلاعات فصلی:*
{E.POINT_RIGHT} فصل: {TT.season(now)}
{E.POINT_RIGHT} تعطیلی: {'بله 🕌' if TT.is_weekend(now) else 'خیر'}
{E.POINT_RIGHT} تعطیل رسمی: {'بله' if TT.is_holiday(now) else 'خیر'}

{E.CHART} *سشن معاملاتی:*
{E.POINT_RIGHT} فعلی: {session['name']}
{E.POINT_RIGHT} شروع: {session['start']} | پایان: {session['end']}
{E.POINT_RIGHT} پیشرفت: {session['progress']}٪
{E.POINT_RIGHT} باقی‌مانده: {session['remaining']} ساعت
"""
    
    @staticmethod
    def watchlist_display(items: List[Dict]) -> str:
        """Build watchlist display"""
        if not items:
            return f"{E.STAR} *واچ‌لیست شما*\n\n{E.INFO} واچ‌لیست شما خالی است.\n{E.POINT_RIGHT} از بخش تحلیل تکنیکال می‌توانید ارزها را اضافه کنید."
        
        text = f"{E.STAR} *واچ‌لیست شما* ({len(items)} ارز)\n\n"
        for i, item in enumerate(items, 1):
            added = TT.format(TT.from_ts(item.get('added_at', 0)), "relative") if item.get('added_at') else "نامشخص"
            text += f"{E.num(i)} {E.CHART} *{item['symbol']}*\n"
            text += f"   {E.CLOCK} {added}\n\n"
        
        return text
    
    @staticmethod
    def alerts_display(alerts: List[Dict]) -> str:
        """Build alerts display"""
        if not alerts:
            return f"{E.BELL} *هشدارهای قیمت*\n\n{E.INFO} هیچ هشدار فعالی ندارید.\n{E.POINT_RIGHT} برای ایجاد هشدار جدید کلیک کنید."
        
        text = f"{E.BELL} *هشدارهای فعال* ({len(alerts)})\n\n"
        for i, alert in enumerate(alerts, 1):
            atype = "بالاتر از ⬆️" if alert.get('alert_type') == 'above' else "پایین‌تر از ⬇️"
            created = TT.format(TT.from_ts(alert.get('created_at', 0)), "relative") if alert.get('created_at') else ""
            text += f"{E.num(i)} {E.CHART} *{alert['symbol']}*\n"
            text += f"   {E.TARGET} {atype}: {alert.get('target_price', 0)}\n"
            if created:
                text += f"   {E.CLOCK} {created}\n"
            text += "\n"
        
        return text
    
    @staticmethod
    def ai_response(answer: str, used: int, limit: int) -> str:
        """Build AI response with usage info"""
        return f"""
{E.ROBOT} *پاسخ هوش مصنوعی:*

{answer}

{E.HOURGLASS} *سوالات باقی‌مانده:* {limit - used} از {limit}
"""

MSG = Messages()

# ════════════════════════════════════════
# MIDDLEWARE & DECORATORS
# ════════════════════════════════════════
def rate_limit(seconds: float = 0.3):
    """Decorator for rate limiting callbacks"""
    def decorator(func):
        last_called = {}
        @wraps(func)
        async def wrapper(callback: CallbackQuery, *args, **kwargs):
            user_id = callback.from_user.id
            now = time.time()
            if user_id in last_called:
                if now - last_called[user_id] < seconds:
                    await callback.answer("⏳ لطفاً کمی صبر کنید...", show_alert=True)
                    return
            last_called[user_id] = now
            return await func(callback, *args, **kwargs)
        return wrapper
    return decorator

def admin_only(func):
    """Decorator for admin-only commands"""
    @wraps(func)
    async def wrapper(callback: CallbackQuery, *args, **kwargs):
        if callback.from_user.id not in cfg.ADMIN_IDS:
            await callback.answer("⛔ دسترسی غیرمجاز!", show_alert=True)
            return
        return await func(callback, *args, **kwargs)
    return wrapper

# ════════════════════════════════════════
# TELEGRAM HANDLERS
# ════════════════════════════════════════
router = Router()

# ── START COMMAND ──
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command - First impression matters!"""
    user_id = message.from_user.id
    full_name = message.from_user.full_name or "کاربر گرامی"
    username = message.from_user.username or ""
    
    # Register user
    await db.upsert_user(user_id, username, full_name)
    
    # Process referral
    args = message.text.split() if message.text else []
    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            referrer_id = int(args[1].replace("ref_", ""))
            if referrer_id != user_id:
                user = await db.get_user(user_id)
                if user and not user.get('referred_by'):
                    await db.execute(
                        "UPDATE users SET referred_by=? WHERE user_id=?",
                        (referrer_id, user_id)
                    )
                    await db.execute(
                        "UPDATE users SET total_referrals=total_referrals+1 WHERE user_id=?",
                        (referrer_id,)
                    )
        except:
            pass
    
    # Get plan info
    plan = await db.get_plan(user_id)
    user = await db.get_user(user_id)
    days_left = 0
    if user and user.get('plan_until'):
        days_left = max(0, int((user['plan_until'] - time.time()) / 86400))
    
    # Get AI usage
    ai_used = await db.get_ai_count(user_id)
    ai_limit = await db.get_ai_limit(user_id)
    ai_left = ai_limit - ai_used
    
    # Send welcome
    welcome_text = MSG.welcome(full_name, plan, days_left, ai_left)
    
    await message.answer(
        welcome_text,
        reply_markup=KB.main_menu(plan),
        parse_mode="HTML"
    )
    await db.log(user_id, "start", f"Plan: {plan}")

# ── MAIN MENU ──
@router.callback_query(F.data == "main_menu")
@rate_limit(0.3)
async def cb_main_menu(callback: CallbackQuery):
    """Return to main menu"""
    plan = await db.get_plan(callback.from_user.id)
    await callback.message.edit_text(
        f"{E.HOME} *منوی اصلی*\n{E.POINT_DOWN} گزینه مورد نظر را انتخاب کنید:",
        reply_markup=KB.main_menu(plan),
        parse_mode="HTML"
    )
    await callback.answer()

# ── MARKET OVERVIEW ──
@router.callback_query(F.data == "market")
@rate_limit(0.5)
async def cb_market(callback: CallbackQuery):
    """Show market overview"""
    await callback.answer("🔄 در حال دریافت اطلاعات بازار...")
    
    tickers = await exchange.get_multiple_tickers(cfg.SYMBOLS)
    
    if not tickers:
        await callback.message.edit_text(
            f"{E.CROSS} خطا در دریافت اطلاعات بازار.",
            reply_markup=KB.back_to_main()
        )
        return
    
    market_text = MSG.market_overview(tickers)
    
    builder = InlineKeyboardBuilder()
    builder.button(text=f"{E.REFRESH} بروزرسانی", callback_data="market")
    builder.button(text=f"{E.CHART} تحلیل تکنیکال", callback_data="analysis")
    builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
    builder.adjust(2, 1)
    
    if len(market_text) > 4000:
        parts = [market_text[i:i+4000] for i in range(0, len(market_text), 4000)]
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                await callback.message.edit_text(part, reply_markup=builder.as_markup(), parse_mode="HTML")
            else:
                await callback.message.answer(part, parse_mode="HTML")
    else:
        await callback.message.edit_text(market_text, reply_markup=builder.as_markup(), parse_mode="HTML")

# ── AI QUESTION ──
@router.callback_query(F.data == "ai")
@rate_limit(1.0)
async def cb_ai(callback: CallbackQuery, state: FSMContext):
    """Start AI question flow"""
    user_id = callback.from_user.id
    can_use, used, limit = await db.can_use_ai(user_id)
    
    if not can_use:
        # Show VIP upgrade prompt
        await callback.message.edit_text(
            MSG.free_ai_limit_warning(used, limit),
            reply_markup=KB.vip_plans(),
            parse_mode="HTML"
        )
        return
    
    await state.set_state(BotStates.waiting_for_ai_question)
    await callback.message.edit_text(
        f"{E.BRAIN} *پرسش از هوش مصنوعی*\n\n"
        f"{E.HOURGLASS} *سوالات باقی‌مانده:* {limit - used} از {limit}\n\n"
        f"{E.POINT_DOWN} لطفاً سوال خود را به صورت متن ارسال کنید:\n\n"
        f"{E.INFO} *مثال:* تحلیل تکنیکال بیت‌کوین را بده\n"
        f"{E.INFO} *مثال:* سیگنال خرید برای اتریوم\n"
        f"{E.INFO} *مثال:* وضعیت بازار امروز را تحلیل کن",
        reply_markup=KB.back_to_main(),
        parse_mode="HTML"
    )

@router.message(StateFilter(BotStates.waiting_for_ai_question))
async def handle_ai_question(message: Message, state: FSMContext):
    """Process AI question"""
    user_id = message.from_user.id
    can_use, used, limit = await db.can_use_ai(user_id)
    
    if not can_use:
        await message.answer(
            MSG.free_ai_limit_warning(used, limit),
            reply_markup=KB.vip_plans(),
            parse_mode="HTML"
        )
        await state.clear()
        return
    
    # Send typing indicator
    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    
    # Get AI response
    answer = await ai.ask(message.text)
    
    # Update counters
    new_count = await db.inc_ai(user_id)
    await db.execute(
        "INSERT INTO ai_history(user_id, question, answer) VALUES(?,?,?)",
        (user_id, message.text[:500], answer[:2000])
    )
    
    # Get fresh limits
    _, _, limit = await db.can_use_ai(user_id)
    
    builder = InlineKeyboardBuilder()
    builder.button(text=f"{E.BRAIN} سوال جدید", callback_data="ai")
    builder.button(text=f"{E.HOME} منوی اصلی", callback_data="main_menu")
    
    response = MSG.ai_response(answer, new_count, limit)
    
    if len(response) > 4000:
        parts = [response[i:i+4000] for i in range(0, len(response), 4000)]
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                await message.answer(part, reply_markup=builder.as_markup(), parse_mode="HTML")
            else:
                await message.answer(part, parse_mode="HTML")
    else:
        await message.answer(response, reply_markup=builder.as_markup(), parse_mode="HTML")
    
    await db.log(user_id, "ai_question", message.text[:100])
    await state.clear()

# ── TECHNICAL ANALYSIS ──
@router.callback_query(F.data == "analysis")
@rate_limit(0.3)
async def cb_analysis(callback: CallbackQuery):
    """Show analysis menu"""
    await callback.message.edit_text(
        f"{E.CHART} *تحلیل تکنیکال*\n\n{E.POINT_DOWN} نماد مورد نظر را انتخاب کنید:",
        reply_markup=KB.analysis_symbols(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("analyze_"))
@rate_limit(1.0)
async def cb_analyze(callback: CallbackQuery):
    """Analyze specific symbol"""
    symbol = callback.data.replace("analyze_", "")
    await callback.answer(f"🔄 در حال تحلیل {symbol}...")
    
    try:
        # Fetch data
        ticker = await exchange.get_ticker(symbol)
        if not ticker:
            raise ValueError("داده یافت نشد")
        
        price = float(ticker.get('last', 0))
        change = float(ticker.get('change_percentage', 0))
        
        klines = await exchange.get_klines(symbol, "1hour", 100)
        if not klines:
            raise ValueError("کندل یافت نشد")
        
        closes = [float(c.get('close', 0)) for c in klines]
        highs = [float(c.get('high', 0)) for c in klines]
        lows = [float(c.get('low', 0)) for c in klines]
        volumes = [float(c.get('volume', 0)) for c in klines]
        
        if len(closes) < 30:
            raise ValueError("داده ناکافی")
        
        # Calculate ALL indicators
        rsi = ta.calculate_rsi(closes)
        macd_line, macd_signal, macd_hist = ta.calculate_macd(closes)
        bb_upper, bb_middle, bb_lower = ta.calculate_bollinger_bands(closes)
        support, resistance = ta.calculate_support_resistance(closes)
        fib_levels = ta.calculate_fibonacci(max(highs), min(lows))
        moving_averages = ta.calculate_moving_averages(closes)
        atr = ta.calculate_atr(highs, lows, closes)
        stoch_k, stoch_d = ta.calculate_stochastic_rsi(closes)
        ichimoku = ta.calculate_ichimoku(highs, lows, closes)
        trend = ta.detect_trend(closes)
        volume_analysis = ta.analyze_volume(volumes, closes)
        market_structure = ta.market_structure(highs, lows)
        
        # AI analysis
        ai_text = await ai.analyze_technically(
            symbol,
            f"قیمت: {price}, RSI: {rsi:.1f}, MACD: {macd_line:.4f}, روند: {trend}"
        )
        
        # Build analysis card
        text = MSG.technical_analysis_card(
            symbol, price, change, rsi, macd_line, macd_signal, macd_hist,
            bb_upper, bb_middle, bb_lower, support, resistance,
            fib_levels, moving_averages, atr, stoch_k, stoch_d,
            ichimoku, trend, volume_analysis, market_structure, ai_text
        )
        
        if len(text) > 4000:
            parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    await callback.message.edit_text(
                        part,
                        reply_markup=KB.analysis_actions(symbol),
                        parse_mode="HTML"
                    )
                else:
                    await callback.message.answer(part, parse_mode="HTML")
        else:
            await callback.message.edit_text(
                text,
                reply_markup=KB.analysis_actions(symbol),
                parse_mode="HTML"
            )
        
        await db.log(callback.from_user.id, "analysis", symbol)
        
    except Exception as e:
        logger.error(f"Analysis error for {symbol}: {e}")
        await callback.message.edit_text(
            f"{E.CROSS} *خطا در تحلیل {symbol}*\n{E.INFO} {str(e)[:100]}",
            reply_markup=KB.back_to_main(),
            parse_mode="HTML"
        )

# ── TIME ──
@router.callback_query(F.data == "time")
@rate_limit(0.3)
async def cb_time(callback: CallbackQuery):
    """Show time information"""
    await callback.message.edit_text(
        MSG.time_info(),
        reply_markup=KB.back_to_main(),
        parse_mode="HTML"
    )
    await callback.answer()

# ── VIP ──
@router.callback_query(F.data == "vip")
@rate_limit(0.3)
async def cb_vip(callback: CallbackQuery):
    """Show VIP plans"""
    await callback.message.edit_text(
        MSG.vip_plans_info(),
        reply_markup=KB.vip_plans(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("buy_"))
@rate_limit(0.3)
async def cb_buy(callback: CallbackQuery):
    """Handle plan purchase"""
    plan_key = callback.data.replace("buy_", "")
    if plan_key not in cfg.PLANS:
        await callback.answer("پلن نامعتبر!", show_alert=True)
        return
    
    await callback.message.edit_text(
        MSG.payment_instruction(plan_key),
        reply_markup=KB.confirm_payment(plan_key),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("paid_"))
@rate_limit(0.3)
async def cb_paid(callback: CallbackQuery, state: FSMContext):
    """Confirm payment"""
    plan_key = callback.data.replace("paid_", "")
    plan = cfg.PLANS.get(plan_key, cfg.PLANS["vip"])
    
    await state.set_state(BotStates.waiting_for_payment_receipt)
    await state.update_data(plan=plan_key, amount=plan['price'])
    
    await callback.message.edit_text(
        f"{E.ENVELOPE} *ارسال رسید*\n\n{E.POINT_DOWN} عکس رسید را ارسال کنید:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{E.BACK} بازگشت", callback_data="vip")]
        ]),
        parse_mode="HTML"
    )

@router.message(StateFilter(BotStates.waiting_for_payment_receipt), F.photo)
async def handle_receipt(message: Message, state: FSMContext):
    """Process payment receipt"""
    user_id = message.from_user.id
    data = await state.get_data()
    plan_key = data.get('plan', 'vip')
    amount = data.get('amount', 0)
    plan = cfg.PLANS.get(plan_key, cfg.PLANS["vip"])
    
    pid = await db.add_payment(user_id, plan_key, amount)
    await db.execute(
        "UPDATE payments SET receipt_file_id=? WHERE id=?",
        (message.photo[-1].file_id, pid)
    )
    
    # Notify admins
    for aid in cfg.ADMIN_IDS:
        try:
            txt = f"{E.BELL} *پرداخت جدید*\n{E.PERSON} {user_id}\n{E.CROWN} {plan['name']}\n{E.MONEY} {amount:,} تومان\n{E.CARD} ID: {pid}"
            await message.bot.send_message(
                aid, txt,
                reply_markup=KB.admin_payment_actions(pid),
                parse_mode="HTML"
            )
            await message.bot.send_photo(aid, message.photo[-1].file_id)
        except:
            pass
    
    await message.answer(
        f"{E.CHECK} *رسید دریافت شد*\n{E.HOURGLASS} در حال بررسی...\n{E.ENVELOPE} {cfg.SUPPORT_CONTACT}",
        reply_markup=KB.back_to_main(),
        parse_mode="HTML"
    )
    await db.log(user_id, "receipt", str(pid))
    await state.clear()

# ── ADMIN PAYMENT ACTIONS ──
@router.callback_query(F.data.startswith("approve_"))
@admin_only
async def cb_approve(callback: CallbackQuery):
    """Admin: approve payment"""
    pid = int(callback.data.replace("approve_", ""))
    if await db.approve_payment(pid, callback.from_user.id):
        p = await db.fetchone("SELECT * FROM payments WHERE id=?", (pid,))
        if p:
            try:
                await callback.bot.send_message(
                    p['user_id'],
                    f"{E.PARTY} *تبریک!*\n{E.CHECK} پرداخت تایید شد!\n{E.CROWN} پلن: {p['plan']}",
                    parse_mode="HTML"
                )
            except:
                pass
        await callback.message.edit_text(f"{E.CHECK} تایید شد.", parse_mode="HTML")
    else:
        await callback.answer("خطا!", show_alert=True)

@router.callback_query(F.data.startswith("reject_"))
@admin_only
async def cb_reject(callback: CallbackQuery):
    """Admin: reject payment"""
    pid = int(callback.data.replace("reject_", ""))
    await db.execute(
        "UPDATE payments SET status='rejected', processed_at=? WHERE id=?",
        (time.time(), pid)
    )
    await callback.message.edit_text(f"{E.CROSS} رد شد.", parse_mode="HTML")

# ── WATCHLIST ──
@router.callback_query(F.data == "watchlist")
@rate_limit(0.3)
async def cb_watchlist(callback: CallbackQuery):
    """Show watchlist"""
    items = await db.get_watchlist(callback.from_user.id)
    text = MSG.watchlist_display(items)
    await callback.message.edit_text(text, reply_markup=KB.back_to_main(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("watch_add_"))
@rate_limit(0.3)
async def cb_watchlist_add(callback: CallbackQuery):
    """Add to watchlist"""
    symbol = callback.data.replace("watch_add_", "")
    if await db.add_watchlist(callback.from_user.id, symbol):
        await callback.answer(f"{E.CHECK} {symbol} اضافه شد!", show_alert=True)
    else:
        await callback.answer(f"{E.CROSS} خطا در افزودن!", show_alert=True)

# ── ALERTS ──
@router.callback_query(F.data == "alerts")
@rate_limit(0.3)
async def cb_alerts(callback: CallbackQuery):
    """Show alerts"""
    alerts = await db.get_active_alerts(callback.from_user.id)
    text = MSG.alerts_display(alerts)
    
    builder = InlineKeyboardBuilder()
    builder.button(text=f"{E.PLUS} هشدار جدید", callback_data="alert_new")
    builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "alert_new")
@rate_limit(0.3)
async def cb_alert_new(callback: CallbackQuery, state: FSMContext):
    """Start new alert"""
    await state.set_state(BotStates.waiting_for_alert_symbol)
    await callback.message.edit_text(
        f"{E.BELL} *هشدار جدید*\n{E.POINT_DOWN} نماد را وارد کنید:\nمثال: BTCUSDT",
        reply_markup=KB.back_to_main(),
        parse_mode="HTML"
    )

@router.message(StateFilter(BotStates.waiting_for_alert_symbol))
async def handle_alert_symbol(message: Message, state: FSMContext):
    """Process alert symbol"""
    symbol = message.text.strip().upper()
    await state.update_data(alert_symbol=symbol)
    await state.set_state(BotStates.waiting_for_alert_type)
    await message.answer(
        f"{E.CHART} *{symbol}*\n{E.POINT_DOWN} نوع هشدار:",
        reply_markup=KB.alert_types(symbol),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("alert_"))
@rate_limit(0.3)
async def cb_alert_type(callback: CallbackQuery, state: FSMContext):
    """Handle alert type"""
    parts = callback.data.replace("alert_", "").split("_", 1)
    atype = parts[0]
    symbol = parts[1] if len(parts) > 1 else "BTCUSDT"
    
    await state.update_data(alert_type=atype)
    await state.set_state(BotStates.waiting_for_alert_price)
    
    await callback.message.edit_text(
        f"{E.TARGET} *قیمت برای {symbol}*\n{E.POINT_DOWN} قیمت را وارد کنید:\nمثال: 45000",
        reply_markup=KB.back_to_main(),
        parse_mode="HTML"
    )

@router.message(StateFilter(BotStates.waiting_for_alert_price))
async def handle_alert_price(message: Message, state: FSMContext):
    """Process alert price"""
    try:
        price = float(message.text.strip().replace(",", ""))
        if price <= 0:
            raise ValueError
        
        data = await state.get_data()
        symbol = data.get('alert_symbol', 'BTCUSDT')
        atype = data.get('alert_type', 'above')
        
        await db.create_alert(message.from_user.id, symbol, price, atype)
        
        await message.answer(
            f"{E.CHECK} *هشدار ثبت شد*\n{E.CHART} {symbol}\n{E.TARGET} {price:,.4f}",
            reply_markup=KB.back_to_main(),
            parse_mode="HTML"
        )
        await db.log(message.from_user.id, "alert_created", f"{symbol} {price}")
    except ValueError:
        await message.answer(
            f"{E.CROSS} عدد معتبر وارد کنید!",
            reply_markup=KB.back_to_main(),
            parse_mode="HTML"
        )
    
    await state.clear()

# ── ABOUT & SUPPORT ──
@router.callback_query(F.data == "about")
@rate_limit(0.3)
async def cb_about(callback: CallbackQuery):
    """Show about"""
    await callback.message.edit_text(
        MSG.about_bot(),
        reply_markup=KB.about_buttons(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "support")
@rate_limit(0.3)
async def cb_support(callback: CallbackQuery):
    """Show support"""
    await callback.message.edit_text(
        MSG.support_info(),
        reply_markup=KB.support_buttons(),
        parse_mode="HTML"
    )
    await callback.answer()

# ════════════════════════════════════════
# END OF PART 3 - CONTINUE TO PART 4
# ════════════════════════════════════════
