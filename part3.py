import Optional, Dict, Any, List, Tuple# ═══════════════════════════════════════════════════════════
# PART 3: COMPLETE HANDLERS, KEYBOARDS, MESSAGES, ADMIN
# ═══════════════════════════════════════════════════════════

from part1 import *
from part2 import *

# ════════════════════════════════════════
# OWNER & ADMIN CONFIG
# ════════════════════════════════════════
OWNER_ID = 6063731196
OWNER_USERNAME = "@Amir92aa"
CHANNEL_ID = "@CryptoPulse606"
CHANNEL_URL = "https://t.me/CryptoPulse606"

def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID

def is_admin(user_id: int) -> bool:
    return user_id == OWNER_ID or user_id in cfg.ADMIN_IDS

# ════════════════════════════════════════
# FSM STATES
# ════════════════════════════════════════
class BotStates(StatesGroup):
    waiting_for_ai_question = State()
    waiting_for_payment_receipt = State()
    waiting_for_custom_symbol = State()
    waiting_for_alert_symbol = State()
    waiting_for_alert_price = State()
    waiting_for_alert_type = State()
    waiting_for_feedback = State()
    waiting_for_broadcast = State()
    waiting_for_risk_level = State()
    waiting_for_withdrawal_wallet = State()
    waiting_for_withdrawal_amount = State()

# ════════════════════════════════════════
# CHANNEL NOTIFIER - COMPLETE
# ════════════════════════════════════════
class ChannelNotifier:
    """Professional channel notification system for @CryptoPulse606"""
    
    @classmethod
    async def _send(cls, bot_instance, text: str, disable_preview: bool = True):
        if not bot_instance:
            return
        try:
            await bot_instance.send_message(
                CHANNEL_ID, text, parse_mode="HTML",
                disable_web_page_preview=disable_preview
            )
        except Exception as e:
            logger.error(f"Channel send error: {e}")
    
    @classmethod
    async def new_user(cls, bot_instance, user_id: int, full_name: str, username: str, plan: str):
        await cls._send(bot_instance, f"""
{E.SPARKLES} *کاربر جدید!*

{E.PERSON} *نام:* {full_name}
{E.CARD} *شناسه:* <code>{user_id}</code>
{E.AT} *یوزرنیم:* @{username if username else 'ندارد'}
{E.CROWN} *پلن:* {plan.upper()}
{E.CLOCK} *زمان:* {TT.format(TT.now(), 'full')}

{E.ROBOT} به {cfg.APP_NAME} پیوست! 🚀
""")
    
    @classmethod
    async def new_payment(cls, bot_instance, user_id: int, plan: str, amount: float, payment_id: int):
        plan_info = cfg.PLANS.get(plan, {})
        await cls._send(bot_instance, f"""
{E.BELL} *پرداخت جدید!*

{E.PERSON} *کاربر:* <code>{user_id}</code>
{E.CROWN} *پلن:* {plan_info.get('name', plan)}
{E.MONEY} *مبلغ:* {amount:,} تومان
{E.CARD} *شناسه:* <code>{payment_id}</code>
{E.CLOCK} *زمان:* {TT.format(TT.now(), 'full')}

{E.HOURGLASS} *وضعیت:* در انتظار تأیید
""")
    
    @classmethod
    async def payment_approved(cls, bot_instance, user_id: int, plan: str, amount: float):
        plan_info = cfg.PLANS.get(plan, {})
        await cls._send(bot_instance, f"""
{E.CHECK} *پرداخت تأیید شد!*

{E.PERSON} *کاربر:* <code>{user_id}</code>
{E.CROWN} *پلن فعال:* {plan_info.get('name', plan)}
{E.MONEY} *مبلغ:* {amount:,} تومان
{E.CLOCK} *زمان:* {TT.format(TT.now(), 'full')}

{E.MONEY} *درآمد:* +{amount:,} تومان 💰
""")
    
    @classmethod
    async def payment_rejected(cls, bot_instance, user_id: int, plan: str, amount: float):
        await cls._send(bot_instance, f"""
{E.CROSS} *پرداخت رد شد!*

{E.PERSON} *کاربر:* <code>{user_id}</code>
{E.MONEY} *مبلغ:* {amount:,} تومان
{E.CLOCK} *زمان:* {TT.format(TT.now(), 'full')}
""")
    
    @classmethod
    async def daily_report(cls, bot_instance, stats: Dict):
        await cls._send(bot_instance, f"""
{E.CHART} *گزارش روزانه {cfg.APP_NAME}*

{E.CALENDAR} *تاریخ:* {TT.format(TT.now(), 'date')}

{E.PERSON} *کاربران:*
{E.POINT_RIGHT} کل: {stats.get('total_users', 0):,}
{E.POINT_RIGHT} ویژه: {stats.get('premium_users', 0):,}
{E.POINT_RIGHT} تبدیل: {stats.get('conversion', 0)}%

{E.MONEY} *مالی:*
{E.POINT_RIGHT} درآمد کل: {stats.get('total_revenue', 0):,} تومان

{E.BRAIN} *AI:* {stats.get('total_ai_queries', 0):,} پرسش

{E.GLOBE} *وضعیت:* آنلاین 🟢
""")
    
    @classmethod
    async def market_alert_channel(cls, bot_instance, symbol: str, price: float, change: float, direction: str):
        emoji = E.change_icon(change)
        dir_emoji = "🟢" if direction == "up" else "🔴"
        await cls._send(bot_instance, f"""
{E.BELL} *هشدار بازار!*

{E.CHART} *{symbol}*
{E.MONEY} *قیمت:* ${price:,.4f}
{emoji} *تغییر ۲۴h:* {change:+.2f}%
{dir_emoji} *جهت:* {'صعودی ⬆️' if direction == 'up' else 'نزولی ⬇️'}

{E.CLOCK} {TT.format(TT.now(), 'time')}
""")
    
    @classmethod
    async def vip_promo(cls, bot_instance):
        await cls._send(bot_instance, f"""
{E.CROWN}{E.CROWN}{E.CROWN} *فرصت ویژه!* {E.CROWN}{E.CROWN}{E.CROWN}

{E.ROBOT} *ربات {cfg.APP_NAME}*
{E.BRAIN} تحلیل حرفه‌ای با هوش مصنوعی Groq
{E.CHART} ۱۵+ اندیکاتور تکنیکال
{E.BELL} هشدار قیمت لحظه‌ای

{E.DIAMOND} *VIP فقط {cfg.PLANS['vip']['price']:,} تومان*

{E.POINT_RIGHT} همین حالا شروع کنید 👇
""")
    
    @classmethod
    async def signal_alert(cls, bot_instance, symbol: str, direction: str, entry: float, sl: float, tp: float):
        dir_text = "LONG 🟢" if direction.upper() == "LONG" else "SHORT 🔴"
        await cls._send(bot_instance, f"""
{E.TARGET} *سیگنال جدید!*

{E.CHART} *{symbol}*
{E.BULL} *نوع:* {dir_text}
{E.MONEY} *ورود:* ${entry:,.4f}
{E.SHIELD} *حد ضرر:* ${sl:,.4f}
{E.TARGET} *هدف:* ${tp:,.4f}

{E.CLOCK} {TT.format(TT.now(), 'full')}

{E.WARNING} *سلب مسئولیت:* این یک سیگنال آموزشی است.
""")


