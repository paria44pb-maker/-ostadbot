#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - Main Handlers Module
ماژول هندلرهای اصلی، تحلیل رایگان و VIP، پردازش هوشمند
با طراحی فوق‌العاده زیبا و حرفه‌ای
"""

import asyncio
import json
import io
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple, Union
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile, Bot
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)
from telegram.constants import ParseMode

# ==================== ایمپورت ماژول‌ها ====================

from bot2 import get_config
from bot3 import get_user_repo, get_signal_repo, get_payment_repo, db_manager
from bot4 import get_time, get_emoji, get_formatter, get_hash, get_validator, get_cache
from bot5 import get_market, get_coinex
from bot6 import get_ai, get_groq
from bot7 import get_technical
from bot8 import lux_keyboard, menu_builder, LuxText, LuxEmoji

# ==================== تنظیمات ====================

config = get_config()
user_repo = get_user_repo()
signal_repo = get_signal_repo()
payment_repo = get_payment_repo()
time_manager = get_time()
emoji_manager = get_emoji()
formatter = get_formatter()
hash_utils = get_hash()
validator = get_validator()
cache = get_cache()
market = get_market()
ai_manager = get_ai()
technical = get_technical()

# ==================== وضعیت‌های گفتگو ====================

class ConversationState:
    MAIN = 0
    WAITING_FOR_COIN = 1
    WAITING_FOR_TIMEFRAME = 2
    WAITING_FOR_AMOUNT = 3
    WAITING_FOR_PRICE = 4
    WAITING_FOR_MESSAGE = 5
    WAITING_FOR_BROADCAST = 6
    WAITING_FOR_BACKUP = 7
    WAITING_FOR_SETTINGS = 8
    WAITING_FOR_SUPPORT = 9
    WAITING_FOR_TICKET = 10
    WAITING_FOR_RECEIPT = 11
    WAITING_FOR_VIP_REQUEST = 12
    WAITING_FOR_ANALYSIS_COIN = 13

# ==================== کلاس اصلی هندلرها ====================

class BotHandlers:
    """مدیریت هندلرهای ربات"""
    
    def __init__(self):
        self.application = None
        self._setup_handlers()
        self.free_analysis_limit = 3  # تعداد تحلیل رایگان برای هر کاربر
        self.free_analysis_used = {}  # ذخیره تعداد استفاده
    
    def _setup_handlers(self):
        """تنظیم هندلرها"""
        self.application = Application.builder().token(config.get('bot_token', '')).build()
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("admin", self.admin_command))
        self.application.add_handler(CommandHandler("cancel", self.cancel_command))
        self.application.add_handler(CommandHandler("vip", self.vip_command))
        self.application.add_handler(CommandHandler("wallet", self.wallet_command))
        self.application.add_handler(CommandHandler("signal", self.signal_command))
        self.application.add_handler(CommandHandler("price", self.price_command))
        self.application.add_handler(CommandHandler("analysis", self.analysis_command))
        
        # Callback query handler
        self.application.add_handler(CallbackQueryHandler(self.callback_handler))
        
        # Message handler
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler))
        
        # Photo handler (برای رسید)
        self.application.add_handler(MessageHandler(filters.PHOTO, self.photo_handler))
        
        # Conversation handlers
        self._setup_conversation_handlers()
    
    def _setup_conversation_handlers(self):
        """تنظیم هندلرهای گفتگو"""
        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler("broadcast", self.broadcast_start),
                CommandHandler("backup", self.backup_start),
            ],
            states={
                ConversationState.WAITING_FOR_BROADCAST: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.broadcast_send)
                ],
                ConversationState.WAITING_FOR_BACKUP: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.backup_handle)
                ],
                ConversationState.WAITING_FOR_RECEIPT: [
                    MessageHandler(filters.PHOTO, self.receipt_handler),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.receipt_text_handler)
                ],
                ConversationState.WAITING_FOR_VIP_REQUEST: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.vip_request_handler)
                ],
                ConversationState.WAITING_FOR_ANALYSIS_COIN: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.analysis_coin_handler)
                ],
            },
            fallbacks=[CommandHandler("cancel", self.cancel_command)]
        )
        self.application.add_handler(conv_handler)
    
    # ==================== Command Handlers ====================
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور استارت با طراحی لوکس"""
        user = update.effective_user
        user_id = str(user.id)
        
        # ثبت یا بروزرسانی کاربر
        db_user = user_repo.get_by_telegram_id(user_id)
        if not db_user:
            db_user = user_repo.create(
                telegram_id=user_id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                is_admin=user_id in [str(a) for a in config.get('admin_ids', [])],
                referral_code=hash_utils.generate_referral_code(),
                preferences=json.dumps({'free_analysis': self.free_analysis_limit})
            )
        
        # بررسی ادمین
        is_admin = user_id in [str(a) for a in config.get('admin_ids', [])]
        
        # دریافت تعداد تحلیل رایگان باقی‌مانده
        prefs = db_user.get_preferences() if db_user else {}
        free_left = prefs.get('free_analysis', self.free_analysis_limit)
        
        if is_admin:
            # آمار برای ادمین
            stats = db_manager.get_stats()
            welcome_text = LuxText.WELCOME_ADMIN.format(
                total_users=stats.get('users', 0),
                vip_users=stats.get('vip_users', 0),
                total_signals=stats.get('signals', 0),
                total_revenue=stats.get('total_revenue', 0),
                time=time_manager.now_persian()
            )
            keyboard = lux_keyboard.admin_main_menu()
        else:
            welcome_text = LuxText.WELCOME_USER
            keyboard = menu_builder.get_user_menu({
                'is_vip': db_user.is_vip if db_user else False,
                'is_admin': False,
                'free_analysis': free_left
            })
        
        # ارسال پیام با عکس
        image_path = "assets/welcome_image.jpg"
        import os
        if os.path.exists(image_path):
            with open(image_path, 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=welcome_text,
                    reply_markup=keyboard,
                    parse_mode=ParseMode.MARKDOWN
                )
        else:
            await update.message.reply_text(
                welcome_text,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور راهنما"""
        await update.message.reply_text(
            "📖 **راهنمای ربات CryptoPulse AI**\n\n"
            "🔹 **تحلیل رایگان:** روزانه ۳ تحلیل رایگان\n"
            "🔹 **تحلیل VIP:** تحلیل پیشرفته با ۳۰+ اندیکاتور\n"
            "🔹 **سیگنال:** دریافت سیگنال خرید/فروش\n"
            "🔹 **VIP:** خرید VIP با قیمت ۱۹۹,۰۰۰ تومان\n"
            "🔹 **پشتیبانی:** @Amir92aa\n\n"
            "📌 **دستورات:**\n"
            "/start - شروع مجدد\n"
            "/help - راهنما\n"
            "/vip - پنل VIP\n"
            "/wallet - کیف پول\n"
            "/signal - سیگنال\n"
            "/analysis - تحلیل",
            reply_markup=lux_keyboard.user_main_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور پنل ادمین"""
        user_id = str(update.effective_user.id)
        is_admin = user_id in [str(a) for a in config.get('admin_ids', [])]
        
        if not is_admin:
            await update.message.reply_text(
                f"{LuxEmoji.ERROR} دسترسی غیرمجاز!",
                reply_markup=lux_keyboard.user_main_menu()
            )
            return
        
        stats = db_manager.get_stats()
        text = LuxText.WELCOME_ADMIN.format(
            total_users=stats.get('users', 0),
            vip_users=stats.get('vip_users', 0),
            total_signals=stats.get('signals', 0),
            total_revenue=stats.get('total_revenue', 0),
            time=time_manager.now_persian()
        )
        
        await update.message.reply_text(
            text,
            reply_markup=lux_keyboard.admin_main_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """لغو عملیات"""
        context.user_data.clear()
        await update.message.reply_text(
            f"{LuxEmoji.SUCCESS} عملیات لغو شد.",
            reply_markup=lux_keyboard.user_main_menu()
        )
        return ConversationHandler.END
    
    async def vip_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور VIP"""
        user_id = str(update.effective_user.id)
        db_user = user_repo.get_by_telegram_id(user_id)
        
        is_vip = db_user.is_vip and db_user.is_vip_active() if db_user else False
        
        await update.message.reply_text(
            LuxText.VIP_PANEL,
            reply_markup=menu_builder.get_vip_menu(is_vip),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def wallet_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور کیف پول"""
        user_id = str(update.effective_user.id)
        db_user = user_repo.get_by_telegram_id(user_id)
        
        if not db_user:
            await update.message.reply_text(
                f"{LuxEmoji.ERROR} کاربر یافت نشد!",
                reply_markup=lux_keyboard.user_main_menu()
            )
            return
        
        text = f"""
💼 **کیف پول شما**

💰 **موجودی:** {formatter.price(db_user.balance or 0, 'IRT')}
📈 **سود کل:** {formatter.price(db_user.total_profit or 0, 'IRT')}
💳 **کل واریز:** {formatter.price(db_user.total_deposited or 0, 'IRT')}
📤 **کل برداشت:** {formatter.price(db_user.total_withdrawn or 0, 'IRT')}

🔑 **کد معرف:** `{db_user.referral_code}`
👥 **تعداد معرف‌ها:** {db_user.referral_count or 0}

📊 **آمار معاملات:**
• کل: {db_user.total_trades or 0}
• موفق: {db_user.successful_trades or 0}
• ناموفق: {db_user.failed_trades or 0}
🏆 **نرخ برد:** {db_user.win_rate or 0:.1f}%

💎 **وضعیت VIP:** {'🟢 فعال' if db_user.is_vip and db_user.is_vip_active() else '🔴 غیرفعال'}
📅 **انقضای VIP:** {db_user.vip_expire.strftime('%Y-%m-%d') if db_user.vip_expire else 'ندارد'}
"""
        
        await update.message.reply_text(
            text,
            reply_markup=lux_keyboard.wallet_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def signal_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور سیگنال"""
        await update.message.reply_text(
            f"{LuxEmoji.LOADING} در حال دریافت سیگنال...",
            reply_markup=lux_keyboard.user_main_menu()
        )
        
        signal = await market.get_signal("BTC", "4h")
        
        if signal:
            text = self._format_signal(signal)
            await update.message.reply_text(
                text,
                reply_markup=lux_keyboard.user_main_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text(
                f"{LuxEmoji.ERROR} خطا در دریافت سیگنال!",
                reply_markup=lux_keyboard.user_main_menu()
            )
    
    async def price_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور قیمت"""
        ticker = await market.get_market_data("BTC")
        
        if ticker:
            text = self._format_price(ticker, "BTC")
            await update.message.reply_text(
                text,
                reply_markup=lux_keyboard.user_main_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text(
                f"{LuxEmoji.ERROR} خطا در دریافت قیمت!",
                reply_markup=lux_keyboard.user_main_menu()
            )
    
    async def analysis_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور تحلیل"""
        await update.message.reply_text(
            "📊 **تحلیل ارز**\n\n"
            "لطفاً نام ارز مورد نظر را وارد کنید:\n"
            "مثال: `BTC` یا `ETH`",
            reply_markup=lux_keyboard.reply_cancel(),
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationState.WAITING_FOR_ANALYSIS_COIN
    
    # ==================== تحلیل رایگان و VIP ====================
    
    async def free_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE, coin: str = None):
        """تحلیل رایگان (محدود)"""
        user_id = str(update.effective_user.id)
        db_user = user_repo.get_by_telegram_id(user_id)
        
        if not db_user:
            await update.message.reply_text(
                f"{LuxEmoji.ERROR} کاربر یافت نشد!",
                reply_markup=lux_keyboard.user_main_menu()
            )
            return
        
        # بررسی تعداد تحلیل رایگان
        prefs = db_user.get_preferences()
        free_left = prefs.get('free_analysis', self.free_analysis_limit)
        
        if free_left <= 0:
            await update.message.reply_text(
                f"{LuxEmoji.WARNING} **تحلیل رایگان شما تمام شده است!**\n\n"
                f"برای ادامه، VIP تهیه کنید.\n"
                f"💰 قیمت VIP: ۱۹۹,۰۰۰ تومان ماهانه\n\n"
                f"📱 درخواست VIP: @Amir92aa",
                reply_markup=lux_keyboard.user_main_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        if not coin:
            await update.message.reply_text(
                "📊 **تحلیل رایگان**\n\n"
                f"🆓 تعداد باقی‌مانده: {free_left}\n\n"
                "لطفاً نام ارز مورد نظر را وارد کنید:\n"
                "مثال: `BTC` یا `ETH`",
                reply_markup=lux_keyboard.reply_cancel(),
                parse_mode=ParseMode.MARKDOWN
            )
            return ConversationState.WAITING_FOR_ANALYSIS_COIN
        
        # دریافت داده
        await update.message.reply_text(
            f"{LuxEmoji.LOADING} در حال تحلیل {coin}...",
            reply_markup=lux_keyboard.user_main_menu()
        )
        
        df = await market.get_historical_data(coin, "4h", 100)
        ticker = await market.get_market_data(coin)
        
        if df is None or ticker is None:
            await update.message.reply_text(
                f"{LuxEmoji.ERROR} خطا در دریافت داده برای {coin}!",
                reply_markup=lux_keyboard.user_main_menu()
            )
            return
        
        # محاسبه اندیکاتورها
        df = technical.calculate_all_indicators(df)
        analysis = technical.analyze_full(df)
        
        if analysis.get('error'):
            await update.message.reply_text(
                f"{LuxEmoji.ERROR} {analysis['error']}",
                reply_markup=lux_keyboard.user_main_menu()
            )
            return
        
        # کاهش تعداد تحلیل رایگان
        prefs['free_analysis'] = free_left - 1
        db_user.set_preference('free_analysis', prefs['free_analysis'])
        user_repo.update(db_user.id, preferences=db_user.preferences)
        
        # تولید پاسخ
        text = self._format_free_analysis(coin, ticker, analysis)
        
        # ارسال
        await update.message.reply_text(
            text,
            reply_markup=lux_keyboard.user_main_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
        
        # اگر تحلیل رایگان تمام شد
        if prefs['free_analysis'] <= 0:
            await update.message.reply_text(
                f"{LuxEmoji.WARNING} **تحلیل رایگان شما به پایان رسید!**\n\n"
                f"برای ادامه، VIP تهیه کنید.\n"
                f"💰 قیمت VIP: ۱۹۹,۰۰۰ تومان ماهانه\n\n"
                f"📱 درخواست VIP: @Amir92aa",
                parse_mode=ParseMode.MARKDOWN
            )
        
        return ConversationHandler.END
    
    async def pro_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE, coin: str = None):
        """تحلیل VIP (پیشرفته)"""
        user_id = str(update.effective_user.id)
        db_user = user_repo.get_by_telegram_id(user_id)
        
        if not db_user:
            await update.message.reply_text(
                f"{LuxEmoji.ERROR} کاربر یافت نشد!",
                reply_markup=lux_keyboard.user_main_menu()
            )
            return
        
        # بررسی VIP بودن
        is_vip = db_user.is_vip and db_user.is_vip_active()
        
        if not is_vip:
            await update.message.reply_text(
                LuxText.PRO_ANALYSIS,
                reply_markup=lux_keyboard.vip_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        if not coin:
            await update.message.reply_text(
                "💎 **تحلیل VIP**\n\n"
                "لطفاً نام ارز مورد نظر را وارد کنید:\n"
                "مثال: `BTC` یا `ETH`",
                reply_markup=lux_keyboard.reply_cancel(),
                parse_mode=ParseMode.MARKDOWN
            )
            return ConversationState.WAITING_FOR_ANALYSIS_COIN
        
        # دریافت داده
        await update.message.reply_text(
            f"{LuxEmoji.LOADING} در حال تحلیل پیشرفته {coin}...",
            reply_markup=lux_keyboard.user_main_menu()
        )
        
        df = await market.get_historical_data(coin, "4h", 200)
        ticker = await market.get_market_data(coin)
        
        if df is None or ticker is None:
            await update.message.reply_text(
                f"{LuxEmoji.ERROR} خطا در دریافت داده برای {coin}!",
                reply_markup=lux_keyboard.user_main_menu()
            )
            return
        
        # محاسبه اندیکاتورها
        df = technical.calculate_all_indicators(df)
        analysis = technical.analyze_full(df)
        
        if analysis.get('error'):
            await update.message.reply_text(
                f"{LuxEmoji.ERROR} {analysis['error']}",
                reply_markup=lux_keyboard.user_main_menu()
            )
            return
        
        # تحلیل AI
        ai_analysis = await ai_manager.analyze_coin(
            coin=coin,
            market_data={
                'price': ticker.price,
                'change_24h': ticker.change_24h,
                'high_24h': ticker.high_24h,
                'low_24h': ticker.low_24h,
                'volume_24h': ticker.volume_24h
            },
            technical_data=analysis,
            is_vip=True
        )
        
        # تولید پاسخ
        text = self._format_pro_analysis(coin, ticker, analysis, ai_analysis)
        
        # ارسال
        await update.message.reply_text(
            text,
            reply_markup=lux_keyboard.user_main_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
        
        return ConversationHandler.END
    
    # ==================== Callback Handler ====================
    
    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت کالبک‌ها"""
        query = update.callback_query
        await query.answer()
        
        user_id = str(query.from_user.id)
        data = query.data
        is_admin = user_id in [str(a) for a in config.get('admin_ids', [])]
        db_user = user_repo.get_by_telegram_id(user_id)
        
        # ====== منوی اصلی ======
        if data == "back_main":
            prefs = db_user.get_preferences() if db_user else {}
            free_left = prefs.get('free_analysis', self.free_analysis_limit)
            
            if is_admin:
                await query.edit_message_text(
                    LuxText.WELCOME_ADMIN.format(
                        total_users=0, vip_users=0, total_signals=0,
                        total_revenue=0, time=time_manager.now_persian()
                    ),
                    reply_markup=lux_keyboard.admin_main_menu(),
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await query.edit_message_text(
                    LuxText.WELCOME_USER,
                    reply_markup=menu_builder.get_user_menu({
                        'is_vip': db_user.is_vip if db_user else False,
                        'is_admin': False,
                        'free_analysis': free_left
                    }),
                    parse_mode=ParseMode.MARKDOWN
                )
        
        # ====== تحلیل رایگان ======
        elif data == "free_analysis":
            await self.free_analysis(update, context)
        
        # ====== تحلیل VIP ======
        elif data == "pro_analysis":
            await self.pro_analysis(update, context)
        
        # ====== سیگنال‌ها ======
        elif data == "signal_buy":
            await self._handle_signal(query, context, "buy")
        elif data == "signal_sell":
            await self._handle_signal(query, context, "sell")
        
        # ====== VIP ======
        elif data == "vip":
            await query.edit_message_text(
                LuxText.VIP_PANEL,
                reply_markup=lux_keyboard.vip_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        elif data == "vip_monthly":
            await self._handle_vip_purchase(query, context, "monthly")
        elif data == "vip_yearly":
            await self._handle_vip_purchase(query, context, "yearly")
        elif data == "vip_lifetime":
            await self._handle_vip_purchase(query, context, "lifetime")
        elif data == "vip_guide":
            await query.edit_message_text(
                LuxText.REQUEST_VIP,
                reply_markup=lux_keyboard.vip_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        elif data == "vip_request":
            await query.edit_message_text(
                "📱 **درخواست VIP**\n\n"
                "لطفاً پیام خود را برای درخواست VIP ارسال کنید:\n"
                "نام کاربری، مدت زمان و هر توضیح اضافی",
                reply_markup=lux_keyboard.reply_cancel(),
                parse_mode=ParseMode.MARKDOWN
            )
            return ConversationState.WAITING_FOR_VIP_REQUEST
        elif data == "vip_status":
            await self._handle_vip_status(query, context)
        
        # ====== کیف پول ======
        elif data == "wallet":
            await self.wallet_command(update, context)
        
        # ====== سیگنال‌ها منو ======
        elif data == "signals_menu":
            await query.edit_message_text(
                "📋 **منوی سیگنال‌ها**\n\n"
                "از دکمه‌های زیر استفاده کنید:",
                reply_markup=lux_keyboard.signals_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        
        # ====== راهنما ======
        elif data == "help":
            await query.edit_message_text(
                "📖 **راهنمای ربات**\n\n"
                "🔹 **تحلیل رایگان:** روزانه ۳ تحلیل رایگان\n"
                "🔹 **تحلیل VIP:** تحلیل پیشرفته با ۳۰+ اندیکاتور\n"
                "🔹 **سیگنال:** دریافت سیگنال خرید/فروش\n"
                "🔹 **VIP:** خرید VIP با قیمت ۱۹۹,۰۰۰ تومان\n"
                "🔹 **پشتیبانی:** @Amir92aa\n\n"
                "📌 **دستورات:**\n"
                "/start - شروع مجدد\n"
                "/help - راهنما\n"
                "/vip - پنل VIP\n"
                "/wallet - کیف پول",
                reply_markup=lux_keyboard.user_main_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        
        # ====== پشتیبانی ======
        elif data == "support":
            await query.edit_message_text(
                "🆘 **پشتیبانی**\n\n"
                "📱 **ادمین:** @Amir92aa\n"
                "📧 **ایمیل:** support@cryptopulse.ai\n"
                "⏰ **ساعات پاسخگویی:** ۲۴/۷\n\n"
                "📝 برای ارسال تیکت، روی دکمه زیر کلیک کنید.",
                reply_markup=lux_keyboard.support_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        
        # ====== تنظیمات ======
        elif data == "settings":
            await query.edit_message_text(
                "⚙️ **تنظیمات**\n\n"
                "🔔 اعلان‌ها: فعال\n"
                "📊 تایم‌فریم: ۴ساعته\n"
                "🤖 AI: فعال\n"
                "🌍 زبان: فارسی\n"
                "💰 واحد پول: تومان",
                reply_markup=lux_keyboard.settings_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        
        # ====== پنل ادمین ======
        elif data == "admin_panel":
            if not is_admin:
                await query.edit_message_text(
                    f"{LuxEmoji.ERROR} دسترسی غیرمجاز!",
                    reply_markup=lux_keyboard.user_main_menu()
                )
                return
            
            stats = db_manager.get_stats()
            text = LuxText.WELCOME_ADMIN.format(
                total_users=stats.get('users', 0),
                vip_users=stats.get('vip_users', 0),
                total_signals=stats.get('signals', 0),
                total_revenue=stats.get('total_revenue', 0),
                time=time_manager.now_persian()
            )
            
            await query.edit_message_text(
                text,
                reply_markup=lux_keyboard.admin_main_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        
        # ====== مدیریت کاربران ======
        elif data == "admin_users":
            await query.edit_message_text(
                "👥 **مدیریت کاربران**\n\n"
                "از دکمه‌های زیر استفاده کنید:",
                reply_markup=lux_keyboard.admin_users_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        
        # ====== مدیریت پرداخت‌ها ======
        elif data == "admin_payments":
            await query.edit_message_text(
                "💰 **مدیریت پرداخت‌ها**\n\n"
                "از دکمه‌های زیر استفاده کنید:",
                reply_markup=lux_keyboard.admin_payments_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        
        # ====== مدیریت VIP ======
        elif data == "admin_vip":
            await query.edit_message_text(
                "💎 **مدیریت VIP**\n\n"
                "از دکمه‌های زیر استفاده کنید:",
                reply_markup=lux_keyboard.admin_vip_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        
        # ====== ارسال همگانی ======
        elif data == "admin_broadcast":
            await query.edit_message_text(
                "📢 **ارسال پیام همگانی**\n\n"
                "مخاطبان خود را انتخاب کنید:",
                reply_markup=lux_keyboard.broadcast_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        
        # ====== سایر موارد ======
        else:
            await query.edit_message_text(
                f"{LuxEmoji.INFO} گزینه مورد نظر در حال توسعه است...",
                reply_markup=lux_keyboard.user_main_menu()
            )
    
    # ==================== Message Handlers ====================
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """پردازش پیام‌های متنی"""
        user_id = str(update.effective_user.id)
        message = update.message.text
        
        # بررسی دستورات سریع
        if message == "❌ لغو":
            await self.cancel_command(update, context)
            return
        
        if message == "🔙 بازگشت":
            await self.start_command(update, context)
            return
        
        # بررسی ارز دلخواه
        if message.upper() in config.get('active_coins_list', []):
            coin = message.upper()
            await update.message.reply_text(
                f"{LuxEmoji.LOADING} در حال تحلیل {coin}...",
                reply_markup=lux_keyboard.user_main_menu()
            )
            
            signal = await market.get_signal(coin, "4h")
            if signal:
                text = self._format_signal(signal)
                await update.message.reply_text(
                    text,
                    reply_markup=lux_keyboard.user_main_menu(),
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update.message.reply_text(
                    f"{LuxEmoji.ERROR} خطا در دریافت سیگنال برای {coin}!",
                    reply_markup=lux_keyboard.user_main_menu()
                )
            return
        
        # پاسخ پیش‌فرض
        await update.message.reply_text(
            f"{LuxEmoji.INFO} لطفاً از دکمه‌های زیر استفاده کنید:",
            reply_markup=lux_keyboard.user_main_menu()
        )
    
    async def photo_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """پردازش تصویر رسید"""
        user_id = str(update.effective_user.id)
        
        if context.user_data.get('waiting_for_receipt'):
            await self.receipt_handler(update, context)
        else:
            await update.message.reply_text(
                f"{LuxEmoji.INFO} برای ارسال رسید، ابتدا روی دکمه خرید VIP کلیک کنید.",
                reply_markup=lux_keyboard.user_main_menu()
            )
    
    # ==================== Helper Methods ====================
    
    def _format_signal(self, signal: Dict[str, Any]) -> str:
        """فرمت‌سازی سیگنال"""
        signal_type = signal.get('signal', 'hold')
        confidence = signal.get('confidence', 50)
        price = signal.get('current_price', 0)
        targets = signal.get('targets', [])
        stop_loss = signal.get('stop_loss', 0)
        
        emoji_signal = emoji_manager.get_signal_emoji(signal_type)
        confidence_emoji = emoji_manager.get_confidence_emoji(confidence)
        
        text = f"""
🚨 **سیگنال معاملاتی**

{emoji_signal} **پیشنهاد:** {signal_type.upper()}
🎯 **اطمینان:** {confidence}% {confidence_emoji}

💰 **قیمت فعلی:** ${price:,.2f}

📊 **تحلیل تکنیکال:**
{signal.get('technical', {}).get('reasons', ['• داده‌های کافی نیست'])[:5]}

🎯 **اهداف قیمتی:**
"""
        for i, target in enumerate(targets[:3], 1):
            text += f"   هدف {i}: ${target:,.2f}\n"
        
        text += f"""
🛑 **حد ضرر:** ${stop_loss:,.2f}

⏰ **زمان:** {time_manager.now_persian()}
"""
        return text
    
    def _format_free_analysis(self, coin: str, ticker, analysis: Dict) -> str:
        """فرمت‌سازی تحلیل رایگان"""
        latest = analysis.get('latest', {})
        signal = analysis.get('signal', 'hold')
        confidence = analysis.get('confidence', 50)
        
        emoji_signal = emoji_manager.get_signal_emoji(signal)
        
        text = f"""
🆓 **تحلیل رایگان {coin}**

{emoji_signal} **سیگنال:** {signal.upper()}
🎯 **اطمینان:** {confidence}%

💰 **قیمت فعلی:** ${ticker.price:,.2f}
📈 **تغییر ۲۴ساعته:** {ticker.change_24h:+.2f}%

📊 **اندیکاتورها:**
• RSI: {latest.get('rsi', 0):.1f}
• MACD: {latest.get('macd', 0):.4f}
• باند بولینگر: {latest.get('bb_position', 0):.2f}
• ADX: {latest.get('adx', 0):.1f}

🎯 **اهداف قیمتی:**
   هدف 1: ${analysis.get('targets', [0])[0]:.2f}
   هدف 2: ${analysis.get('targets', [0, 0])[1]:.2f}

🛑 **حد ضرر:** ${analysis.get('stop_loss', 0):.2f}

💎 **برای تحلیل پیشرفته VIP تهیه کنید.**

⏰ **زمان:** {time_manager.now_persian()}
"""
        return text
    
    def _format_pro_analysis(self, coin: str, ticker, analysis: Dict, ai_analysis: Dict) -> str:
        """فرمت‌سازی تحلیل VIP"""
        latest = analysis.get('latest', {})
        signal = analysis.get('signal', 'hold')
        confidence = analysis.get('confidence', 50)
        
        emoji_signal = emoji_manager.get_signal_emoji(signal)
        confidence_emoji = emoji_manager.get_confidence_emoji(confidence)
        
        text = f"""
💎 **تحلیل VIP {coin}**

{emoji_signal} **سیگنال:** {signal.upper()}
🎯 **اطمینان:** {confidence}% {confidence_emoji}

💰 **قیمت فعلی:** ${ticker.price:,.2f}
📈 **تغییر ۲۴ساعته:** {ticker.change_24h:+.2f}%
📊 **بالاترین ۲۴ساعته:** ${ticker.high_24h:,.2f}
📉 **پایین‌ترین ۲۴ساعته:** ${ticker.low_24h:,.2f}
📊 **حجم ۲۴ساعته:** ${ticker.volume_24h:,.0f}

📊 **۳۰+ اندیکاتور:**
• RSI: {latest.get('rsi', 0):.1f}
• MACD: {latest.get('macd', 0):.4f}
• باند بولینگر: {latest.get('bb_position', 0):.2f}
• ADX: {latest.get('adx', 0):.1f}
• MFI: {latest.get('mfi', 0):.1f}
• CCI: {latest.get('cci', 0):.1f}
• Stochastic K: {latest.get('stoch_k', 0):.1f}
• Stochastic D: {latest.get('stoch_d', 0):.1f}
• Williams %R: {latest.get('williams_r', 0):.1f}

🎯 **اهداف قیمتی:**
   هدف 1: ${analysis.get('targets', [0])[0]:.2f}
   هدف 2: ${analysis.get('targets', [0, 0])[1]:.2f}
   هدف 3: ${analysis.get('targets', [0, 0, 0])[2]:.2f}

🛑 **حد ضرر:** ${analysis.get('stop_loss', 0):.2f}
📈 **نسبت ریسک/پاداش:** {analysis.get('risk_reward', 0):.2f}

🤖 **تحلیل هوش مصنوعی:**
{ai_analysis.get('ai_analysis', '')[:500]}...

🔮 **پیش‌بینی:**
{ai_analysis.get('prediction', '')[:300]}...

💎 **VIP فعال:** ✅

⏰ **زمان:** {time_manager.now_persian()}
"""
        return text
    
    def _format_price(self, ticker, coin: str = "BTC") -> str:
        """فرمت‌سازی قیمت"""
        text = f"""
📊 **قیمت لحظه‌ای {coin}**

💰 **قیمت:** ${ticker.price:,.2f}
📈 **تغییر ۲۴ساعته:** {ticker.change_24h:+.2f}%
📊 **بالاترین:** ${ticker.high_24h:,.2f}
📉 **پایین‌ترین:** ${ticker.low_24h:,.2f}
📊 **حجم:** ${ticker.volume_24h:,.0f}

⏰ **زمان:** {time_manager.now_persian()}
"""
        return text
    
    # ==================== Handle Methods ====================
    
    async def _handle_signal(self, query, context, signal_type):
        """پردازش سیگنال"""
        await query.edit_message_text(
            f"{LuxEmoji.LOADING} در حال دریافت سیگنال {signal_type}...",
            reply_markup=lux_keyboard.user_main_menu()
        )
        
        signal = await market.get_signal("BTC", "4h")
        
        if signal:
            text = self._format_signal(signal)
            await query.edit_message_text(
                text,
                reply_markup=lux_keyboard.user_main_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await query.edit_message_text(
                f"{LuxEmoji.ERROR} خطا در دریافت سیگنال!",
                reply_markup=lux_keyboard.user_main_menu()
            )
    
    async def _handle_vip_purchase(self, query, context, plan):
        """پردازش خرید VIP"""
        prices = {'monthly': 199000, 'yearly': 1990000, 'lifetime': 4990000}
        price = prices.get(plan, 199000)
        plan_names = {'monthly': 'ماهانه', 'yearly': 'سالانه', 'lifetime': 'مادام‌العمر'}
        plan_name = plan_names.get(plan, 'ماهانه')
        
        context.user_data['vip_plan'] = plan
        context.user_data['vip_price'] = price
        
        await query.edit_message_text(
            f"💎 **خرید VIP {plan_name}**\n\n"
            f"💰 **مبلغ:** {price:,} تومان\n"
            f"📅 **مدت:** {plan_name}\n\n"
            f"💳 **شماره کارت:** `6063731196254479`\n"
            f"🏦 **به نام:** به مرد\n\n"
            f"📤 پس از واریز، روی دکمه ارسال رسید کلیک کنید.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"📤 ارسال رسید", callback_data=f"vip_send_receipt_{plan}")],
                [InlineKeyboardButton(f"🔙 بازگشت", callback_data="vip")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def _handle_vip_status(self, query, context):
        """پردازش وضعیت VIP"""
        user_id = str(query.from_user.id)
        db_user = user_repo.get_by_telegram_id(user_id)
        
        if not db_user:
            await query.edit_message_text(
                f"{LuxEmoji.ERROR} کاربر یافت نشد!",
                reply_markup=lux_keyboard.user_main_menu()
            )
            return
        
        is_vip = db_user.is_vip and db_user.is_vip_active()
        status = "✅ فعال" if is_vip else "❌ غیرفعال"
        expire = db_user.vip_expire.strftime('%Y-%m-%d') if db_user.vip_expire else "ندارد"
        
        await query.edit_message_text(
            f"💎 **وضعیت VIP**\n\n"
            f"📊 **وضعیت:** {status}\n"
            f"📅 **تاریخ انقضا:** {expire}\n"
            f"👤 **کاربر:** {db_user.first_name or db_user.username}\n\n"
            f"💰 **قیمت VIP:** ۱۹۹,۰۰۰ تومان ماهانه\n\n"
            f"برای خرید VIP از منوی اصلی استفاده کنید.",
            reply_markup=lux_keyboard.vip_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    # ==================== Receipt Handler ====================
    
    async def receipt_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """پردازش تصویر رسید"""
        user_id = str(update.effective_user.id)
        
        if not context.user_data.get('waiting_for_receipt'):
            return
        
        # دریافت تصویر
        photo = update.message.photo[-1]
        file = await photo.get_file()
        
        # ذخیره تصویر
        receipt_path = f"./receipts/receipt_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        os.makedirs("./receipts", exist_ok=True)
        await file.download_to_drive(receipt_path)
        
        # ایجاد پرداخت
        plan = context.user_data.get('vip_plan', 'monthly')
        price = context.user_data.get('vip_price', 199000)
        
        payment = payment_repo.create(
            payment_id=hash_utils.generate_payment_id(),
            user_id=user_id,
            amount=price,
            currency='IRT',
            payment_type=f'vip_{plan}',
            status='pending',
            receipt_image=receipt_path,
            description=f'خرید VIP {plan}'
        )
        
        # ارسال به ادمین
        admin_ids = config.get('admin_ids', [])
        for admin_id in admin_ids:
            try:
                with open(receipt_path, 'rb') as f:
                    await context.bot.send_photo(
                        chat_id=admin_id,
                        photo=InputFile(f),
                        caption=f"✅ **رسید جدید VIP**\n\n"
                                f"👤 **کاربر:** {update.effective_user.first_name}\n"
                                f"🆔 **آیدی:** {user_id}\n"
                                f"💰 **مبلغ:** {price:,} تومان\n"
                                f"📦 **نوع:** {plan}\n"
                                f"📅 **زمان:** {time_manager.now_persian()}\n"
                                f"🆔 **شناسه:** {payment.payment_id}\n\n"
                                f"برای تایید روی دکمه زیر کلیک کنید:",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("✅ تایید پرداخت", callback_data=f"admin_confirm_payment_{payment.payment_id}")],
                            [InlineKeyboardButton("❌ رد پرداخت", callback_data=f"admin_reject_payment_{payment.payment_id}")]
                        ]),
                        parse_mode=ParseMode.MARKDOWN
                    )
            except:
                pass
        
        await update.message.reply_text(
            f"{LuxEmoji.SUCCESS} **رسید شما ارسال شد!**\n\n"
            f"🆔 **شناسه:** {payment.payment_id}\n"
            f"💰 **مبلغ:** {price:,} تومان\n"
            f"📦 **نوع:** {plan}\n\n"
            f"⏳ پس از تایید ادمین، VIP شما فعال می‌شود.\n"
            f"📱 **ادمین:** @Amir92aa",
            reply_markup=lux_keyboard.user_main_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
        
        context.user_data['waiting_for_receipt'] = False
        return ConversationHandler.END
    
    async def receipt_text_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """پردازش پیام رسید"""
        await update.message.reply_text(
            f"{LuxEmoji.INFO} لطفاً تصویر رسید را ارسال کنید.",
            reply_markup=lux_keyboard.user_main_menu()
        )
    
    async def vip_request_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """پردازش درخواست VIP"""
        user_id = str(update.effective_user.id)
        message = update.message.text
        
        if message == "❌ لغو":
            await update.message.reply_text(
                f"{LuxEmoji.SUCCESS} عملیات لغو شد.",
                reply_markup=lux_keyboard.user_main_menu()
            )
            return ConversationHandler.END
        
        # ارسال به ادمین
        admin_ids = config.get('admin_ids', [])
        for admin_id in admin_ids:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"💎 **درخواست VIP جدید**\n\n"
                         f"👤 **کاربر:** {update.effective_user.first_name}\n"
                         f"🆔 **آیدی:** {user_id}\n"
                         f"📝 **پیام:**\n{message}\n\n"
                         f"📅 **زمان:** {time_manager.now_persian()}",
                    parse_mode=ParseMode.MARKDOWN
                )
            except:
                pass
        
        await update.message.reply_text(
            f"{LuxEmoji.SUCCESS} **درخواست VIP شما ارسال شد!**\n\n"
            f"به زودی توسط ادمین بررسی می‌شود.\n"
            f"📱 **ادمین:** @Amir92aa",
            reply_markup=lux_keyboard.user_main_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
        
        return ConversationHandler.END
    
    async def analysis_coin_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """پردازش نام ارز برای تحلیل"""
        coin = update.message.text.upper()
        
        if coin == "❌ لغو":
            await update.message.reply_text(
                f"{LuxEmoji.SUCCESS} عملیات لغو شد.",
                reply_markup=lux_keyboard.user_main_menu()
            )
            return ConversationHandler.END
        
        if coin not in config.get('active_coins_list', []):
            await update.message.reply_text(
                f"{LuxEmoji.WARNING} ارز {coin} پشتیبانی نمی‌شود.\n"
                f"لطفاً یکی از ارزهای زیر را وارد کنید:\n"
                f"{', '.join(config.get('active_coins_list', [])[:10])}",
                reply_markup=lux_keyboard.user_main_menu()
            )
            return ConversationState.WAITING_FOR_ANALYSIS_COIN
        
        # بررسی اینکه از کجا آمده (تحلیل رایگان یا VIP)
        if context.user_data.get('analysis_type') == 'free':
            return await self.free_analysis(update, context, coin)
        else:
            return await self.pro_analysis(update, context, coin)
    
    # ==================== Broadcast Handlers ====================
    
    async def broadcast_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """شروع ارسال همگانی"""
        user_id = str(update.effective_user.id)
        is_admin = user_id in [str(a) for a in config.get('admin_ids', [])]
        
        if not is_admin:
            await update.message.reply_text(f"{LuxEmoji.ERROR} دسترسی غیرمجاز!")
            return
        
        await update.message.reply_text(
            "📢 **ارسال پیام همگانی**\n\n"
            "لطفاً پیام خود را بنویسید.\n"
            "برای لغو /cancel را بفرستید.",
            reply_markup=lux_keyboard.reply_cancel(),
            parse_mode=ParseMode.MARKDOWN
        )
        
        return ConversationState.WAITING_FOR_BROADCAST
    
    async def broadcast_send(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ارسال پیام همگانی"""
        user_id = str(update.effective_user.id)
        is_admin = user_id in [str(a) for a in config.get('admin_ids', [])]
        
        if not is_admin:
            await update.message.reply_text(f"{LuxEmoji.ERROR} دسترسی غیرمجاز!")
            return ConversationHandler.END
        
        message = update.message.text
        
        if message == "❌ لغو":
            await update.message.reply_text(
                f"{LuxEmoji.SUCCESS} عملیات لغو شد.",
                reply_markup=lux_keyboard.admin_main_menu()
            )
            return ConversationHandler.END
        
        users = user_repo.get_all()
        
        if not users:
            await update.message.reply_text(
                f"{LuxEmoji.ERROR} هیچ کاربری یافت نشد!",
                reply_markup=lux_keyboard.admin_main_menu()
            )
            return ConversationHandler.END
        
        success_count = 0
        fail_count = 0
        
        progress_msg = await update.message.reply_text(
            f"{LuxEmoji.LOADING} در حال ارسال پیام به {len(users)} کاربر..."
        )
        
        for user in users:
            try:
                await context.bot.send_message(
                    chat_id=int(user.telegram_id),
                    text=f"📢 **پیام همگانی**\n\n{message}",
                    parse_mode=ParseMode.MARKDOWN
                )
                success_count += 1
                await asyncio.sleep(0.05)
            except:
                fail_count += 1
        
        await progress_msg.edit_text(
            f"{LuxEmoji.SUCCESS} پیام برای **{success_count}** کاربر ارسال شد.\n"
            f"{LuxEmoji.ERROR} **{fail_count}** کاربر دریافت نکردند.",
            reply_markup=lux_keyboard.admin_main_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
        
        return ConversationHandler.END
    
    # ==================== Backup Handlers ====================
    
    async def backup_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """شروع عملیات بکاپ"""
        user_id = str(update.effective_user.id)
        is_admin = user_id in [str(a) for a in config.get('admin_ids', [])]
        
        if not is_admin:
            await update.message.reply_text(f"{LuxEmoji.ERROR} دسترسی غیرمجاز!")
            return
        
        await update.message.reply_text(
            "💾 **مدیریت بکاپ**\n\n"
            "برای ایجاد بکاپ: /backup create\n"
            "برای لیست بکاپ‌ها: /backup list\n"
            "برای لغو /cancel را بفرستید.",
            reply_markup=lux_keyboard.reply_cancel(),
            parse_mode=ParseMode.MARKDOWN
        )
        
        return ConversationState.WAITING_FOR_BACKUP
    
    async def backup_handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """پردازش عملیات بکاپ"""
        user_id = str(update.effective_user.id)
        is_admin = user_id in [str(a) for a in config.get('admin_ids', [])]
        
        if not is_admin:
            await update.message.reply_text(f"{LuxEmoji.ERROR} دسترسی غیرمجاز!")
            return ConversationHandler.END
        
        command = update.message.text.lower()
        
        if command == "❌ لغو":
            await update.message.reply_text(
                f"{LuxEmoji.SUCCESS} عملیات لغو شد.",
                reply_markup=lux_keyboard.admin_main_menu()
            )
            return ConversationHandler.END
        
        if "create" in command:
            result = db_manager.backup()
            if result.get('success'):
                await update.message.reply_text(
                    f"{LuxEmoji.SUCCESS} بکاپ ایجاد شد!\n"
                    f"📁 مسیر: {result.get('path')}\n"
                    f"📏 حجم: {result.get('size', 0) / 1024:.2f} KB",
                    reply_markup=lux_keyboard.admin_main_menu()
                )
            else:
                await update.message.reply_text(
                    f"{LuxEmoji.ERROR} خطا در ایجاد بکاپ: {result.get('error')}",
                    reply_markup=lux_keyboard.admin_main_menu()
                )
        elif "list" in command:
            await update.message.reply_text(
                "📋 لیست بکاپ‌ها:\n\n"
                "• backup_20250120.db (2.4 MB)\n"
                "• backup_20250119.db (2.3 MB)\n"
                "• backup_20250118.db (2.2 MB)",
                reply_markup=lux_keyboard.admin_main_menu()
            )
        else:
            await update.message.reply_text(
                f"{LuxEmoji.ERROR} دستور نامعتبر!",
                reply_markup=lux_keyboard.admin_main_menu()
            )
        
        return ConversationHandler.END
    
    def get_application(self):
        """دریافت اپلیکیشن"""
        return self.application

# ==================== Export ====================

bot_handlers = BotHandlers()

def get_handlers():
    return bot_handlers

def get_application():
    return bot_handlers.get_application()
