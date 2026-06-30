
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - Keyboards & Menus Module
ماژول کیبوردهای لوکس، منوهای شیک و دکمه‌های حرفه‌ای
با طراحی خاص و کاربرپسند
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import json

# ==================== ایموجی‌های لوکس ====================

class LuxEmoji:
    """ایموجی‌های شیک و لوکس"""
    MAIN = "🏛️"
    VIP = "💎"
    GOLD = "✨"
    DIAMOND = "💠"
    CROWN = "👑"
    STAR = "⭐"
    ROCKET = "🚀"
    FIRE = "🔥"
    LIGHTNING = "⚡"
    SHIELD = "🛡️"
    TROPHY = "🏆"
    MEDAL = "🏅"
    COIN = "🪙"
    MONEY = "💰"
    CREDIT = "💳"
    BANK = "🏦"
    CHART = "📊"
    SIGNAL = "📡"
    ANALYSIS = "🔬"
    SETTINGS = "⚙️"
    USER = "👤"
    ADMIN = "👑"
    SUPPORT = "🆘"
    HELP = "📖"
    WALLET = "💼"
    PORTFOLIO = "📈"
    TRADE = "🔄"
    BUY = "🟢"
    SELL = "🔴"
    HOLD = "🟡"
    STRONG_BUY = "💚"
    STRONG_SELL = "❤️"
    BACK = "🔙"
    NEXT = "➡️"
    PREV = "⬅️"
    UP = "⬆️"
    DOWN = "⬇️"
    PLUS = "➕"
    MINUS = "➖"
    CHECK = "✅"
    CROSS = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    SUCCESS = "🌟"
    ERROR = "💢"
    LOADING = "⏳"
    FREE = "🆓"
    PREMIUM = "💎"
    PRO = "🏅"
    ENTERPRISE = "🏢"
    COMMUNITY = "👥"
    CHAT = "💬"
    CALL = "📞"
    EMAIL = "📧"
    LOCATION = "📍"
    CALENDAR = "📅"
    CLOCK = "⏰"
    BELL = "🔔"
    LOCK = "🔒"
    UNLOCK = "🔓"
    KEY = "🔑"
    GIFT = "🎁"
    TICKET = "🎫"
    RIBBON = "🎀"
    PARTY = "🎉"
    CONFETTI = "🎊"
    SPARKLE = "✨"
    GLOW = "🌟"
    PEACE = "☮️"
    LOVE = "💖"
    HEART = "❤️"
    FLOWER = "🌸"
    LEAF = "🍃"
    SUN = "☀️"
    MOON = "🌙"
    CLOUD = "☁️"
    RAIN = "🌧️"
    SNOW = "❄️"
    STORM = "⛈️"
    WIND = "💨"
    WATER = "💧"
    EARTH = "🌍"
    MOUNTAIN = "🏔️"
    FOREST = "🌲"
    OCEAN = "🌊"
    FLAG = "🏁"
    GLOBE = "🌐"
    IRAN = "🇮🇷"
    USA = "🇺🇸"
    UK = "🇬🇧"
    GERMANY = "🇩🇪"
    FRANCE = "🇫🇷"
    ITALY = "🇮🇹"
    SPAIN = "🇪🇸"
    JAPAN = "🇯🇵"
    CHINA = "🇨🇳"
    RUSSIA = "🇷🇺"
    AUSTRALIA = "🇦🇺"
    BRAZIL = "🇧🇷"
    INDIA = "🇮🇳"
    TURKEY = "🇹🇷"
    UAE = "🇦🇪"

# ==================== متن‌های شیک ====================

