# ═══════════════════════════════════════════════════════════
# PART 3: HANDLERS, KEYBOARDS, MESSAGES, FASTAPI, MAIN
# ═══════════════════════════════════════════════════════════

# IMPORTS FOR PART 3
import os
import json
import time
import asyncio
import logging
import traceback
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
from functools import wraps

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    Update, BotCommand, BotCommandScopeDefault
)
from aiogram.enums import ParseMode, ChatAction
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties

# Import shared components from part1 and part2
from part1 import *
from part2 import *

logger = logging.getLogger("OstadBot")

# ════════════════════════════════════════
# SECTION 14: FSM STATES
# ════════════════════════════════════════

class BotStates(StatesGroup):
    """Finite State Machine states for bot conversations"""
    waiting_for_ai_question = State()
    waiting_for_payment_receipt = State()
    waiting_for_payment_amount = State()
    waiting_for_wallet_address = State()
    waiting_for_custom_symbol = State()
    waiting_for_alert_symbol = State()
    waiting_for_alert_price = State()
    waiting_for_alert_type = State()
    waiting_for_feedback = State()
    waiting_for_broadcast_message = State()
    waiting_for_broadcast_confirm = State()
    waiting_for_risk_level = State()
    waiting_for_language = State()
    waiting_for_withdrawal_amount = State()
    waiting_for_withdrawal_wallet = State()

# ════════════════════════════════════════
# SECTION 15: KEYBOARD FACTORY
# ════════════════════════════════════════

class KeyboardFactory:
    """Factory class for building all bot keyboards"""
    
    @staticmethod
    def main_menu(plan: str = "free") -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text=f"{E.SEARCH} بازار", callback_data="menu_market")
        builder.button(text=f"{E.BRAIN} هوش مصنوعی", callback_data="menu_ai")
        builder.button(text=f"{E.CHART} تحلیل تکنیکال", callback_data="menu_analysis")
        builder.button(text=f"{E.BELL} هشدار قیمت", callback_data="menu_alerts")
        builder.button(text=f"{E.STAR} واچ‌لیست", callback_data="menu_watchlist")
        builder.button(text=f"{E.CLOCK} زمان تهران", callback_data="menu_time")
        if plan == PlanType.FREE.value:
            builder.button(text=f"{E.CROWN} ارتقا به VIP", callback_data="menu_vip")
        builder.button(text=f"{E.ROBOT} درباره ما", callback_data="menu_about")
        builder.button(text=f"{E.ENVELOPE} پشتیبانی", callback_data="menu_support")
        builder.adjust(3, 2, 2, 2)
        return builder.as_markup()
    
    @staticmethod
    def admin_menu() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text=f"{E.PERSON} کاربران", callback_data="admin_users")
        builder.button(text=f"{E.CARD} پرداخت‌ها", callback_data="admin_payments")
        builder.button(text=f"{E.CHART} سیگنال‌ها", callback_data="admin_signals")
        builder.button(text=f"{E.BELL} هشدارها", callback_data="admin_alerts")
        builder.button(text=f"{E.SETTINGS} تنظیمات", callback_data="admin_settings")
        builder.button(text=f"{E.MAIL} ارسال همگانی", callback_data="admin_broadcast")
        builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
        builder.adjust(2, 2, 2, 1)
        return builder.as_markup()
    
    @staticmethod
    def vip_plans() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text=f"{E.CROWN} VIP - {PLANS['vip']['price']:,} تومان", callback_data="buy_vip")
        builder.button(text=f"{E.DIAMOND} PRO - {PLANS['pro']['price']:,} تومان", callback_data="buy_pro")
        builder.button(text=f"{E.CROWN}{E.DIAMOND} ELITE - {PLANS['elite']['price']:,} تومان", callback_data="buy_elite")
        builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
        builder.adjust(1)
        return builder.as_markup()
    
    @staticmethod
    def analysis_symbols() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for sym in DEFAULT_SYMBOLS[:10]:
            name = sym.replace("USDT", "")
            persian = SYMBOL_NAMES_PERSIAN.get(name, name)
            builder.button(text=f"{E.CHART} {name} ({persian})", callback_data=f"analyze_{sym}")
        builder.button(text=f"{E.SEARCH} نماد دلخواه", callback_data="custom_symbol")
        builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
        builder.adjust(2)
        return builder.as_markup()
    
    @staticmethod
    def timeframes() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for tf, name in list(TIMEFRAMES.items())[:6]:
            builder.button(text=f"{E.CLOCK} {name}", callback_data=f"tf_{tf}")
        builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
        builder.adjust(3)
        return builder.as_markup()
    
    @staticmethod
    def back_to_main() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{E.BACK} بازگشت به منوی اصلی", callback_data="main_menu")]
        ])
    
    @staticmethod
    def confirm_payment(plan: str) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text=f"{E.CHECK} پرداخت کردم ✅", callback_data=f"confirm_pay_{plan}")
        builder.button(text=f"{E.BACK} بازگشت", callback_data="menu_vip")
        return builder.as_markup()
    
    @staticmethod
    def admin_payment_actions(payment_id: int) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text=f"{E.CHECK} تایید", callback_data=f"admin_approve_{payment_id}")
        builder.button(text=f"{E.CROSS} رد", callback_data=f"admin_reject_{payment_id}")
        return builder.as_markup()
    
    @staticmethod
    def alert_types(symbol: str) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text=f"{E.CHART_UP} بالاتر از", callback_data=f"alerttype_above_{symbol}")
        builder.button(text=f"{E.CHART_DOWN} پایین‌تر از", callback_data=f"alerttype_below_{symbol}")
        builder.button(text=f"{E.BACK} بازگشت", callback_data="menu_alerts")
        return builder.as_markup()
    
    @staticmethod
    def risk_levels() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text=f"🟢 پایین", callback_data="risk_low")
        builder.button(text=f"🟡 متوسط", callback_data="risk_medium")
        builder.button(text=f"🔴 بالا", callback_data="risk_high")
        builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
        return builder.as_markup()
    
    @staticmethod
    def refresh_and_back(refresh_callback: str = "main_menu") -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text=f"{E.REFRESH} بروزرسانی", callback_data=refresh_callback)
        builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
        return builder.as_markup()