# ════════════════════════════════════════
# KEYBOARD FACTORY - COMPLETE
# ════════════════════════════════════════
class KeyboardFactory:
    """Professional keyboard builder for all menus"""
    
    @staticmethod
    def main_menu(plan: str = "free", user_id: int = 0) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        
        # Row 1 - Market & AI & Analysis
        builder.button(text=f"{E.SEARCH} بازار", callback_data="market")
        builder.button(text=f"{E.BRAIN} هوش مصنوعی", callback_data="ai")
        builder.button(text=f"{E.CHART} تحلیل تکنیکال", callback_data="analysis")
        
        # Row 2 - Alerts & Watchlist & Time
        builder.button(text=f"{E.BELL} هشدار قیمت", callback_data="alerts")
        builder.button(text=f"{E.STAR} واچ‌لیست", callback_data="watchlist")
        builder.button(text=f"{E.CLOCK} زمان تهران", callback_data="time")
        
        # Row 3 - VIP (only for free non-admin users)
        if plan == "free" and not is_admin(user_id):
            builder.button(text=f"{E.CROWN} ارتقا به VIP", callback_data="vip")
            builder.button(text=f"{E.GIFT} دعوت دوستان", callback_data="referral")
        
        # Row 4 - Signals (VIP only)
        if plan != "free" or is_admin(user_id):
            builder.button(text=f"{E.TARGET} سیگنال‌های VIP", callback_data="signals")
        
        # Row 5 - Admin (only for owner/admins)
        if is_admin(user_id):
            builder.button(text=f"{E.SETTINGS} پنل مدیریت", callback_data="admin_panel")
        
        # Row 6 - About & Support
        builder.button(text=f"{E.ROBOT} درباره", callback_data="about")
        builder.button(text=f"{E.ENVELOPE} پشتیبانی", callback_data="support")
        
        builder.adjust(3, 3, 2, 1, 1, 2)
        return builder.as_markup()
    
    @staticmethod
    def admin_panel() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text=f"{E.CARD} پرداخت‌های معلق", callback_data="admin_pending")
        builder.button(text=f"{E.CHART} آمار کامل", callback_data="admin_stats")
        builder.button(text=f"{E.MONEY} درآمد", callback_data="admin_revenue")
        builder.button(text=f"{E.MAIL} ارسال به کانال", callback_data="admin_channel_post")
        builder.button(text=f"{E.PERSON} کاربران ویژه", callback_data="admin_premium_users")
        builder.button(text=f"{E.BELL} هشدارهای فعال", callback_data="admin_alerts_list")
        builder.button(text=f"{E.TARGET} سیگنال‌های فعال", callback_data="admin_signals_list")
        builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
        builder.adjust(1)
        return builder.as_markup()
    
    @staticmethod
    def admin_payment_actions(payment_id: int) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text=f"{E.CHECK} تأیید پرداخت", callback_data=f"approve_{payment_id}")
        builder.button(text=f"{E.CROSS} رد پرداخت", callback_data=f"reject_{payment_id}")
        return builder.as_markup()
    
    @staticmethod
    def vip_plans() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text=f"{E.CROWN} VIP - {cfg.PLANS['vip']['price']:,} تومان", callback_data="buy_vip")
        builder.button(text=f"{E.DIAMOND} PRO - {cfg.PLANS['pro']['price']:,} تومان", callback_data="buy_pro")
        builder.button(text=f"{E.CROWN}{E.DIAMOND} ELITE - {cfg.PLANS['elite']['price']:,} تومان", callback_data="buy_elite")
        builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
        builder.adjust(1)
        return builder.as_markup()
    
    @staticmethod
    def analysis_symbols() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for sym in cfg.SYMBOLS[:10]:
            name = sym.replace("USDT", "")
            persian = cfg.SYMBOL_NAMES.get(name, name)
            builder.button(text=f"{E.CHART} {name}", callback_data=f"analyze_{sym}")
        builder.button(text=f"{E.SEARCH} نماد دلخواه", callback_data="custom_symbol")
        builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
        builder.adjust(3)
        return builder.as_markup()
    
    @staticmethod
    def analysis_actions(symbol: str) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text=f"{E.BELL} هشدار قیمت", callback_data=f"alert_{symbol}")
        builder.button(text=f"{E.STAR} افزودن به واچ‌لیست", callback_data=f"watch_add_{symbol}")
        builder.button(text=f"{E.ROBOT} تحلیل AI", callback_data=f"ai_analyze_{symbol}")
        builder.button(text=f"{E.TARGET} دریافت سیگنال", callback_data=f"signal_{symbol}")
        builder.button(text=f"{E.BACK} بازگشت", callback_data="analysis")
        builder.adjust(2, 2, 1)
        return builder.as_markup()
    
    @staticmethod
    def back_to_main() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{E.BACK} بازگشت", callback_data="main_menu")]
        ])
    
    @staticmethod
    def confirm_payment(plan: str) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text=f"{E.CHECK} پرداخت کردم", callback_data=f"paid_{plan}")
        builder.button(text=f"{E.BACK} بازگشت", callback_data="vip")
        return builder.as_markup()
    
    @staticmethod
    def about_buttons() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text=f"{E.PHONE} کانال تلگرام", url=CHANNEL_URL)
        builder.button(text=f"{E.ENVELOPE} ارتباط با سازنده", url=cfg.CREATOR_URL)
        builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
        builder.adjust(1)
        return builder.as_markup()
    
    @staticmethod
    def support_buttons() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text=f"{E.ENVELOPE} پیام به پشتیبان", url=cfg.CREATOR_URL)
        builder.button(text=f"{E.PHONE} کانال", url=CHANNEL_URL)
        builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
        builder.adjust(2, 1)
        return builder.as_markup()
    
    @staticmethod
    def alert_types(symbol: str) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text=f"{E.CHART_UP} بالاتر از", callback_data=f"alert_above_{symbol}")
        builder.button(text=f"{E.CHART_DOWN} پایین‌تر از", callback_data=f"alert_below_{symbol}")
        builder.button(text=f"{E.BACK} بازگشت", callback_data="alerts")
        return builder.as_markup()
    
    @staticmethod
    def referral_menu(user_id: int) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text=f"{E.LINK} کپی لینک دعوت", callback_data=f"copy_ref_{user_id}")
        builder.button(text=f"{E.CHART} آمار زیرمجموعه", callback_data="ref_stats")
        builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
        return builder.as_markup()