class LuxText:
    """متن‌های شیک و لوکس"""
    
    WELCOME_USER = """
✨ **به CryptoPulse AI خوش آمدید!**

🏛️ **دستیار هوشمند تحلیل و سیگنال ارزهای دیجیتال**

💎 ما با استفاده از پیشرفته‌ترین هوش مصنوعی و تحلیل تکنیکال،  
به شما در تصمیم‌گیری‌های بهتر و پرسودتر کمک می‌کنیم.

---

🌟 **خدمات ما:**
• 📊 تحلیل لحظه‌ای بازار با ۳۰+ اندیکاتور
• 🤖 هوش مصنوعی پیشرفته (Groq AI)
• 📡 سیگنال‌های دقیق و سریع
• 💎 پنل VIP با امکانات ویژه
• 🆓 درخواست تحلیل رایگان (محدود)
• 💰 تحلیل پیشرفته و تخصصی (VIP)

---

**📊 همراها شما در مسیر سودآوری**

از دکمه‌های زیر برای شروع استفاده کنید 👇
"""
    
    WELCOME_ADMIN = """
👑 **به CryptoPulse AI خوش آمدید!**

🏛️ **سازنده عزیز، پنل مدیریت و تنظیمات ربات**

💎 شما کنترل کامل بر تمام بخش‌های ربات دارید.

---

📊 **آمار کلی:**
👥 **کاربران:** {total_users:,} نفر
💎 **VIP:** {vip_users:,} نفر
📡 **سیگنال‌ها:** {total_signals:,} مورد
💰 **درآمد:** ${total_revenue:,.2f}

⏰ **زمان:** {time}

---

از دکمه‌های زیر برای مدیریت استفاده کنید 👇
"""
    
    VIP_PANEL = """
💎 **پنل VIP CryptoPulse AI**

✨ **امکانات ویژه VIP:**
• 📊 سیگنال‌های اختصاصی VIP
• 🤖 تحلیل پیشرفته با AI (نامحدود)
• 🆘 پشتیبانی اولویت‌دار
• 💎 دسترسی به ارزهای ویژه
• 🔔 هشدارهای لحظه‌ای
• 📈 مدیریت پورتفولیو
• 🎯 سیگنال‌های دقیق‌تر
• 📊 اندیکاتورهای پیشرفته
• 🔬 تحلیل تخصصی و فاندامنتال
• 📡 سیگنال‌های لحظه‌ای

💰 **قیمت‌ها:**
• 💎 ماهانه: ۱۹۹,۰۰۰ تومان
• 💎 سالانه: ۱,۹۹۰,۰۰۰ تومان
• 👑 مادام‌العمر: ۴,۹۹۰,۰۰۰ تومان

🎁 **درخواست VIP:** @Amir92aa

📌 **برای خرید روی گزینه مورد نظر کلیک کنید.**
"""
    
    FREE_ANALYSIS = """
🆓 **تحلیل رایگان (محدود)**

📊 **شما {remaining} تحلیل رایگان باقی مانده دارید.**

📈 **امکانات تحلیل رایگان:**
• ۵ اندیکاتور اصلی
• سیگنال خرید/فروش
• سطح اطمینان
• ۲ هدف قیمتی
• حد ضرر پیشنهادی

💎 **برای تحلیل پیشرفته و نامحدود، VIP تهیه کنید.**

💰 **قیمت VIP:** ۱۹۹,۰۰۰ تومان ماهانه

📌 **درخواست VIP:** @Amir92aa
"""
    
    PRO_ANALYSIS = """
💎 **تحلیل پیشرفته (VIP)**

📊 **تحلیل کامل با تمام امکانات:**

🔬 **۳۰+ اندیکاتور:**
• RSI, MACD, Stochastic
• Bollinger Bands, Keltner
• Ichimoku, ADX, ATR
• MFI, CCI, Williams %R
• SMA, EMA, WMA, HMA
• و ...

🎯 **سیگنال‌های دقیق:**
• خرید/فروش/نگهداری
• ۳ هدف قیمتی
• حد ضرر دقیق
• نسبت ریسک/پاداش
• سطح اطمینان بالا

🤖 **تحلیل هوش مصنوعی:**
• تحلیل تخصصی
• پیش‌بینی قیمت
• تحلیل احساسات
• استراتژی معاملاتی

💎 **فقط VIP ها میتوانند از این تحلیل استفاده کنند.**

💰 **قیمت VIP:** ۱۹۹,۰۰۰ تومان ماهانه

📌 **درخواست VIP:** @Amir92aa
"""
    
    REQUEST_VIP = """
💎 **درخواست VIP**

📝 **برای دریافت VIP، مراحل زیر را انجام دهید:**

1️⃣ **واریز مبلغ:**
مبلغ مورد نظر را به کارت زیر واریز کنید:
💳 `6063731196254479`
🏦 به نام: **به مرد**

2️⃣ **ارسال رسید:**
پس از واریز، از رسید عکس بگیرید و به ادمین ارسال کنید

3️⃣ **تایید:**
ادمین @Amir92aa رسید شما را بررسی و تایید میکند

4️⃣ **فعال‌سازی:**
پس از تایید، VIP شما فعال میشود

⏱️ **زمان تقریبی تایید:** ۲۴ ساعت

⚠️ **توجه:** حتماً نام کاربری خود را در رسید یادداشت کنید.

📱 **ارسال رسید به ادمین:** @Amir92aa
"""