KB = KeyboardFactory()

# ════════════════════════════════════════
# SECTION 16: MESSAGE TEMPLATE ENGINE
# ════════════════════════════════════════

class MessageTemplateEngine:
    """Engine for building all bot message templates"""
    
    @staticmethod
    def welcome_message(user_name: str, plan: str, days_left: int) -> str:
        now = TT.now()
        plan_icon = E.plan_icon(plan)
        plan_name = T.PLAN_NAMES.get(plan, "رایگان")
        greeting = TT.greeting(now)
        return f"""
{E.ROCKET}{E.FIRE}{E.ROCKET} *{APP_NAME}* {E.ROCKET}{E.FIRE}{E.ROCKET}
{E.SPARKLES} نسخه {APP_VERSION}

{E.ROBOT} {greeting} *{user_name}* عزیز!
{E.WAVE} به پیشرفته‌ترین ربات تحلیل کریپتو خوش آمدید!

{E.CLOCK} *زمان تهران:* {TT.format(now, 'full')}
{E.GLOBE} *فصل:* {TT.get_season(now)}
{E.CHART} *سشن معاملاتی:* {TT.trading_session(now)}

{E.DIAMOND}{'━'*20}{E.DIAMOND}
{plan_icon} *پلن فعلی:* {plan_name}
{E.CALENDAR} *اعتبار باقی‌مانده:* {days_left} روز
{E.DIAMOND}{'━'*20}{E.DIAMOND}

{E.POINT_DOWN} *لطفاً از منوی زیر گزینه مورد نظر را انتخاب کنید:*
"""
    
    @staticmethod
    def market_overview(tickers: Dict[str, Dict]) -> str:
        now = TT.now()
        text = f"""{E.GLOBE} *خلاصه بازار ارزهای دیجیتال*
{E.CLOCK} {TT.format(now, 'time')} | {TT.format(now, 'date')}
{E.CHART} سشن: {TT.trading_session(now)}

"""
        for symbol, data in tickers.items():
            try:
                price = float(data.get('last', 0))
                change = float(data.get('change_percentage', 0))
                volume = float(data.get('volume', 0))
                emoji = E.change_icon(change)
                name = symbol.replace("USDT", "")
                persian = SYMBOL_NAMES_PERSIAN.get(name, name)
                text += f"{emoji} *{name}* ({persian})\n"
                text += f"  {E.MONEY} قیمت: ${T.format_price(price)}\n"
                text += f"  {E.CHART} تغییر: {T.format_percent(change)}\n"
                text += f"  {E.WAVE} حجم: {T.format_volume(volume)}\n\n"
            except:
                text += f"{E.CROSS} {symbol}: خطا در دریافت\n\n"
        return text
    
    @staticmethod
    def technical_analysis_card(symbol, price, change, rsi, macd_line, macd_signal,
                                macd_hist, bb_upper, bb_middle, bb_lower,
                                support, resistance, fib_levels, moving_averages,
                                trend, volume_analysis, market_structure, ai_analysis=""):
        rsi_status = E.rsi_status(rsi)
        fib_text = "\n".join([f"  {E.POINT_RIGHT} {n}: {v:.4f}" for n, v in list(fib_levels.items())[:7]])
        ma_text = "\n".join([f"  {E.POINT_RIGHT} {n}: {v:.4f}" for n, v in list(moving_averages.items())[:4]])
        change_emoji = E.change_icon(change)
        trend_icon = E.trend_icon(trend)
        vol_signal = volume_analysis.get('signal', 'خنثی')
        structure_bias = market_structure.get('bias', 'خنثی')
        
        text = f"""
{E.CHART}{E.CHART}{E.CHART} *تحلیل {symbol}* {E.CHART}{E.CHART}{E.CHART}

{E.MONEY} *قیمت:* ${price:,.4f}
{change_emoji} *تغییر ۲۴h:* {change:+.2f}%

{E.THERMOMETER} *اندیکاتورها:*
{E.POINT_RIGHT} RSI: {rsi_status}
{E.POINT_RIGHT} MACD: {macd_line:.4f} | سیگنال: {macd_signal:.4f}
{E.POINT_RIGHT} بولینگر: ↑{bb_upper:.4f} | ↔{bb_middle:.4f} | ↓{bb_lower:.4f}

{E.SHIELD} *حمایت:* ${support:,.4f}
{E.SWORD} *مقاومت:* ${resistance:,.4f}

{E.CRYSTAL} *فیبوناچی:*
{fib_text}

{E.MAGNET} *میانگین‌های متحرک:*
{ma_text}

{E.MOUNTAIN} *روند:* {trend_icon} {trend}
{E.WAVE} *حجم:* {vol_signal}
{E.BULB} *ساختار:* {structure_bias}

{E.CLOCK} *زمان تحلیل:* {TT.format(TT.now(), 'full')}
"""
        if ai_analysis:
            text += f"\n{E.DIAMOND}{'━'*10}{E.DIAMOND}\n{E.ROBOT} *تحلیل AI:*\n{ai_analysis}"
        
        text += f"\n{E.WARNING} *سلب مسئولیت:* این تحلیل صرفاً جنبه اطلاع‌رسانی دارد."
        return text
    
    @staticmethod
    def vip_plans_info() -> str:
        text = f"{E.CROWN}{E.CROWN}{E.CROWN} *پلن‌های اشتراک VIP* {E.CROWN}{E.CROWN}{E.CROWN}\n\n"
        for pk in ["vip", "pro", "elite"]:
            p = PLANS[pk]
            text += f"""
{p['icon']} *{p['name']}*
{E.MONEY} قیمت: *{p['price']:,} تومان*
{E.CALENDAR} مدت: *{p['days']} روز*
{E.BRAIN} سوالات AI: *{p['ai_daily_limit']} در روز*
{E.BELL} هشدارها: *{p['max_alerts']} عدد*
{E.STAR} واچ‌لیست: *{p['max_watchlist']} عدد*

*امکانات:*
"""
            for f in p['features'][:5]:
                text += f"  {E.CHECK} {f}\n"
            text += "\n" + "─" * 30 + "\n"
        
        text += f"""
{E.GIFT} *هدیه ویژه:* {WELCOME_BONUS_DAYS} روز VIP رایگان!
{E.CARD} *شماره کارت:* `{CARD_NUMBER}`
{E.PERSON} *به نام:* {CARD_HOLDER}

{E.POINT_DOWN} *برای خرید روی پلن مورد نظر کلیک کنید:*
"""
        return text
    
    @staticmethod
    def payment_instruction(plan_key: str) -> str:
        p = PLANS.get(plan_key, PLANS["vip"])
        return f"""
{E.CARD} *پرداخت اشتراک {p['name']}*

{E.MONEY} *مبلغ:* {p['price']:,} تومان
{E.CALENDAR} *مدت:* {p['days']} روز

{E.BANK} *اطلاعات کارت:*
{E.POINT_RIGHT} شماره: `{CARD_NUMBER}`
{E.POINT_RIGHT} به نام: {CARD_HOLDER}

{E.WARNING} *نکات:*
{E.POINT_RIGHT} مبلغ را دقیقاً واریز کنید
{E.POINT_RIGHT} رسید را همینجا ارسال کنید

{E.POINT_DOWN} *پس از پرداخت روی دکمه زیر کلیک کنید:*
"""
    
    @staticmethod
    def about_bot() -> str:
        return f"""
{E.ROBOT} *{APP_NAME} v{APP_VERSION}*
{E.LIGHTNING} پیشرفته‌ترین ربات تحلیل کریپتو

{E.BRAIN} *مشخصات:*
{E.POINT_RIGHT} AI: Groq (Llama 3.3 70B)
{E.POINT_RIGHT} صرافی: CoinEx
{E.POINT_RIGHT} تحلیل: RSI, MACD, Bollinger, Fibonacci, MA
{E.POINT_RIGHT} پرایس اکشن و ساختار بازار
{E.POINT_RIGHT} هشدار هوشمند قیمت
{E.POINT_RIGHT} سیستم اشتراک VIP

{E.CROWN} *تیم:* {CREATOR_USERNAME}
{E.PHONE} *کانال:* {CHANNEL_USERNAME}
{E.ENVELOPE} *پشتیبانی:* {SUPPORT_CONTACT}

{E.CLOCK} {TT.format(TT.now(), 'full')}
"""
    
    @staticmethod
    def support_info() -> str:
        return f"""
{E.ENVELOPE} *پشتیبانی {APP_NAME}*

{E.PERSON} *راه‌های ارتباطی:*
{E.POINT_RIGHT} تلگرام: {SUPPORT_CONTACT}
{E.POINT_RIGHT} کانال: {CHANNEL_USERNAME}

{E.CLOCK} *ساعات پاسخگویی:*
{E.POINT_RIGHT} همه روزه: ۸ صبح تا ۱۲ شب
{E.POINT_RIGHT} VIP: کمتر از ۱ ساعت

{E.CARD} *اطلاعات بانکی:*
{E.POINT_RIGHT} شماره کارت: `{CARD_NUMBER}`
{E.POINT_RIGHT} به نام: {CARD_HOLDER}
"""
    
    @staticmethod
    def time_info_message() -> str:
        now = TT.now()
        session = TT.session_details(now)
        return f"""
{E.CLOCK} *اطلاعات زمان تهران*

{E.CALENDAR} *تاریخ:* {TT.format(now, 'date')}
{E.WATCH} *ساعت:* {TT.format(now, 'time')}
{E.GLOBE} *فصل:* {TT.get_season(now)}
{E.CHART} *سشن:* {session['name']}

{E.POINT_RIGHT} شروع: {session['start']} | پایان: {session['end']}
{E.POINT_RIGHT} پیشرفت: {session['progress']}٪
{E.INFO} *جمعه:* {'بله 🕌' if TT.is_weekend(now) else 'خیر'}
"""
    
    @staticmethod
    def admin_stats_message(stats: Dict) -> str:
        return f"""
{E.SETTINGS} *پنل مدیریت {APP_NAME}*

{E.PERSON} *کاربران:*
{E.POINT_RIGHT} کل: {stats.get('total_users', 0):,}
{E.POINT_RIGHT} ویژه: {stats.get('premium_users', 0):,}
{E.POINT_RIGHT} فعال امروز: {stats.get('active_today', 0):,}
{E.POINT_RIGHT} نرخ تبدیل: {stats.get('conversion_rate', 0)}٪

{E.MONEY} *مالی:*
{E.POINT_RIGHT} درآمد کل: {stats.get('total_revenue', 0):,} تومان
{E.POINT_RIGHT} پرداخت‌های معلق: {stats.get('pending_payments', 0)}

{E.BRAIN} *AI:* {stats.get('total_ai_queries', 0):,} پرسش
{E.CHART} *سیگنال‌ها:* {stats.get('active_signals', 0)} فعال
{E.BELL} *هشدارها:* {stats.get('active_alerts', 0)} فعال

{E.CLOCK} {TT.format(TT.now(), 'full')}
"""