KB = KeyboardFactory()


# ════════════════════════════════════════
# MESSAGE TEMPLATES - COMPLETE
# ════════════════════════════════════════
class Messages:
    """Professional message templates"""
    
    @staticmethod
    def welcome(name: str, plan: str, days: int, ai_left: int) -> str:
        now = TT.now()
        plan_icon = E.plan_icon(plan)
        plan_name = {"free": "رایگان 🆓", "vip": "VIP 👑", "pro": "PRO 💎", "elite": "ELITE 👑💎"}.get(plan, "رایگان")
        greeting = TT.greeting()
        
        # Owner special welcome
        if plan == "elite":
            vip_note = f"\n{E.CROWN} *شما مالک ربات هستید!* تمام امکانات برای شما آزاد است.\n"
        elif plan != "free":
            vip_note = f"\n{E.DIAMOND} شما کاربر ویژه هستید! از تمام امکانات لذت ببرید.\n"
        else:
            vip_note = f"\n{E.WARNING} شما کاربر رایگان هستید. برای دسترسی به امکانات بیشتر، VIP شوید.\n"
        
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
{E.BRAIN} *سوالات AI:* {ai_left} عدد باقی‌مانده
{E.DIAMOND}{'━'*20}{E.DIAMOND}
{vip_note}
{E.POINT_DOWN} *منوی اصلی:*
"""
    
    @staticmethod
    def free_ai_limit_warning(used: int, limit: int) -> str:
        return f"""
{E.WARNING} *محدودیت هوش مصنوعی*

{E.HOURGLASS} شما *{used}* از *{limit}* سوال رایگان خود را استفاده کرده‌اید.

{E.LOCK} برای دسترسی نامحدود به تحلیل‌های هوش مصنوعی:

{E.CROWN} *VIP:* ۵۰ تحلیل در روز - *{cfg.PLANS['vip']['price']:,} تومان*
{E.DIAMOND} *PRO:* ۲۰۰ تحلیل در روز - *{cfg.PLANS['pro']['price']:,} تومان*

{E.POINT_DOWN} *برای ارتقا کلیک کنید:*
"""
    
    @staticmethod
    def market_overview(tickers: Dict[str, Dict]) -> str:
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
                text += f"{E.CROSS} {symbol}: خطا\n\n"
        
        text += f"{E.INFO} *برای تحلیل دقیق از منوی تحلیل تکنیکال استفاده کنید.*"
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
        change_emoji = E.change_icon(change)
        rsi_status = E.rsi_status(rsi)
        trend_icon = E.trend_icon(trend)
        
        fib_text = "\n".join([f"  {E.POINT_RIGHT} {name}: {value:.4f}" for name, value in list(fib_levels.items())[:7]])
        ma_text = "\n".join([f"  {E.POINT_RIGHT} {name}: {value:.4f}" for name, value in list(moving_averages.items())[:4]])
        
        text = f"""
{E.CHART}{E.CHART}{E.CHART} *تحلیل تکنیکال {symbol}* {E.CHART}{E.CHART}{E.CHART}

{E.MONEY} *قیمت:* {T.format_price(price)}
{change_emoji} *تغییر ۲۴h:* {T.format_percent(change)}

{E.THERMOMETER} *اندیکاتورها:*
{E.POINT_RIGHT} RSI (14): {rsi_status}
{E.POINT_RIGHT} MACD: {macd_line:.4f} | Signal: {macd_signal:.4f}
{E.POINT_RIGHT} Stochastic: K={stoch_k:.1f} D={stoch_d:.1f}
{E.POINT_RIGHT} ATR (14): {atr:.4f}

{E.CHART} *بولینگر:* ↑{bb_upper:.4f} ↔{bb_middle:.4f} ↓{bb_lower:.4f}

{E.SHIELD} *حمایت:* ${support:,.4f} | {E.SWORD} *مقاومت:* ${resistance:,.4f}

{E.CRYSTAL} *فیبوناچی:*
{fib_text}

{E.MAGNET} *میانگین‌ها:*
{ma_text}

{E.MOUNTAIN} *روند:* {trend_icon} {trend}
{E.WIND} *حجم:* {volume_analysis.get('signal', 'خنثی')}
{E.BULB} *ساختار:* {market_structure.get('bias', 'خنثی')}