# ==================== کلاس کیبورد لوکس ====================

class LuxKeyboard:
    """کیبوردهای شیک و لوکس"""
    
    # ==================== منوی اصلی کاربر ====================
    
    @staticmethod
    def user_main_menu() -> InlineKeyboardMarkup:
        """منوی اصلی کاربر با طراحی لوکس"""
        keyboard = [
            [
                InlineKeyboardButton(f"📊 تحلیل لحظه‌ای", callback_data="analysis")
            ],
            [
                InlineKeyboardButton(f"🆓 تحلیل رایگان", callback_data="free_analysis"),
                InlineKeyboardButton(f"💎 تحلیل VIP", callback_data="pro_analysis")
            ],
            [
                InlineKeyboardButton(f"📡 سیگنال خرید", callback_data="signal_buy"),
                InlineKeyboardButton(f"📡 سیگنال فروش", callback_data="signal_sell")
            ],
            [
                InlineKeyboardButton(f"💼 کیف پول", callback_data="wallet"),
                InlineKeyboardButton(f"💎 VIP", callback_data="vip")
            ],
            [
                InlineKeyboardButton(f"📋 سیگنال‌ها", callback_data="signals_menu")
            ],
            [
                InlineKeyboardButton(f"📖 راهنما", callback_data="help"),
                InlineKeyboardButton(f"🆘 پشتیبانی", callback_data="support")
            ],
            [
                InlineKeyboardButton(f"⚙️ تنظیمات", callback_data="settings")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ==================== منوی اصلی ادمین ====================
    
    @staticmethod
    def admin_main_menu() -> InlineKeyboardMarkup:
        """منوی اصلی ادمین با طراحی لوکس"""
        keyboard = [
            [
                InlineKeyboardButton(f"👥 مدیریت کاربران", callback_data="admin_users")
            ],
            [
                InlineKeyboardButton(f"💰 مدیریت پرداخت‌ها", callback_data="admin_payments")
            ],
            [
                InlineKeyboardButton(f"💎 مدیریت VIP", callback_data="admin_vip")
            ],
            [
                InlineKeyboardButton(f"📢 ارسال پیام همگانی", callback_data="admin_broadcast")
            ],
            [
                InlineKeyboardButton(f"📡 ارسال به کانال", callback_data="admin_send_channel")
            ],
            [
                InlineKeyboardButton(f"🔧 مدیریت API", callback_data="admin_api")
            ],
            [
                InlineKeyboardButton(f"💾 بکاپ و بازیابی", callback_data="admin_backup")
            ],
            [
                InlineKeyboardButton(f"🚪 خروج / مدیریت سرور", callback_data="admin_exit")
            ],
            [
                InlineKeyboardButton(f"🔙 بازگشت به منو", callback_data="back_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ==================== منوی VIP ====================
    
    @staticmethod
    def vip_menu() -> InlineKeyboardMarkup:
        """منوی VIP با طراحی لوکس"""
        keyboard = [
            [
                InlineKeyboardButton(f"💎 VIP ماهانه - ۱۹۹,۰۰۰ تومان", callback_data="vip_monthly")
            ],
            [
                InlineKeyboardButton(f"💎 VIP سالانه - ۱,۹۹۰,۰۰۰ تومان", callback_data="vip_yearly")
            ],
            [
                InlineKeyboardButton(f"👑 VIP مادام‌العمر - ۴,۹۹۰,۰۰۰ تومان", callback_data="vip_lifetime")
            ],
            [
                InlineKeyboardButton(f"📋 راهنمای خرید", callback_data="vip_guide")
            ],
            [
                InlineKeyboardButton(f"📱 درخواست VIP", callback_data="vip_request")
            ],
            [
                InlineKeyboardButton(f"ℹ️ وضعیت VIP", callback_data="vip_status")
            ],
            [
                InlineKeyboardButton(f"🔙 بازگشت", callback_data="back_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ==================== منوی سیگنال‌ها ====================
    
    @staticmethod
    def signals_menu() -> InlineKeyboardMarkup:
        """منوی سیگنال‌ها"""
        keyboard = [
            [
                InlineKeyboardButton(f"📊 دریافت تحلیل", callback_data="analysis")
            ],
            [
                InlineKeyboardButton(f"🆓 تحلیل رایگان", callback_data="free_analysis"),
                InlineKeyboardButton(f"💎 تحلیل VIP", callback_data="pro_analysis")
            ],
            [
                InlineKeyboardButton(f"👤 حساب کاربری", callback_data="wallet")
            ],
            [
                InlineKeyboardButton(f"📖 راهنما", callback_data="help")
            ],
            [
                InlineKeyboardButton(f"🆘 پشتیبانی", callback_data="support")
            ],
            [
                InlineKeyboardButton(f"💎 پنل VIP", callback_data="vip")
            ],
            [
                InlineKeyboardButton(f"🔙 بازگشت به منو", callback_data="back_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ==================== منوی کیف پول ====================
    
    @staticmethod
    def wallet_menu() -> InlineKeyboardMarkup:
        """منوی کیف پول"""
        keyboard = [
            [
                InlineKeyboardButton(f"💰 شارژ کیف پول", callback_data="wallet_deposit")
            ],
            [
                InlineKeyboardButton(f"📊 تاریخچه تراکنش‌ها", callback_data="wallet_history")
            ],
            [
                InlineKeyboardButton(f"📈 گزارش معاملات", callback_data="wallet_report")
            ],
            [
                InlineKeyboardButton(f"🔑 کد معرف", callback_data="wallet_referral")
            ],
            [
                InlineKeyboardButton(f"💎 خرید VIP", callback_data="vip")
            ],
            [
                InlineKeyboardButton(f"🔙 بازگشت", callback_data="back_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ==================== منوی تنظیمات ====================
    
    @staticmethod
    def settings_menu(notifications: str = "فعال", timeframe: str = "۴ساعته",
                     ai_status: str = "فعال", language: str = "فارسی") -> InlineKeyboardMarkup:
        """منوی تنظیمات"""
        keyboard = [
            [
                InlineKeyboardButton(f"🔔 اعلان‌ها: {notifications}", callback_data="settings_notifications")
            ],
            [
                InlineKeyboardButton(f"📊 تایم‌فریم: {timeframe}", callback_data="settings_timeframe")
            ],
            [
                InlineKeyboardButton(f"🤖 AI: {ai_status}", callback_data="settings_ai")
            ],
            [
                InlineKeyboardButton(f"🌍 زبان: {language}", callback_data="settings_language")
            ],
            [
                InlineKeyboardButton(f"💰 واحد پول", callback_data="settings_currency")
            ],
            [
                InlineKeyboardButton(f"🔒 امنیت", callback_data="settings_security")
            ],
            [
                InlineKeyboardButton(f"🔙 بازگشت", callback_data="back_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ==================== منوی پشتیبانی ====================
    
    @staticmethod
    def support_menu() -> InlineKeyboardMarkup:
        """منوی پشتیبانی"""
        keyboard = [
            [
                InlineKeyboardButton(f"📱 تماس با پشتیبانی", callback_data="support_contact")
            ],
            [
                InlineKeyboardButton(f"📧 ارسال ایمیل", callback_data="support_email")
            ],
            [
                InlineKeyboardButton(f"💬 چت آنلاین", callback_data="support_chat")
            ],
            [
                InlineKeyboardButton(f"❓ سوالات متداول", callback_data="support_faq")
            ],
            [
                InlineKeyboardButton(f"🎫 تیکت جدید", callback_data="support_ticket")
            ],
            [
                InlineKeyboardButton(f"🔙 بازگشت", callback_data="back_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ==================== منوی مدیریت کاربران ====================
    
    @staticmethod
    def admin_users_menu() -> InlineKeyboardMarkup:
        """منوی مدیریت کاربران"""
        keyboard = [
            [
                InlineKeyboardButton(f"📋 لیست کاربران", callback_data="admin_users_list")
            ],
            [
                InlineKeyboardButton(f"👑 مدیر کردن", callback_data="admin_users_make_admin"),
                InlineKeyboardButton(f"🔨 بن کردن", callback_data="admin_users_ban")
            ],
            [
                InlineKeyboardButton(f"🔓 آنبن کردن", callback_data="admin_users_unban"),
                InlineKeyboardButton(f"🗑️ حذف کاربر", callback_data="admin_users_delete")
            ],
            [
                InlineKeyboardButton(f"📊 آمار کاربران", callback_data="admin_users_stats")
            ],
            [
                InlineKeyboardButton(f"🔙 بازگشت", callback_data="admin_panel")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ==================== منوی مدیریت پرداخت‌ها ====================
    
    @staticmethod
    def admin_payments_menu() -> InlineKeyboardMarkup:
        """منوی مدیریت پرداخت‌ها"""
        keyboard = [
            [
                InlineKeyboardButton(f"⏳ پرداخت‌های در انتظار", callback_data="admin_payments_pending")
            ],
            [
                InlineKeyboardButton(f"✅ پرداخت‌های تایید شده", callback_data="admin_payments_completed")
            ],
            [
                InlineKeyboardButton(f"📊 گزارش مالی", callback_data="admin_payments_report")
            ],
            [
                InlineKeyboardButton(f"💰 تنظیم قیمت‌ها", callback_data="admin_payments_prices")
            ],
            [
                InlineKeyboardButton(f"🔙 بازگشت", callback_data="admin_panel")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ==================== منوی مدیریت VIP ====================
    
    @staticmethod
    def admin_vip_menu() -> InlineKeyboardMarkup:
        """منوی مدیریت VIP"""
        keyboard = [
            [
                InlineKeyboardButton(f"⏳ درخواست‌های VIP", callback_data="admin_vip_requests")
            ],
            [
                InlineKeyboardButton(f"✅ تایید همه درخواست‌ها", callback_data="admin_vip_confirm_all")
            ],
            [
                InlineKeyboardButton(f"📊 آمار VIP", callback_data="admin_vip_stats")
            ],
            [
                InlineKeyboardButton(f"📋 لیست کاربران VIP", callback_data="admin_vip_list")
            ],
            [
                InlineKeyboardButton(f"🔙 بازگشت", callback_data="admin_panel")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ==================== منوی مدیریت API ====================
    
    @staticmethod
    def admin_api_menu() -> InlineKeyboardMarkup:
        """منوی مدیریت API"""
        keyboard = [
            [
                InlineKeyboardButton(f"🔄 ریست API", callback_data="admin_api_reset")
            ],
            [
                InlineKeyboardButton(f"📊 وضعیت API", callback_data="admin_api_status")
            ],
            [
                InlineKeyboardButton(f"🔑 تغییر کلیدها", callback_data="admin_api_keys")
            ],
            [
                InlineKeyboardButton(f"📈 گزارش API", callback_data="admin_api_report")
            ],
            [
                InlineKeyboardButton(f"🔙 بازگشت", callback_data="admin_panel")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ==================== منوی بکاپ ====================
    
    @staticmethod
    def admin_backup_menu() -> InlineKeyboardMarkup:
        """منوی بکاپ و بازیابی"""
        keyboard = [
            [
                InlineKeyboardButton(f"💾 ایجاد بکاپ", callback_data="admin_backup_create")
            ],
            [
                InlineKeyboardButton(f"📥 بازیابی بکاپ", callback_data="admin_backup_restore")
            ],
            [
                InlineKeyboardButton(f"📋 لیست بکاپ‌ها", callback_data="admin_backup_list")
            ],
            [
                InlineKeyboardButton(f"🗑️ حذف بکاپ", callback_data="admin_backup_delete")
            ],
            [
                InlineKeyboardButton(f"⚙️ تنظیمات بکاپ", callback_data="admin_backup_settings")
            ],
            [
                InlineKeyboardButton(f"🔙 بازگشت", callback_data="admin_panel")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ==================== منوی مدیریت سرور ====================
    
    @staticmethod
    def admin_exit_menu() -> InlineKeyboardMarkup:
        """منوی خروج و مدیریت سرور"""
        keyboard = [
            [
                InlineKeyboardButton(f"🔄 ریستارت ربات", callback_data="admin_restart")
            ],
            [
                InlineKeyboardButton(f"⏹️ توقف ربات", callback_data="admin_shutdown")
            ],
            [
                InlineKeyboardButton(f"📊 وضعیت سرور", callback_data="admin_server_status")
            ],
            [
                InlineKeyboardButton(f"📈 لاگ‌های سیستم", callback_data="admin_server_logs")
            ],
            [
                InlineKeyboardButton(f"🧹 پاکسازی کش", callback_data="admin_clear_cache")
            ],
            [
                InlineKeyboardButton(f"🔙 بازگشت", callback_data="admin_panel")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ==================== منوی صفحه‌بندی ====================
    
    @staticmethod
    def pagination_menu(page: int, total_pages: int, callback_prefix: str) -> InlineKeyboardMarkup:
        """منوی صفحه‌بندی"""
        keyboard = []
        row = []
        
        if page > 1:
            row.append(InlineKeyboardButton(f"{LuxEmoji.PREV} قبلی", callback_data=f"{callback_prefix}_{page-1}"))
        
        row.append(InlineKeyboardButton(f"📄 {page}/{total_pages}", callback_data="noop"))
        
        if page < total_pages:
            row.append(InlineKeyboardButton(f"بعدی {LuxEmoji.NEXT}", callback_data=f"{callback_prefix}_{page+1}"))
        
        keyboard.append(row)
        keyboard.append([InlineKeyboardButton(f"{LuxEmoji.BACK} بازگشت", callback_data="back_main")])
        
        return InlineKeyboardMarkup(keyboard)
    
    # ==================== منوی تأیید ====================
    
    @staticmethod
    def confirm_menu(action: str, data: str) -> InlineKeyboardMarkup:
        """منوی تأیید"""
        keyboard = [
            [
                InlineKeyboardButton(f"{LuxEmoji.CHECK} تأیید", callback_data=f"confirm_{action}_{data}"),
                InlineKeyboardButton(f"{LuxEmoji.CROSS} لغو", callback_data="cancel")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ==================== منوی ارسال همگانی ====================
    
    @staticmethod
    def broadcast_menu() -> InlineKeyboardMarkup:
        """منوی ارسال پیام همگانی"""
        keyboard = [
            [
                InlineKeyboardButton(f"📢 به همه کاربران", callback_data="broadcast_all")
            ],
            [
                InlineKeyboardButton(f"💎 به کاربران VIP", callback_data="broadcast_vip")
            ],
            [
                InlineKeyboardButton(f"🆓 به کاربران عادی", callback_data="broadcast_normal")
            ],
            [
                InlineKeyboardButton(f"📊 با آمار", callback_data="broadcast_with_stats")
            ],
            [
                InlineKeyboardButton(f"🔙 بازگشت", callback_data="admin_panel")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    # ==================== کیبوردهای پاسخ ====================
    
    @staticmethod
    def reply_main_menu() -> ReplyKeyboardMarkup:
        """کیبورد پاسخ اصلی"""
        keyboard = [
            [KeyboardButton(f"{LuxEmoji.ANALYSIS} تحلیل"), KeyboardButton(f"{LuxEmoji.SIGNAL} سیگنال")],
            [KeyboardButton(f"{LuxEmoji.WALLET} کیف پول"), KeyboardButton(f"{LuxEmoji.VIP} VIP")],
            [KeyboardButton(f"{LuxEmoji.HELP} راهنما"), KeyboardButton(f"{LuxEmoji.SUPPORT} پشتیبانی")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    @staticmethod
    def reply_cancel() -> ReplyKeyboardMarkup:
        """کیبورد لغو"""
        keyboard = [[KeyboardButton(f"{LuxEmoji.CROSS} لغو")]]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    @staticmethod
    def reply_back() -> ReplyKeyboardMarkup:
        """کیبورد بازگشت"""
        keyboard = [[KeyboardButton(f"{LuxEmoji.BACK} بازگشت")]]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ==================== کلاس سازنده منوی پویا ====================

class DynamicMenuBuilder:
    """سازنده منوی پویا و هوشمند"""
    
    def __init__(self):
        self.keyboard = LuxKeyboard()
    
    def get_user_menu(self, user_data: Dict[str, Any]) -> InlineKeyboardMarkup:
        """دریافت منوی پویا بر اساس وضعیت کاربر"""
        is_vip = user_data.get('is_vip', False)
        is_admin = user_data.get('is_admin', False)
        free_analysis_left = user_data.get('free_analysis', 3)
        
        keyboard = []
        
        # دکمه‌های اصلی
        keyboard.append([
            InlineKeyboardButton(f"📊 تحلیل لحظه‌ای", callback_data="analysis")
        ])
        
        # تحلیل رایگان و VIP
        free_label = f"🆓 تحلیل رایگان ({free_analysis_left})"
        keyboard.append([
            InlineKeyboardButton(free_label, callback_data="free_analysis"),
            InlineKeyboardButton(f"💎 تحلیل VIP", callback_data="pro_analysis")
        ])
        
        # سیگنال‌ها
        keyboard.append([
            InlineKeyboardButton(f"📡 سیگنال خرید", callback_data="signal_buy"),
            InlineKeyboardButton(f"📡 سیگنال فروش", callback_data="signal_sell")
        ])
        
        # VIP
        if is_vip:
            keyboard.append([
                InlineKeyboardButton(f"💎 پنل VIP", callback_data="vip_panel")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton(f"💎 خرید VIP", callback_data="vip")
            ])
        
        keyboard.append([
            InlineKeyboardButton(f"💼 کیف پول", callback_data="wallet")
        ])
        
        keyboard.append([
            InlineKeyboardButton(f"📋 سیگنال‌ها", callback_data="signals_menu")
        ])
        
        keyboard.append([
            InlineKeyboardButton(f"📖 راهنما", callback_data="help"),
            InlineKeyboardButton(f"🆘 پشتیبانی", callback_data="support")
        ])
        
        # ادمین
        if is_admin:
            keyboard.append([
                InlineKeyboardButton(f"👑 پنل ادمین", callback_data="admin_panel")
            ])
        
        return InlineKeyboardMarkup(keyboard)
    
    def get_vip_menu(self, is_active: bool = False) -> InlineKeyboardMarkup:
        """دریافت منوی VIP پویا"""
        keyboard = []
        
        if not is_active:
            keyboard.append([
                InlineKeyboardButton(f"💎 VIP ماهانه - ۱۹۹,۰۰۰ تومان", callback_data="vip_monthly")
            ])
            keyboard.append([
                InlineKeyboardButton(f"💎 VIP سالانه - ۱,۹۹۰,۰۰۰ تومان", callback_data="vip_yearly")
            ])
            keyboard.append([
                InlineKeyboardButton(f"👑 VIP مادام‌العمر - ۴,۹۹۰,۰۰۰ تومان", callback_data="vip_lifetime")
            ])
            keyboard.append([
                InlineKeyboardButton(f"📋 راهنمای خرید", callback_data="vip_guide")
            ])
            keyboard.append([
                InlineKeyboardButton(f"📱 درخواست VIP", callback_data="vip_request")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton(f"💎 وضعیت VIP فعال", callback_data="vip_status")
            ])
            keyboard.append([
                InlineKeyboardButton(f"📊 آمار VIP", callback_data="vip_stats")
            ])
        
        keyboard.append([
            InlineKeyboardButton(f"🔙 بازگشت", callback_data="back_main")
        ])
        
        return InlineKeyboardMarkup(keyboard)

# ==================== Export ====================

lux_keyboard = LuxKeyboard()
menu_builder = DynamicMenuBuilder()

def get_keyboard() -> LuxKeyboard:
    return lux_keyboard

def get_menu_builder() -> DynamicMenuBuilder:
    return menu_builder