MSG = MessageTemplateEngine()

# ════════════════════════════════════════
# SECTION 17: MIDDLEWARE & DECORATORS
# ════════════════════════════════════════

def rate_limit(seconds: float = 0.5):
    """Decorator for rate limiting callbacks"""
    def decorator(func):
        last_called = {}
        @wraps(func)
        async def wrapper(callback: CallbackQuery, *args, **kwargs):
            user_id = callback.from_user.id
            now = time.time()
            if user_id in last_called:
                elapsed = now - last_called[user_id]
                if elapsed < seconds:
                    await callback.answer("⏳ لطفاً کمی صبر کنید...", show_alert=True)
                    return
            last_called[user_id] = now
            return await func(callback, *args, **kwargs)
        return wrapper
    return decorator

def require_premium(func):
    """Decorator to require premium access"""
    @wraps(func)
    async def wrapper(callback: CallbackQuery, *args, **kwargs):
        user_id = callback.from_user.id
        if not await db.is_premium(user_id):
            await callback.answer(
                f"{E.LOCK} این قابلیت مخصوص کاربران VIP است.",
                show_alert=True
            )
            return
        return await func(callback, *args, **kwargs)
    return wrapper

def admin_only(func):
    """Decorator to require admin access"""
    @wraps(func)
    async def wrapper(callback: CallbackQuery, *args, **kwargs):
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("⛔ دسترسی غیرمجاز!", show_alert=True)
            return
        return await func(callback, *args, **kwargs)
    return wrapper