{E.CLOCK} *زمان:* {TT.format(TT.now(), 'full')}
"""
        if ai_analysis:
            text += f"""
{E.DIAMOND}{'━'*20}{E.DIAMOND}
{E.ROBOT} *تحلیل AI:*
{ai_analysis}
"""
        text += f"\n{E.WARNING} *سلب مسئولیت:* این تحلیل آموزشی است، نه سیگنال خرید و فروش."
        return text
    
    @staticmethod
    def vip_plans_info() -> str:
        text = f"{E.CROWN}{E.CROWN}{E.CROWN} *پلن‌های اشتراک* {E.CROWN}{E.CROWN}{E.CROWN}\n\n"
        for pk in ["vip", "pro", "elite"]:
            p = cfg.PLANS[pk]
            text += f"{E.plan_icon(pk)} *{p['name']}*\n"
            text += f"{E.MONEY} {p['price']:,} تومان | {E.CALENDAR} {p['days']} روز\n"
            text += f"{E.BRAIN} {p['ai_limit']} AI | {E.BELL} {p['alerts']} هشدار | {E.STAR} {p['watchlist']} واچ‌لیست\n"
            text += f"{E.CHECK} " + " | ".join(p['features'][:3]) + "\n"
            text += "─" * 30 + "\n"
        text += f"\n{E.CARD} *کارت:* `{cfg.CARD_NUMBER}` | {E.PERSON} *{cfg.CARD_HOLDER}*\n{E.POINT_DOWN} *انتخاب کنید:*"
        return text
    
    @staticmethod
    def payment_instruction(plan_key: str) -> str:
        p = cfg.PLANS.get(plan_key, cfg.PLANS["vip"])
        return f"""
{E.CARD} *پرداخت {p['name']}*

{E.MONEY} *مبلغ:* {p['price']:,} تومان
{E.CALENDAR} *مدت:* {p['days']} روز

{E.BANK} *کارت:* `{cfg.CARD_NUMBER}`
{E.PERSON} *به نام:* {cfg.CARD_HOLDER}

{E.WARNING} مبلغ را دقیقاً واریز کنید.
{E.POINT_DOWN} سپس رسید را ارسال کنید:
"""
    
    @staticmethod
    def about_bot() -> str:
        return f"""
{E.ROBOT} *{cfg.APP_NAME} v{cfg.APP_VERSION}*

{E.LIGHTNING} پیشرفته‌ترین ربات تحلیل کریپتو ایران

{E.BRAIN} *مشخصات فنی:*
{E.POINT_RIGHT} AI: Groq (Llama 3.3 70B)
{E.POINT_RIGHT} صرافی: CoinEx
{E.POINT_RIGHT} ۱۵+ اندیکاتور تکنیکال
{E.POINT_RIGHT} RSI, MACD, Bollinger, Fibonacci, ATR
{E.POINT_RIGHT} Stochastic RSI, Ichimoku Cloud
{E.POINT_RIGHT} پرایس اکشن و ساختار بازار
{E.POINT_RIGHT} هشدار هوشمند قیمت
{E.POINT_RIGHT} سیستم اشتراک VIP

{E.CROWN} *تیم:* {OWNER_USERNAME}
{E.PHONE} *کانال:* {CHANNEL_ID}

{E.CLOCK} {TT.format(TT.now(), 'full')}
"""
    
    @staticmethod
    def support_info() -> str:
        return f"""
{E.ENVELOPE} *پشتیبانی*

{E.PERSON} {cfg.SUPPORT_CONTACT}
{E.PHONE} {CHANNEL_ID}

{E.CLOCK} ۸ صبح تا ۱۲ شب
{E.LIGHTNING} VIP: کمتر از ۱ ساعت

{E.CARD} *کارت:* `{cfg.CARD_NUMBER}`
{E.PERSON} {cfg.CARD_HOLDER}
"""
    
    @staticmethod
    def time_info() -> str:
        now = TT.now()
        session = TT.session_details(now)
        weekend_text = "بله 🕌" if TT.is_weekend(now) else "خیر"
        holiday_text = "بله" if TT.is_holiday(now) else "خیر"
        night_text = "بله 🌙" if TT.is_night_time(now) else "خیر ☀️"
        date_str = TT.format(now, 'date')
        time_str = TT.format(now, 'time')
        season_str = TT.season(now)
        session_name = session['name']
        session_start = session['start']
        session_end = session['end']
        session_progress = session['progress']
        session_remaining = session['remaining']
        day_name = TT.DAYS[now.weekday()]
        
        return f"""
{E.CLOCK} *اطلاعات زمان و تاریخ تهران*

{E.CALENDAR} *تاریخ امروز:*
{E.POINT_RIGHT} {date_str}
{E.POINT_RIGHT} {day_name}

{E.WATCH} *ساعت فعلی:* {time_str}

{E.GLOBE} *اطلاعات فصلی:*
{E.POINT_RIGHT} فصل: {season_str}
{E.POINT_RIGHT} تعطیلی (جمعه): {weekend_text}
{E.POINT_RIGHT} تعطیل رسمی: {holiday_text}
{E.POINT_RIGHT} شب: {night_text}

{E.CHART} *سشن معاملاتی:*
{E.POINT_RIGHT} فعلی: {session_name}
{E.POINT_RIGHT} شروع: {session_start} | پایان: {session_end}
{E.POINT_RIGHT} پیشرفت: {session_progress}٪
{E.POINT_RIGHT} باقی‌مانده: {session_remaining} ساعت