# ════════════════════════════════════════
# SECTION 18: TELEGRAM HANDLERS
# ════════════════════════════════════════

router = Router()

# ── Start Command ──

@router.message(CommandStart())
async def command_start(message: Message, state: FSMContext):
    """Handle /start command"""
    user_id = message.from_user.id
    full_name = message.from_user.full_name or "کاربر گرامی"
    username = message.from_user.username or ""
    
    await db.upsert_user(user_id, username, full_name)
    
    # Process referral
    args = message.text.split() if message.text else []
    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            referrer_id = int(args[1].replace("ref_", ""))
            if referrer_id != user_id:
                user = await db.get_user(user_id)
                if user and not user.get('referred_by'):
                    await db.execute("UPDATE users SET referred_by=? WHERE user_id=?", (referrer_id, user_id))
                    await db.execute("UPDATE users SET total_referrals=total_referrals+1 WHERE user_id=?", (referrer_id,))
        except:
            pass
    
    # Welcome bonus
    user = await db.get_user(user_id)
    if user and not user.get('welcome_bonus'):
        await db.execute(
            "UPDATE users SET plan='vip', plan_until=?, welcome_bonus=1 WHERE user_id=?",
            (time.time() + WELCOME_BONUS_DAYS * 86400, user_id)
        )
    
    plan = await db.get_user_plan(user_id)
    days_left = 0
    if user and user.get('plan_until'):
        days_left = max(0, int((user['plan_until'] - time.time()) / 86400))
    
    await message.answer(
        MSG.welcome_message(full_name, plan, days_left),
        reply_markup=KB.main_menu(plan),
        parse_mode="HTML"
    )
    await db.log(user_id, "start", f"Plan: {plan}")


# ── Main Menu ──

@router.callback_query(F.data == "main_menu")
@rate_limit(0.3)
async def callback_main_menu(callback: CallbackQuery):
    """Return to main menu"""
    plan = await db.get_user_plan(callback.from_user.id)
    await callback.message.edit_text(
        f"{E.HOME} *منوی اصلی*\n{E.POINT_DOWN} گزینه مورد نظر را انتخاب کنید:",
        reply_markup=KB.main_menu(plan),
        parse_mode="HTML"
    )
    await callback.answer()

# ── Market Overview ──

@router.callback_query(F.data == "menu_market")
@rate_limit(0.5)
async def callback_market(callback: CallbackQuery):
    """Show market overview"""
    await callback.answer("🔄 در حال دریافت اطلاعات بازار...")
    
    tickers = await exchange.get_multiple_tickers(DEFAULT_SYMBOLS[:10])
    
    if not tickers:
        await callback.message.edit_text(
            f"{E.CROSS} خطا در دریافت اطلاعات بازار.",
            reply_markup=KB.back_to_main()
        )
        return
    
    market_text = MSG.market_overview(tickers)
    
    builder = InlineKeyboardBuilder()
    builder.button(text=f"{E.REFRESH} بروزرسانی", callback_data="menu_market")
    builder.button(text=f"{E.CHART} تحلیل تکنیکال", callback_data="menu_analysis")
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

# ── AI Question ──

@router.callback_query(F.data == "menu_ai")
@rate_limit(1.0)
async def callback_ai_menu(callback: CallbackQuery, state: FSMContext):
    """Start AI question flow"""
    user_id = callback.from_user.id
    can_use, used, limit = await db.can_use_ai(user_id)
    
    if not can_use:
        await callback.message.edit_text(
            f"{E.WARNING} *محدودیت هوش مصنوعی*\n\n{E.HOURGLASS} {used}/{limit} سوال\n{E.LOCK} ارتقا دهید:",
            reply_markup=KB.vip_plans(),
            parse_mode="HTML"
        )
        return
    
    await state.set_state(BotStates.waiting_for_ai_question)
    await callback.message.edit_text(
        f"{E.BRAIN} *پرسش از هوش مصنوعی*\n\n{E.HOURGLASS} {limit - used} سوال باقی‌مانده\n{E.POINT_DOWN} سوال خود را بفرستید:",
        reply_markup=KB.back_to_main(),
        parse_mode="HTML"
    )

@router.message(StateFilter(BotStates.waiting_for_ai_question))
async def handle_ai_question(message: Message, state: FSMContext):
    """Process AI question"""
    user_id = message.from_user.id
    can_use, used, limit = await db.can_use_ai(user_id)
    
    if not can_use:
        await message.answer(f"{E.WARNING} محدودیت روزانه تمام شده.", reply_markup=KB.vip_plans())
        await state.clear()
        return
    
    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    
    answer = await ai.ask(message.text)
    await db.increment_ai_usage(user_id)
    await db.save_ai_conversation(user_id, message.text, answer)
    
    new_count = await db.get_ai_usage(user_id)
    
    builder = InlineKeyboardBuilder()
    builder.button(text=f"{E.BRAIN} سوال جدید", callback_data="menu_ai")
    builder.button(text=f"{E.HOME} منوی اصلی", callback_data="main_menu")
    
    response = f"{E.ROBOT} *پاسخ هوش مصنوعی:*\n\n{answer}\n\n{E.HOURGLASS} {new_count}/{limit}"
    
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

# ── Technical Analysis ──

@router.callback_query(F.data == "menu_analysis")
@rate_limit(0.3)
async def callback_analysis_menu(callback: CallbackQuery):
    """Show analysis symbol selection"""
    await callback.message.edit_text(
        f"{E.CHART} *تحلیل تکنیکال*\n{E.POINT_DOWN} نماد مورد نظر را انتخاب کنید:",
        reply_markup=KB.analysis_symbols(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("analyze_"))
@rate_limit(1.0)
async def callback_analyze_symbol(callback: CallbackQuery):
    """Analyze a specific symbol"""
    symbol = callback.data.replace("analyze_", "")
    await callback.answer(f"🔄 در حال تحلیل {symbol}...")
    
    try:
        ticker = await exchange.get_ticker(symbol)
        if not ticker:
            raise ValueError("اطلاعات یافت نشد")
        
        price = float(ticker.get('last', 0))
        change = float(ticker.get('change_percentage', 0))
        
        klines = await exchange.get_klines(symbol, "1hour", 100)
        if not klines:
            raise ValueError("داده کندل یافت نشد")
        
        closes = [float(c.get('close', 0)) for c in klines]
        highs = [float(c.get('high', 0)) for c in klines]
        lows = [float(c.get('low', 0)) for c in klines]
        volumes = [float(c.get('volume', 0)) for c in klines]
        
        if len(closes) < 30:
            raise ValueError("داده کافی نیست")
        
        rsi = ta.calculate_rsi(closes)
        macd_line, macd_signal, macd_hist = ta.calculate_macd(closes)
        bb_upper, bb_middle, bb_lower = ta.calculate_bollinger_bands(closes)
        support, resistance = ta.calculate_support_resistance(closes)
        fib_levels = ta.calculate_fibonacci(max(highs), min(lows))
        moving_averages = ta.calculate_moving_averages(closes)
        trend = ta.detect_trend(closes)
        volume_analysis = ta.analyze_volume(volumes, closes)
        market_structure = ta.market_structure(highs, lows)
        
        ai_text = await ai.analyze_technically(symbol, f"قیمت: {price}, RSI: {rsi:.1f}, روند: {trend}")
        
        text = MSG.technical_analysis_card(
            symbol, price, change, rsi, macd_line, macd_signal, macd_hist,
            bb_upper, bb_middle, bb_lower, support, resistance,
            fib_levels, moving_averages, trend, volume_analysis,
            market_structure, ai_text
        )
        
        builder = InlineKeyboardBuilder()
        builder.button(text=f"{E.BELL} تنظیم هشدار", callback_data=f"alert_{symbol}")
        builder.button(text=f"{E.STAR} افزودن به واچ‌لیست", callback_data=f"watch_add_{symbol}")
        builder.button(text=f"{E.BACK} بازگشت", callback_data="menu_analysis")
        builder.adjust(2, 1)
        
        if len(text) > 4000:
            parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    await callback.message.edit_text(part, reply_markup=builder.as_markup(), parse_mode="HTML")
                else:
                    await callback.message.answer(part, parse_mode="HTML")
        else:
            await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
        
        await db.log(callback.from_user.id, "analysis", symbol)
        
    except Exception as e:
        logger.error(f"Analysis error for {symbol}: {e}")
        await callback.message.edit_text(
            f"{E.CROSS} *خطا در تحلیل {symbol}*\n{E.INFO} {str(e)[:100]}\n{E.POINT_RIGHT} لطفاً دوباره تلاش کنید.",
            reply_markup=KB.back_to_main(),
            parse_mode="HTML"
        )

# ── Time Information ──

@router.callback_query(F.data == "menu_time")
@rate_limit(0.3)
async def callback_time_info(callback: CallbackQuery):
    """Show Tehran time information"""
    await callback.message.edit_text(
        MSG.time_info_message(),
        reply_markup=KB.refresh_and_back("menu_time"),
        parse_mode="HTML"
    )
    await callback.answer()

# ── VIP Plans ──

@router.callback_query(F.data == "menu_vip")
@rate_limit(0.3)
async def callback_vip_menu(callback: CallbackQuery):
    """Show VIP plans"""
    await callback.message.edit_text(
        MSG.vip_plans_info(),
        reply_markup=KB.vip_plans(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("buy_"))
@rate_limit(0.3)
async def callback_buy_plan(callback: CallbackQuery):
    """Handle plan purchase"""
    plan_key = callback.data.replace("buy_", "")
    if plan_key not in PLANS:
        await callback.answer("❌ پلن نامعتبر!", show_alert=True)
        return
    
    await callback.message.edit_text(
        MSG.payment_instruction(plan_key),
        reply_markup=KB.confirm_payment(plan_key),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("confirm_pay_"))
@rate_limit(0.3)
async def callback_confirm_payment(callback: CallbackQuery, state: FSMContext):
    """Confirm payment and request receipt"""
    plan_key = callback.data.replace("confirm_pay_", "")
    plan = PLANS.get(plan_key, PLANS["vip"])
    
    await state.set_state(BotStates.waiting_for_payment_receipt)
    await state.update_data(plan=plan_key, amount=plan['price'])
    
    await callback.message.edit_text(
        f"{E.ENVELOPE} *ارسال رسید پرداخت*\n\n{E.POINT_DOWN} لطفاً عکس رسید را ارسال کنید.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{E.BACK} بازگشت", callback_data="menu_vip")]
        ]),
        parse_mode="HTML"
    )

@router.message(StateFilter(BotStates.waiting_for_payment_receipt), F.photo)
async def handle_payment_receipt(message: Message, state: FSMContext):
    """Process payment receipt"""
    user_id = message.from_user.id
    data = await state.get_data()
    plan_key = data.get('plan', 'vip')
    amount = data.get('amount', 0)
    plan = PLANS.get(plan_key, PLANS["vip"])
    
    payment_id = await db.create_payment(user_id, plan_key, amount)
    await db.execute("UPDATE payments SET receipt_file_id=? WHERE id=?", (message.photo[-1].file_id, payment_id))
    
    for admin_id in ADMIN_IDS:
        try:
            admin_text = f"{E.BELL} *پرداخت جدید*\n{E.PERSON} کاربر: `{user_id}`\n{E.CROWN} پلن: {plan['name']}\n{E.MONEY} مبلغ: *{amount:,} تومان*\n{E.CARD} شناسه: `{payment_id}`"
            await message.bot.send_message(admin_id, admin_text, reply_markup=KB.admin_payment_actions(payment_id), parse_mode="HTML")
            await message.bot.send_photo(admin_id, message.photo[-1].file_id)
        except:
            pass
    
    await message.answer(
        f"{E.CHECK} *رسید دریافت شد!*\n{E.HOURGLASS} در حال بررسی...\n{E.ENVELOPE} {SUPPORT_CONTACT}",
        reply_markup=KB.back_to_main(),
        parse_mode="HTML"
    )
    await db.log(user_id, "payment_receipt", str(payment_id))
    await state.clear()