{E.INFO} *راهنما:* بازار کریپتو ۲۴/۷ فعال است.
"""
    
    @staticmethod
    def watchlist_display(items: List[Dict]) -> str:
        if not items:
            return f"{E.STAR} *واچ‌لیست*\n{E.INFO} خالی است."
        text = f"{E.STAR} *واچ‌لیست* ({len(items)})\n\n"
        for i, item in enumerate(items, 1):
            added = TT.format(TT.from_ts(item.get('added_at', 0)), "relative")
            text += f"{E.num(i)} {E.CHART} *{item['symbol']}* ({added})\n"
        return text
    
    @staticmethod
    def alerts_display(alerts: List[Dict]) -> str:
        if not alerts:
            return f"{E.BELL} *هشدارها*\n{E.INFO} هیچ هشدار فعالی ندارید."
        text = f"{E.BELL} *هشدارهای فعال* ({len(alerts)})\n\n"
        for i, a in enumerate(alerts, 1):
            atype = "بالاتر ⬆️" if a.get('alert_type') == 'above' else "پایین‌تر ⬇️"
            created = TT.format(TT.from_ts(a.get('created_at', 0)), "relative")
            text += f"{E.num(i)} {E.CHART} *{a['symbol']}*: {atype} {a.get('target_price', 0)}\n   {E.CLOCK} {created}\n\n"
        return text
    
    @staticmethod
    def ai_response(answer: str, used: int, limit: int) -> str:
        return f"{E.ROBOT} *پاسخ AI:*\n\n{answer}\n\n{E.HOURGLASS} *باقی‌مانده:* {limit - used} از {limit}"

MSG = Messages()


# ════════════════════════════════════════
# DECORATORS
# ════════════════════════════════════════
def rate_limit(seconds: float = 0.3):
    def decorator(func):
        last_called = {}
        @wraps(func)
        async def wrapper(callback: CallbackQuery, *args, **kwargs):
            user_id = callback.from_user.id
            now = time.time()
            if user_id in last_called and now - last_called[user_id] < seconds:
                await callback.answer("⏳ کمی صبر کنید...", show_alert=True)
                return
            last_called[user_id] = now
            return await func(callback, *args, **kwargs)
        return wrapper
    return decorator

def admin_only(func):
    @wraps(func)
    async def wrapper(callback: CallbackQuery, *args, **kwargs):
        if not is_admin(callback.from_user.id):
            await callback.answer("⛔ دسترسی غیرمجاز!", show_alert=True)
            return
        return await func(callback, *args, **kwargs)
    return wrapper


# ════════════════════════════════════════
# ROUTER & HANDLERS
# ════════════════════════════════════════
router = Router()

# ── START ──
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    full_name = message.from_user.full_name or "کاربر"
    username = message.from_user.username or ""
    
    await db.upsert_user(user_id, username, full_name)
    
    args = message.text.split() if message.text else []
    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            referrer_id = int(args[1].replace("ref_", ""))
            if referrer_id != user_id:
                user = await db.get_user(user_id)
                if user and not user.get('referred_by'):
                    await db.execute("UPDATE users SET referred_by=? WHERE user_id=?", (referrer_id, user_id))
                    await db.execute("UPDATE users SET total_referrals=total_referrals+1 WHERE user_id=?", (referrer_id,))
        except: pass
    
    if is_owner(user_id):
        await db.set_plan(user_id, "elite", 36500)
    
    plan = await db.get_plan(user_id)
    user = await db.get_user(user_id)
    days_left = max(0, int(((user.get('plan_until', 0) if user else 0) - time.time())/86400)) if user else 0
    
    ai_used = await db.get_ai_count(user_id)
    ai_limit = await db.get_ai_limit(user_id)
    ai_left = ai_limit - ai_used
    
    await message.answer(MSG.welcome(full_name, plan, days_left, ai_left), reply_markup=KB.main_menu(plan, user_id), parse_mode="HTML")
    await db.log(user_id, "start", plan)
    
    if user and user.get('created_at') and time.time() - user['created_at'] < 60:
        await ChannelNotifier.new_user(bot, user_id, full_name, username, plan)

# ── MAIN MENU ──
@router.callback_query(F.data == "main_menu")
@rate_limit(0.3)
async def cb_main_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    plan = await db.get_plan(user_id)
    if is_owner(user_id) and plan != "elite":
        await db.set_plan(user_id, "elite", 36500)
        plan = "elite"
    await callback.message.edit_text(f"{E.HOME} *منوی اصلی*\n{E.POINT_DOWN} انتخاب کنید:", reply_markup=KB.main_menu(plan, user_id), parse_mode="HTML")
    await callback.answer()

# ── MARKET ──
@router.callback_query(F.data == "market")
@rate_limit(0.5)
async def cb_market(callback: CallbackQuery):
    await callback.answer("در حال دریافت...")
    tickers = await exchange.get_multiple_tickers(cfg.SYMBOLS)
    if not tickers:
        await callback.message.edit_text(f"{E.CROSS} خطا!", reply_markup=KB.back_to_main())
        return
    text = MSG.market_overview(tickers)
    builder = InlineKeyboardBuilder()
    builder.button(text=f"{E.REFRESH} بروزرسانی", callback_data="market")
    builder.button(text=f"{E.CHART} تحلیل", callback_data="analysis")
    builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
    if len(text) > 4000:
        parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for i, p in enumerate(parts):
            if i == len(parts)-1: await callback.message.edit_text(p, reply_markup=builder.as_markup(), parse_mode="HTML")
            else: await callback.message.answer(p, parse_mode="HTML")
    else:
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")

# ── AI ──
@router.callback_query(F.data == "ai")
@rate_limit(1.0)
async def cb_ai(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if is_owner(user_id):
        can_use, used, limit = True, 0, 999999
    else:
        can_use, used, limit = await db.can_use_ai(user_id)
    if not can_use:
        await callback.message.edit_text(MSG.free_ai_limit_warning(used, limit), reply_markup=KB.vip_plans(), parse_mode="HTML")
        return
    await state.set_state(BotStates.waiting_for_ai_question)
    await callback.message.edit_text(f"{E.BRAIN} *پرسش از AI*\n{E.HOURGLASS} {limit-used} سوال باقی‌مانده\n{E.POINT_DOWN} سوال بفرستید:", reply_markup=KB.back_to_main(), parse_mode="HTML")

@router.message(StateFilter(BotStates.waiting_for_ai_question))
async def handle_ai(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if is_owner(user_id):
        can_use, used, limit = True, 0, 999999
    else:
        can_use, used, limit = await db.can_use_ai(user_id)
    if not can_use:
        await message.answer(MSG.free_ai_limit_warning(used, limit), reply_markup=KB.vip_plans(), parse_mode="HTML")
        await state.clear()
        return
    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    answer = await ai.ask(message.text)
    if not is_owner(user_id):
        new_count = await db.inc_ai(user_id)
    else:
        new_count = 0
    await db.execute("INSERT INTO ai_history(user_id, question, answer) VALUES(?,?,?)", (user_id, message.text[:500], answer[:2000]))
    builder = InlineKeyboardBuilder()
    builder.button(text=f"{E.BRAIN} سوال جدید", callback_data="ai")
    builder.button(text=f"{E.HOME} منوی اصلی", callback_data="main_menu")
    response = MSG.ai_response(answer, new_count, limit)
    if len(response) > 4000:
        parts = [response[i:i+4000] for i in range(0, len(response), 4000)]
        for i, p in enumerate(parts):
            if i == len(parts)-1: await message.answer(p, reply_markup=builder.as_markup(), parse_mode="HTML")
            else: await message.answer(p, parse_mode="HTML")
    else:
        await message.answer(response, reply_markup=builder.as_markup(), parse_mode="HTML")
    await db.log(user_id, "ai", message.text[:100])
    await state.clear()
    # ── ANALYSIS ──
@router.callback_query(F.data == "analysis")
@rate_limit(0.3)
async def cb_analysis(callback: CallbackQuery):
    await callback.message.edit_text(f"{E.CHART} *تحلیل تکنیکال*\n{E.POINT_DOWN} انتخاب کنید:", reply_markup=KB.analysis_symbols(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("analyze_"))
@rate_limit(1.0)
async def cb_analyze(callback: CallbackQuery):
    symbol = callback.data.replace("analyze_", "")
    await callback.answer(f"تحلیل {symbol}...")
    try:
        ticker = await exchange.get_ticker(symbol)
        if not ticker: raise ValueError("داده نیست")
        price = float(ticker.get('last', 0))
        change = float(ticker.get('change_percentage', 0))
        klines = await exchange.get_klines(symbol, "1hour", 100)
        if not klines: raise ValueError("کندل نیست")
        closes = [float(c.get('close',0)) for c in klines]
        highs = [float(c.get('high',0)) for c in klines]
        lows = [float(c.get('low',0)) for c in klines]
        volumes = [float(c.get('volume',0)) for c in klines]
        if len(closes) < 30: raise ValueError("داده کم")
        
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
        
        ai_text = await ai.analyze_technically(symbol, f"قیمت:{price} RSI:{rsi:.1f} روند:{trend}")
        
        text = MSG.technical_analysis_card(symbol, price, change, rsi, macd_line, macd_signal, macd_hist, bb_upper, bb_middle, bb_lower, support, resistance, fib_levels, moving_averages, atr, stoch_k, stoch_d, ichimoku, trend, volume_analysis, market_structure, ai_text)
        
        if len(text) > 4000:
            parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
            for i, p in enumerate(parts):
                if i == len(parts)-1: await callback.message.edit_text(p, reply_markup=KB.analysis_actions(symbol), parse_mode="HTML")
                else: await callback.message.answer(p, parse_mode="HTML")
        else:
            await callback.message.edit_text(text, reply_markup=KB.analysis_actions(symbol), parse_mode="HTML")
        await db.log(callback.from_user.id, "analysis", symbol)
    except Exception as e:
        await callback.message.edit_text(f"{E.CROSS} خطا: {str(e)[:100]}", reply_markup=KB.back_to_main(), parse_mode="HTML")

# ── TIME ──
@router.callback_query(F.data == "time")
async def cb_time(callback: CallbackQuery):
    await callback.message.edit_text(MSG.time_info(), reply_markup=KB.back_to_main(), parse_mode="HTML")
    await callback.answer()

# ── VIP ──
@router.callback_query(F.data == "vip")
async def cb_vip(callback: CallbackQuery):
    await callback.message.edit_text(MSG.vip_plans_info(), reply_markup=KB.vip_plans(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("buy_"))
async def cb_buy(callback: CallbackQuery):
    plan = callback.data.replace("buy_", "")
    if plan not in cfg.PLANS:
        await callback.answer("نامعتبر!", show_alert=True)
        return
    await callback.message.edit_text(MSG.payment_instruction(plan), reply_markup=KB.confirm_payment(plan), parse_mode="HTML")

@router.callback_query(F.data.startswith("paid_"))
async def cb_paid(callback: CallbackQuery, state: FSMContext):
    plan = callback.data.replace("paid_", "")
    p = cfg.PLANS.get(plan, cfg.PLANS["vip"])
    await state.set_state(BotStates.waiting_for_payment_receipt)
    await state.update_data(plan=plan, amount=p['price'])
    await callback.message.edit_text(f"{E.ENVELOPE} *رسید را ارسال کنید*", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{E.BACK} بازگشت", callback_data="vip")]]), parse_mode="HTML")

@router.message(StateFilter(BotStates.waiting_for_payment_receipt), F.photo)
async def handle_receipt(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    plan = data.get('plan', 'vip')
    amount = data.get('amount', 0)
    p = cfg.PLANS.get(plan, cfg.PLANS["vip"])
    pid = await db.add_payment(user_id, plan, amount)
    await db.execute("UPDATE payments SET receipt_file_id=? WHERE id=?", (message.photo[-1].file_id, pid))
    if bot:
        try:
            await bot.send_message(OWNER_ID, f"{E.BELL} *پرداخت*\n{E.PERSON} {user_id}\n{E.CROWN} {p['name']}\n{E.MONEY} {amount:,} تومان\n{E.CARD} ID:{pid}", reply_markup=KB.admin_payment_actions(pid), parse_mode="HTML")
            await bot.send_photo(OWNER_ID, message.photo[-1].file_id)
        except: pass
    await ChannelNotifier.new_payment(bot, user_id, plan, amount, pid)
    await message.answer(f"{E.CHECK} *رسید دریافت شد*\n{E.HOURGLASS} در حال بررسی...", reply_markup=KB.back_to_main(), parse_mode="HTML")
    await db.log(user_id, "receipt", str(pid))
    await state.clear()
# ── ADMIN PAYMENT ACTIONS ──
@router.callback_query(F.data.startswith("approve_"))
async def cb_approve(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ دسترسی غیرمجاز!", show_alert=True)
        return
    pid = int(callback.data.replace("approve_", ""))
    if await db.approve_payment(pid, callback.from_user.id):
        p = await db.fetchone("SELECT * FROM payments WHERE id=?", (pid,))
        if p:
            try: await callback.bot.send_message(p['user_id'], f"{E.PARTY} *تبریک!*\n{E.CHECK} پرداخت تأیید شد!\n{E.CROWN} پلن: {p['plan']}", parse_mode="HTML")
            except: pass
            await ChannelNotifier.payment_approved(callback.bot, p['user_id'], p['plan'], p['amount'])
        await callback.message.edit_text(f"{E.CHECK} تأیید شد.", parse_mode="HTML")
    else:
        await callback.answer("خطا!", show_alert=True)

@router.callback_query(F.data.startswith("reject_"))
async def cb_reject(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ دسترسی غیرمجاز!", show_alert=True)
        return
    pid = int(callback.data.replace("reject_", ""))
    await db.execute("UPDATE payments SET status='rejected', processed_at=? WHERE id=?", (time.time(), pid))
    p = await db.fetchone("SELECT * FROM payments WHERE id=?", (pid,))
    if p: await ChannelNotifier.payment_rejected(callback.bot, p['user_id'], p['plan'], p['amount'])
    await callback.message.edit_text(f"{E.CROSS} رد شد.", parse_mode="HTML")

# ── WATCHLIST ──
@router.callback_query(F.data == "watchlist")
async def cb_watchlist(callback: CallbackQuery):
    items = await db.get_watchlist(callback.from_user.id)
    await callback.message.edit_text(MSG.watchlist_display(items), reply_markup=KB.back_to_main(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("watch_add_"))
async def cb_watch_add(callback: CallbackQuery):
    sym = callback.data.replace("watch_add_", "")
    if await db.add_watchlist(callback.from_user.id, sym):
        await callback.answer(f"{E.CHECK} {sym} اضافه شد!", show_alert=True)
    else:
        await callback.answer(f"{E.CROSS} خطا!", show_alert=True)

# ── ALERTS ──
@router.callback_query(F.data == "alerts")
async def cb_alerts(callback: CallbackQuery):
    alerts = await db.get_active_alerts(callback.from_user.id)
    builder = InlineKeyboardBuilder()
    builder.button(text=f"{E.PLUS} جدید", callback_data="alert_new")
    builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
    await callback.message.edit_text(MSG.alerts_display(alerts), reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "alert_new")
async def cb_alert_new(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BotStates.waiting_for_alert_symbol)
    await callback.message.edit_text(f"{E.BELL} *هشدار جدید*\n{E.POINT_DOWN} نماد را وارد کنید:", reply_markup=KB.back_to_main(), parse_mode="HTML")

@router.message(StateFilter(BotStates.waiting_for_alert_symbol))
async def handle_alert_symbol(message: Message, state: FSMContext):
    sym = message.text.strip().upper()
    await state.update_data(alert_symbol=sym)
    await state.set_state(BotStates.waiting_for_alert_type)
    await message.answer(f"{E.CHART} *{sym}*\n{E.POINT_DOWN} نوع:", reply_markup=KB.alert_types(sym), parse_mode="HTML")

@router.callback_query(F.data.startswith("alert_"))
async def cb_alert_type(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.replace("alert_", "").split("_", 1)
    atype, sym = parts[0], parts[1] if len(parts) > 1 else "BTCUSDT"
    await state.update_data(alert_type=atype)
    await state.set_state(BotStates.waiting_for_alert_price)
    await callback.message.edit_text(f"{E.TARGET} *قیمت برای {sym}*\n{E.POINT_DOWN} وارد کنید:", reply_markup=KB.back_to_main(), parse_mode="HTML")

@router.message(StateFilter(BotStates.waiting_for_alert_price))
async def handle_alert_price(message: Message, state: FSMContext):
    try:
        price = float(message.text.strip().replace(",", ""))
        if price <= 0: raise ValueError
        data = await state.get_data()
        sym, atype = data.get('alert_symbol', 'BTCUSDT'), data.get('alert_type', 'above')
        await db.create_alert(message.from_user.id, sym, price, atype)
        await message.answer(f"{E.CHECK} *ثبت شد*\n{E.CHART} {sym}\n{E.TARGET} {price:,.4f}", reply_markup=KB.back_to_main(), parse_mode="HTML")
        await db.log(message.from_user.id, "alert", f"{sym} {price}")
    except:
        await message.answer(f"{E.CROSS} عدد معتبر وارد کنید!", reply_markup=KB.back_to_main(), parse_mode="HTML")
    await state.clear()

# ── SIGNALS (VIP) ──
@router.callback_query(F.data == "signals")
async def cb_signals(callback: CallbackQuery):
    user_id = callback.from_user.id
    plan = await db.get_plan(user_id)
    if plan == "free" and not is_admin(user_id):
        await callback.answer(f"{E.LOCK} مخصوص VIP!", show_alert=True)
        return
    signals = await db.fetchall("SELECT * FROM signals WHERE status='active' ORDER BY created_at DESC LIMIT 5")
    if not signals:
        await callback.message.edit_text(f"{E.TARGET} *سیگنال‌های VIP*\n{E.INFO} سیگنال فعالی نیست.", reply_markup=KB.back_to_main(), parse_mode="HTML")
        return
    text = f"{E.TARGET} *سیگنال‌های فعال*\n\n"
    for s in signals:
        dir_text = "LONG 🟢" if s['direction'].upper() == "LONG" else "SHORT 🔴"
        text += f"{E.CHART} *{s['symbol']}* | {dir_text}\n"
        text += f"{E.MONEY} ورود: {s['entry_price']} | {E.SHIELD} SL: {s['stop_loss']}\n"
        text += f"{E.TARGET} TP: {s.get('take_profit1', 0)}\n\n"
    await callback.message.edit_text(text, reply_markup=KB.back_to_main(), parse_mode="HTML")
    await callback.answer()

# ── REFERRAL ──
@router.callback_query(F.data == "referral")
async def cb_referral(callback: CallbackQuery):
    user_id = callback.from_user.id
    bot_info = await bot.get_me() if bot else None
    bot_username = bot_info.username if bot_info else "OstadBot"
    ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    refs = await db.fetchval("SELECT total_referrals FROM users WHERE user_id=?", (user_id,), 0)
    text = f"""
{E.GIFT} *دعوت دوستان*