# ── Admin Payment Actions ──

@router.callback_query(F.data.startswith("admin_approve_"))
@admin_only
async def callback_admin_approve(callback: CallbackQuery):
    """Admin: approve payment"""
    payment_id = int(callback.data.replace("admin_approve_", ""))
    
    if await db.approve_payment(payment_id, callback.from_user.id):
        payment = await db.fetchone("SELECT * FROM payments WHERE id=?", (payment_id,))
        if payment:
            try:
                plan_name = PLANS.get(payment['plan'], {}).get('name', payment['plan'])
                await callback.bot.send_message(
                    payment['user_id'],
                    f"{E.PARTY}{E.PARTY}{E.PARTY} *تبریک!*\n\n{E.CHECK} پرداخت شما تایید شد!\n{E.CROWN} پلن: {plan_name}\n{E.ROCKET} از امکانات خود لذت ببرید!",
                    parse_mode="HTML"
                )
            except:
                pass
        await callback.message.edit_text(f"{E.CHECK} پرداخت {payment_id} تایید شد.", parse_mode="HTML")
    else:
        await callback.answer("❌ خطا!", show_alert=True)

@router.callback_query(F.data.startswith("admin_reject_"))
@admin_only
async def callback_admin_reject(callback: CallbackQuery):
    """Admin: reject payment"""
    payment_id = int(callback.data.replace("admin_reject_", ""))
    await db.reject_payment(payment_id, callback.from_user.id)
    
    payment = await db.fetchone("SELECT * FROM payments WHERE id=?", (payment_id,))
    if payment:
        try:
            await callback.bot.send_message(
                payment['user_id'],
                f"{E.CROSS} *پرداخت تایید نشد*\n{E.INFO} لطفاً با پشتیبانی تماس بگیرید: {SUPPORT_CONTACT}",
                parse_mode="HTML"
            )
        except:
            pass
    
    await callback.message.edit_text(f"{E.CROSS} پرداخت {payment_id} رد شد.", parse_mode="HTML")

# ── Watchlist ──

@router.callback_query(F.data == "menu_watchlist")
@rate_limit(0.3)
async def callback_watchlist(callback: CallbackQuery):
    """Show user's watchlist"""
    items = await db.get_watchlist(callback.from_user.id)
    
    if not items:
        text = f"{E.STAR} *واچ‌لیست*\n\n{E.INFO} واچ‌لیست شما خالی است."
    else:
        text = f"{E.STAR} *واچ‌لیست شما* ({len(items)} نماد)\n\n"
        for i, item in enumerate(items, 1):
            added = TT.format(TT.from_timestamp(item['added_at']), "relative")
            text += f"{E.number(i)} {E.CHART} *{item['symbol']}* ({added})\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=KB.back_to_main(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("watch_add_"))
@rate_limit(0.3)
async def callback_watchlist_add(callback: CallbackQuery):
    """Add symbol to watchlist"""
    symbol = callback.data.replace("watch_add_", "")
    user_id = callback.from_user.id
    
    if await db.add_to_watchlist(user_id, symbol):
        await callback.answer(f"{E.CHECK} {symbol} به واچ‌لیست اضافه شد!", show_alert=True)
    else:
        await callback.answer(f"{E.CROSS} خطا در افزودن!", show_alert=True)

# ── Alerts ──

@router.callback_query(F.data == "menu_alerts")
@rate_limit(0.3)
async def callback_alerts_menu(callback: CallbackQuery):
    """Show alerts menu"""
    alerts = await db.get_active_alerts(callback.from_user.id)
    
    if not alerts:
        text = f"{E.BELL} *هشدارهای قیمت*\n\n{E.INFO} هیچ هشدار فعالی ندارید."
    else:
        text = f"{E.BELL} *هشدارهای فعال* ({len(alerts)})\n\n"
        for i, a in enumerate(alerts, 1):
            atype = T.ALERT_TYPES.get(a['alert_type'], a['alert_type'])
            created = TT.format(TT.from_timestamp(a['created_at']), "relative")
            text += f"{E.number(i)} {E.CHART} *{a['symbol']}*\n   {E.TARGET} {atype}: {a['target_price']}\n   {E.CLOCK} {created}\n\n"
    
    builder = InlineKeyboardBuilder()
    builder.button(text=f"{E.PLUS} هشدار جدید", callback_data="alert_new")
    builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "alert_new")
@rate_limit(0.3)
async def callback_alert_new(callback: CallbackQuery, state: FSMContext):
    """Start new alert creation"""
    await state.set_state(BotStates.waiting_for_alert_symbol)
    await callback.message.edit_text(
        f"{E.BELL} *هشدار جدید*\n\n{E.POINT_DOWN} نماد را وارد کنید:\nمثال: BTCUSDT",
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
        f"{E.CHART} *{symbol}*\n\n{E.POINT_DOWN} نوع هشدار را انتخاب کنید:",
        reply_markup=KB.alert_types(symbol),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("alerttype_"))
@rate_limit(0.3)
async def callback_alert_type(callback: CallbackQuery, state: FSMContext):
    """Handle alert type selection"""
    try:
        parts = callback.data.replace("alerttype_", "").split("_", 1)
        alert_type = parts[0]
        symbol = parts[1] if len(parts) > 1 else "BTCUSDT"
        
        await state.update_data(alert_type=alert_type)
        await state.set_state(BotStates.waiting_for_alert_price)
        
        await callback.message.edit_text(
            f"{E.TARGET} *قیمت هدف برای {symbol}*\n{E.INFO} نوع: {'بالاتر ⬆️' if alert_type == 'above' else 'پایین‌تر ⬇️'}\n\n{E.POINT_DOWN} قیمت را وارد کنید:\nمثال: 45000.50",
            reply_markup=KB.back_to_main(),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Alert type error: {e}")
        await callback.answer("❌ خطا!", show_alert=True)

@router.message(StateFilter(BotStates.waiting_for_alert_price))
async def handle_alert_price(message: Message, state: FSMContext):
    """Process alert price"""
    try:
        price = float(message.text.strip().replace(",", ""))
        if price <= 0:
            raise ValueError("قیمت نامعتبر")
        
        data = await state.get_data()
        symbol = data.get('alert_symbol', 'BTCUSDT')
        alert_type = data.get('alert_type', 'above')
        
        alert_id = await db.create_alert(message.from_user.id, symbol, price, alert_type)
        
        await message.answer(
            f"{E.CHECK} *هشدار ثبت شد!*\n{E.CHART} {symbol}\n{E.TARGET} {'بالاتر ⬆️' if alert_type == 'above' else 'پایین‌تر ⬇️'} از {price:,.4f}\n{E.CARD} ID: {alert_id}",
            reply_markup=KB.back_to_main(),
            parse_mode="HTML"
        )
        await db.log(message.from_user.id, "alert_created", f"{symbol} {price} {alert_type}")
    except ValueError:
        await message.answer(f"{E.CROSS} *خطا!*\n{E.INFO} لطفاً یک عدد معتبر وارد کنید.", reply_markup=KB.back_to_main(), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"{E.CROSS} خطا در ثبت هشدار.", reply_markup=KB.back_to_main(), parse_mode="HTML")
    
    await state.clear()

# ── About & Support ──

@router.callback_query(F.data == "menu_about")
@rate_limit(0.3)
async def callback_about(callback: CallbackQuery):
    """Show about information"""
    builder = InlineKeyboardBuilder()
    builder.button(text=f"{E.PHONE} کانال", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")
    builder.button(text=f"{E.ENVELOPE} سازنده", url=f"https://t.me/{CREATOR_USERNAME.replace('@', '')}")
    builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
    
    await callback.message.edit_text(MSG.about_bot(), reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "menu_support")
@rate_limit(0.3)
async def callback_support(callback: CallbackQuery):
    """Show support information"""
    builder = InlineKeyboardBuilder()
    builder.button(text=f"{E.ENVELOPE} پیام", url=f"https://t.me/{CREATOR_USERNAME.replace('@', '')}")
    builder.button(text=f"{E.BACK} بازگشت", callback_data="main_menu")
    
    await callback.message.edit_text(MSG.support_info(), reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()

# ── Admin Panel ──

@router.callback_query(F.data == "admin_panel")
@admin_only
@rate_limit(0.3)
async def callback_admin_panel(callback: CallbackQuery):
    """Show admin panel"""
    stats = await db.get_full_stats()
    await callback.message.edit_text(
        MSG.admin_stats_message(stats),
        reply_markup=KB.back_to_main(),
        parse_mode="HTML"
    )
    await callback.answer()

# ════════════════════════════════════════
# SECTION 19: ALERT CHECKER (BACKGROUND)
# ════════════════════════════════════════

async def alert_checker_task():
    """Background task to check price alerts"""
    logger.info("Alert checker started")
    while True:
        try:
            active_alerts = await db.get_active_alerts()
            
            for alert in active_alerts:
                try:
                    ticker = await exchange.get_ticker(alert['symbol'])
                    if not ticker:
                        continue
                    
                    current_price = float(ticker.get('last', 0))
                    target_price = alert['target_price']
                    alert_type = alert['alert_type']
                    
                    triggered = False
                    if alert_type == 'above' and current_price >= target_price:
                        triggered = True
                    elif alert_type == 'below' and current_price <= target_price:
                        triggered = True
                    
                    if triggered:
                        await db.trigger_alert(alert['id'])
                        
                        if bot:
                            try:
                                await bot.send_message(
                                    alert['user_id'],
                                    f"{E.BELL}{E.BELL}{E.BELL} *هشدار قیمت!*\n\n"
                                    f"{E.CHART} *{alert['symbol']}*\n"
                                    f"{E.MONEY} قیمت فعلی: ${current_price:,.4f}\n"
                                    f"{E.TARGET} هدف: {target_price}\n"
                                    f"{E.CLOCK} {TT.format(TT.now(), 'full')}",
                                    parse_mode="HTML"
                                )
                            except:
                                pass
                except:
                    pass
            
            await asyncio.sleep(30)
        except Exception as e:
            logger.error(f"Alert checker error: {e}")
            await asyncio.sleep(60)

# ════════════════════════════════════════
# SECTION 20: BOT SETUP
# ════════════════════════════════════════

try:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    logger.info("Bot instance created successfully")
except Exception as e:
    logger.error(f"Failed to create bot instance: {e}")
    bot = None

dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)

bot_start_time = TT.now()

async def set_bot_commands():
    """Set bot commands menu"""
    if bot is None:
        return
    
    commands = [
        BotCommand(command="start", description="🚀 شروع ربات"),
        BotCommand(command="market", description="📊 بازار"),
        BotCommand(command="ai", description="🤖 هوش مصنوعی"),
        BotCommand(command="analysis", description="📈 تحلیل تکنیکال"),
        BotCommand(command="vip", description="👑 پلن‌های VIP"),
        BotCommand(command="support", description="📧 پشتیبانی"),
    ]
    
    try:
        await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
        logger.info("Bot commands set")
    except Exception as e:
        logger.error(f"Failed to set commands: {e}")

# ════════════════════════════════════════
# SECTION 21: FASTAPI LIFESPAN
# ════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global bot_start_time
    
    logger.info(f"{E.ROCKET} Starting {APP_NAME} v{APP_VERSION}...")
    logger.info(f"Environment: {ENVIRONMENT}")
    logger.info(f"Port: {PORT}")
    
    # Initialize database
    try:
        await db.initialize()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    # Set webhook
    if WEBHOOK_URL and bot:
        try:
            await bot.set_webhook(
                url=f"{WEBHOOK_URL}/webhook",
                secret_token=WEBHOOK_SECRET,
                drop_pending_updates=True
            )
            logger.info(f"Webhook set: {WEBHOOK_URL}/webhook")
        except Exception as e:
            logger.error(f"Webhook setup failed: {e}")
    
    # Set bot commands
    await set_bot_commands()
    
    # Start background tasks
    alert_task = asyncio.create_task(alert_checker_task())
    
    logger.info(f"{E.ROCKET} {APP_NAME} is ready!")
    logger.info(f"Time: {TT.format(TT.now(), 'full')}")
    logger.info(f"Bot uptime started at: {TT.format(bot_start_time, 'full')}")
    
    yield
    
    # Cleanup
    logger.info("Shutting down...")
    
    alert_task.cancel()
    try:
        await alert_task
    except asyncio.CancelledError:
        pass
    
    if bot:
        try:
            await bot.delete_webhook()
        except:
            pass
        try:
            await bot.session.close()
        except:
            pass
    
    try:
        await exchange.close()
    except:
        pass
    
    logger.info(f"{E.WAVE} {APP_NAME} stopped")

# ════════════════════════════════════════
# SECTION 22: FASTAPI APP
# ════════════════════════════════════════

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Professional Crypto Trading Bot with AI, Technical Analysis, and VIP System",
    lifespan=lifespan,
    docs_url="/docs" if ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if ENVIRONMENT == "development" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ════════════════════════════════════════
# SECTION 23: API ENDPOINTS
# ════════════════════════════════════════

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Handle Telegram webhook updates"""
    try:
        secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if secret != WEBHOOK_SECRET:
            logger.warning("Invalid webhook secret attempt")
            raise HTTPException(status_code=403, detail="Invalid webhook secret")
        
        data = await request.json()
        update = Update(**data)
        
        if dp and bot:
            await dp.feed_update(bot, update)
        
        return {"status": "ok"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook error: {e}\n{traceback.format_exc()}")
        return JSONResponse({"status": "error", "message": str(e)[:100]}, status_code=500)

@app.get("/")
async def root_endpoint():
    """Root endpoint"""
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "build": APP_BUILD,
        "creator": CREATOR_USERNAME,
        "channel": CHANNEL_USERNAME,
        "status": "running",
        "time": TT.format(TT.now(), "full"),
        "timestamp": time.time(),
        "environment": ENVIRONMENT
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "time": TT.format(TT.now(), "full"),
        "version": APP_VERSION,
        "uptime": TT.uptime_string(bot_start_time)
    }

@app.get("/stats")
async def get_stats(request: Request):
    """Get bot statistics (protected endpoint)"""
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {WEBHOOK_SECRET}":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    stats = await db.get_full_stats()
    stats["ai_engine"] = ai.get_stats()
    stats["exchange"] = exchange.get_stats()
    stats["uptime"] = TT.uptime_string(bot_start_time)
    
    return stats

@app.get("/admin")
async def admin_dashboard(request: Request):
    """Simple admin dashboard HTML"""
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {WEBHOOK_SECRET}":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    stats = await db.get_full_stats()
    
    html = f"""<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{APP_NAME} - Admin Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Tahoma', sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: #eee; min-height: 100vh; padding: 20px; }}
        .header {{ text-align: center; padding: 30px 0; }}
        .header h1 {{ font-size: 2em; color: #e94560; }}
        .header p {{ color: #aaa; margin-top: 10px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; max-width: 1200px; margin: 0 auto; }}
        .card {{ background: #0f3460; border-radius: 15px; padding: 25px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .card .icon {{ font-size: 2.5em; margin-bottom: 10px; }}
        .card .value {{ font-size: 2em; font-weight: bold; color: #e94560; }}
        .card .label {{ color: #aaa; margin-top: 5px; font-size: 1em; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🦅 {APP_NAME}</h1>
        <p>Admin Dashboard v{APP_VERSION}</p>
        <p>{TT.format(TT.now(), 'full')}</p>
    </div>
    <div class="grid">
        <div class="card"><div class="icon">👥</div><div class="value">{stats['total_users']:,}</div><div class="label">کل کاربران</div></div>
        <div class="card"><div class="icon">👑</div><div class="value">{stats['premium_users']:,}</div><div class="label">کاربران ویژه</div></div>
        <div class="card"><div class="icon">📊</div><div class="value">{stats['conversion_rate']}%</div><div class="label">نرخ تبدیل</div></div>
        <div class="card"><div class="icon">💰</div><div class="value">{stats['total_revenue']:,}</div><div class="label">درآمد کل (تومان)</div></div>
        <div class="card"><div class="icon">🤖</div><div class="value">{stats['total_ai_queries']:,}</div><div class="label">پرسش‌های AI</div></div>
        <div class="card"><div class="icon">📈</div><div class="value">{stats['active_signals']}</div><div class="label">سیگنال‌های فعال</div></div>
    </div>
    <div class="footer">
        <p>سازنده: {CREATOR_USERNAME} | کانال: {CHANNEL_USERNAME}</p>
        <p>Uptime: {TT.uptime_string(bot_start_time)}</p>
    </div>
</body>
</html>"""
    
    return HTMLResponse(content=html)

# ════════════════════════════════════════
# SECTION 24: MAIN ENTRY POINT
# ════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🦅 {APP_NAME} v{APP_VERSION} starting on port {PORT}")
    logger.info(f"Creator: {CREATOR_USERNAME}")
    logger.info(f"Channel: {CHANNEL_USERNAME}")
    
    uvicorn.run(
        "part3:app",
        host="0.0.0.0",
        port=PORT,
        reload=(ENVIRONMENT == "development"),
        log_level="info",
        access_log=(ENVIRONMENT == "development"),
    )

# ════════════════════════════════════════
# END OF PART 3 - PROJECT COMPLETE
# ════════════════════════════════════════