{E.LINK} *لینک شما:*
`{ref_link}`

{E.PERSON} *زیرمجموعه:* {refs} نفر
{E.MONEY} *پاداش:* ۲۰٪ از خرید زیرمجموعه

{E.POINT_RIGHT} لینک رو به اشتراک بذارید!
"""
    await callback.message.edit_text(text, reply_markup=KB.referral_menu(user_id), parse_mode="HTML")
    await callback.answer()

# ── ABOUT ──
@router.callback_query(F.data == "about")
async def cb_about(callback: CallbackQuery):
    await callback.message.edit_text(MSG.about_bot(), reply_markup=KB.about_buttons(), parse_mode="HTML")
    await callback.answer()

# ── SUPPORT ──
@router.callback_query(F.data == "support")
async def cb_support(callback: CallbackQuery):
    await callback.message.edit_text(MSG.support_info(), reply_markup=KB.support_buttons(), parse_mode="HTML")
    await callback.answer()

# ── ADMIN PANEL ──
@router.callback_query(F.data == "admin_panel")
@admin_only
async def cb_admin_panel(callback: CallbackQuery):
    stats = await db.stats()
    pending = await db.count("payments", "status='pending'")
    text = f"""
{E.SETTINGS} *پنل مدیریت*

{E.CROWN} مالک: {OWNER_USERNAME}
{E.PERSON} کاربران: {stats.get('total_users', 0):,}
{E.DIAMOND} ویژه: {stats.get('premium_users', 0):,}
{E.MONEY} درآمد: {stats.get('total_revenue', 0):,} تومان
{E.CARD} پرداخت‌های معلق: {pending}
{E.CLOCK} {TT.format(TT.now(), 'full')}
"""
    await callback.message.edit_text(text, reply_markup=KB.admin_panel(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "admin_pending")
@admin_only
async def cb_admin_pending(callback: CallbackQuery):
    payments = await db.fetchall("SELECT * FROM payments WHERE status='pending' ORDER BY created_at DESC LIMIT 10")
    if not payments:
        await callback.message.edit_text(f"{E.INFO} پرداخت معلقی نیست.", reply_markup=KB.back_to_main())
        return
    text = f"{E.CARD} *پرداخت‌های معلق*\n\n"
    builder = InlineKeyboardBuilder()
    for p in payments:
        pinfo = cfg.PLANS.get(p['plan'], {})
        text += f"{E.PERSON} {p['user_id']} | {pinfo.get('name',p['plan'])} | {p['amount']:,} تومان\n"
        text += f"{E.CARD} ID: {p['id']}\n\n"
        builder.button(text=f"پرداخت {p['id']}", callback_data=f"admin_review_{p['id']}")
    builder.button(text=f"{E.BACK} بازگشت", callback_data="admin_panel")
    builder.adjust(1)
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("admin_review_"))
@admin_only
async def cb_admin_review(callback: CallbackQuery):
    pid = int(callback.data.replace("admin_review_", ""))
    p = await db.fetchone("SELECT * FROM payments WHERE id=?", (pid,))
    if not p:
        await callback.answer("یافت نشد!", show_alert=True)
        return
    pinfo = cfg.PLANS.get(p['plan'], {})
    text = f"{E.CARD} *پرداخت #{pid}*\n{E.PERSON} {p['user_id']}\n{E.CROWN} {pinfo.get('name',p['plan'])}\n{E.MONEY} {p['amount']:,} تومان\n{E.CLOCK} {TT.format(TT.from_ts(p['created_at']), 'full')}"
    await callback.message.edit_text(text, reply_markup=KB.admin_payment_actions(pid), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "admin_stats")
@admin_only
async def cb_admin_stats(callback: CallbackQuery):
    stats = await db.stats()
    text = f"{E.CHART} *آمار*\n{E.PERSON} کاربران: {stats.get('total_users', 0):,}\n{E.DIAMOND} ویژه: {stats.get('premium_users', 0):,}\n{E.MONEY} درآمد: {stats.get('total_revenue', 0):,} تومان\n{E.BRAIN} AI: {stats.get('total_ai_queries', 0):,}"
    await callback.message.edit_text(text, reply_markup=KB.back_to_main(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "admin_revenue")
@admin_only
async def cb_admin_revenue(callback: CallbackQuery):
    total = await db.fetchval("SELECT COALESCE(SUM(amount),0) FROM payments WHERE status='approved'", default=0)
    today = await db.fetchval("SELECT COALESCE(SUM(amount),0) FROM payments WHERE status='approved' AND date(processed_at,'unixepoch')=date('now')", default=0)
    text = f"{E.MONEY} *درآمد*\n{E.DIAMOND} کل: {total:,} تومان\n{E.CHART} امروز: {today:,} تومان"
    await callback.message.edit_text(text, reply_markup=KB.back_to_main(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "admin_channel_post")
@admin_only
async def cb_admin_channel_post(callback: CallbackQuery):
    await ChannelNotifier.vip_promo(callback.bot)
    await callback.answer("✅ ارسال شد!", show_alert=True)

# ════════════════════════════════════════
# END OF PART 3
# ════════════════════════════════════════
