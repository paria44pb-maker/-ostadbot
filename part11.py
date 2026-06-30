#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - VIP & Payment Management Module
ماژول مدیریت VIP و پرداخت‌ها با پشتیبانی کامل
"""

import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from bot2 import get_config
from bot3 import db_manager, user_repo, payment_repo
from bot4 import get_time, get_emoji, get_formatter, get_hash
from bot8 import lux_keyboard, LuxText, LuxEmoji

config = get_config()
time_manager = get_time()
emoji_manager = get_emoji()
formatter = get_formatter()
hash_utils = get_hash()

# ==================== کلاس مدیریت VIP ====================

class VIPManager:
    """مدیریت VIP و پرداخت‌ها"""
    
    def __init__(self):
        self.vip_prices = {
            'monthly': config.get('vip_price_monthly', 199000),
            'yearly': config.get('vip_price_yearly', 1990000),
            'lifetime': config.get('vip_price_lifetime', 4990000)
        }
        self.vip_features = [
            "📊 سیگنال‌های اختصاصی VIP",
            "🤖 تحلیل پیشرفته با AI (نامحدود)",
            "🆘 پشتیبانی اولویت‌دار",
            "💎 دسترسی به ارزهای ویژه",
            "🔔 هشدارهای لحظه‌ای",
            "📈 مدیریت پورتفولیو",
            "🎯 سیگنال‌های دقیق‌تر",
            "📊 اندیکاتورهای پیشرفته",
            "🔬 تحلیل تخصصی و فاندامنتال",
            "📡 سیگنال‌های لحظه‌ای"
        ]
    
    async def request_vip(self, user_id: str, plan: str, payment_id: str) -> bool:
        """ثبت درخواست VIP"""
        price = self.vip_prices.get(plan, 0)
        
        payment = payment_repo.create(
            payment_id=payment_id,
            user_id=user_id,
            amount=price,
            currency='IRT',
            payment_type=f'vip_{plan}',
            status='pending',
            description=f'درخواست VIP {plan}'
        )
        
        return payment is not None
    
    async def activate_vip(self, user_id: str, plan: str) -> bool:
        """فعال‌سازی VIP"""
        user = user_repo.get_by_telegram_id(user_id)
        if not user:
            return False
        
        days = 30 if plan == 'monthly' else 365 if plan == 'yearly' else 9999
        
        user.is_vip = True
        user.vip_level = 1 if plan == 'monthly' else 2 if plan == 'yearly' else 3
        user.vip_plan = plan
        user.vip_expire = time_manager.now() + timedelta(days=days)
        user.vip_purchase_date = time_manager.now()
        
        user_repo.update(
            user.id,
            is_vip=True,
            vip_level=user.vip_level,
            vip_plan=user.vip_plan,
            vip_expire=user.vip_expire,
            vip_purchase_date=user.vip_purchase_date
        )
        
        return True
    
    async def check_vip_status(self, user_id: str) -> Dict[str, Any]:
        """بررسی وضعیت VIP"""
        user = user_repo.get_by_telegram_id(user_id)
        if not user:
            return {'is_vip': False, 'error': 'کاربر یافت نشد'}
        
        is_active = user.is_vip and user.is_vip_active()
        
        return {
            'is_vip': is_active,
            'plan': user.vip_plan if is_active else None,
            'expire': user.vip_expire.strftime('%Y-%m-%d') if user.vip_expire else None,
            'days_left': user.get_vip_days_left() if is_active else 0
        }
    
    def get_vip_price(self, plan: str) -> int:
        return self.vip_prices.get(plan, 0)
    
    def get_vip_features(self) -> List[str]:
        return self.vip_features

# ==================== کلاس هندلرهای VIP ====================

class VIPHandlers:
    """هندلرهای VIP و پرداخت"""
    
    def __init__(self):
        self.vip_manager = VIPManager()
    
    async def show_vip_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش پنل VIP"""
        user_id = str(update.effective_user.id)
        status = await self.vip_manager.check_vip_status(user_id)
        
        is_vip = status.get('is_vip', False)
        
        if is_vip:
            text = f"""
💎 **پنل VIP شما**

📊 **وضعیت:** 🟢 فعال
📅 **طرح:** {status.get('plan', 'نامشخص')}
📆 **انقضا:** {status.get('expire', 'ندارد')}
⏳ **روزهای باقی‌مانده:** {status.get('days_left', 0)}

✨ **امکانات VIP:**
"""
            for feature in self.vip_manager.get_vip_features():
                text += f"• {feature}\n"
        else:
            text = LuxText.VIP_PANEL
        
        await update.message.reply_text(
            text,
            reply_markup=lux_keyboard.vip_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_vip_guide(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش راهنمای خرید VIP"""
        await update.message.reply_text(
            LuxText.REQUEST_VIP,
            reply_markup=lux_keyboard.vip_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_vip_purchase(self, update: Update, context: ContextTypes.DEFAULT_TYPE, plan: str):
        """پردازش خرید VIP"""
        user_id = str(update.effective_user.id)
        price = self.vip_manager.get_vip_price(plan)
        
        plan_names = {
            'monthly': 'ماهانه',
            'yearly': 'سالانه',
            'lifetime': 'مادام‌العمر'
        }
        plan_name = plan_names.get(plan, 'ماهانه')
        
        payment_id = hash_utils.generate_payment_id()
        context.user_data['vip_plan'] = plan
        context.user_data['vip_price'] = price
        context.user_data['payment_id'] = payment_id
        
        await update.message.reply_text(
            f"💎 **خرید VIP {plan_name}**\n\n"
            f"💰 **مبلغ:** {price:,} تومان\n"
            f"📅 **مدت:** {plan_name}\n\n"
            f"💳 **شماره کارت:** `{config.get('vip_payment_card', '6063731196254479')}`\n"
            f"🏦 **به نام:** {config.get('vip_payment_holder', 'به مرد')}\n\n"
            f"📤 پس از واریز، تصویر رسید را ارسال کنید.\n\n"
            f"📱 **ادمین:** @{config.get('vip_admin_username', 'Amir92aa')}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"📤 ارسال رسید", callback_data=f"vip_send_receipt_{plan}")],
                [InlineKeyboardButton(f"🔙 بازگشت", callback_data="vip")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_receipt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """پردازش رسید پرداخت"""
        user_id = str(update.effective_user.id)
        
        if not context.user_data.get('vip_plan'):
            await update.message.reply_text(
                f"{LuxEmoji.INFO} ابتدا طرح VIP را انتخاب کنید.",
                reply_markup=lux_keyboard.vip_menu()
            )
            return
        
        plan = context.user_data.get('vip_plan')
        price = context.user_data.get('vip_price')
        payment_id = context.user_data.get('payment_id')
        
        # ذخیره تصویر
        photo = update.message.photo[-1]
        file = await photo.get_file()
        
        receipt_path = f"./receipts/receipt_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        os.makedirs("./receipts", exist_ok=True)
        await file.download_to_drive(receipt_path)
        
        # ثبت در دیتابیس
        await self.vip_manager.request_vip(user_id, plan, payment_id)
        
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
                                f"🆔 **شناسه:** {payment_id}\n"
                                f"📅 **زمان:** {time_manager.now_persian()}\n\n"
                                f"برای تایید روی دکمه زیر کلیک کنید:",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("✅ تایید پرداخت", callback_data=f"admin_confirm_payment_{payment_id}")],
                            [InlineKeyboardButton("❌ رد پرداخت", callback_data=f"admin_reject_payment_{payment_id}")]
                        ]),
                        parse_mode=ParseMode.MARKDOWN
                    )
            except:
                pass
        
        await update.message.reply_text(
            f"{LuxEmoji.SUCCESS} **رسید شما ارسال شد!**\n\n"
            f"🆔 **شناسه:** {payment_id}\n"
            f"💰 **مبلغ:** {price:,} تومان\n"
            f"📦 **نوع:** {plan}\n\n"
            f"⏳ پس از تایید ادمین، VIP شما فعال می‌شود.\n"
            f"📱 **ادمین:** @{config.get('vip_admin_username', 'Amir92aa')}",
            reply_markup=lux_keyboard.user_main_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
        
        context.user_data.clear()
    
    async def handle_confirm_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE, payment_id: str):
        """تایید پرداخت توسط ادمین"""
        user_id = str(update.effective_user.id)
        is_admin = user_id in [str(a) for a in config.get('admin_ids', [])]
        
        if not is_admin:
            await update.message.reply_text(f"{LuxEmoji.ERROR} دسترسی غیرمجاز!")
            return
        
        # پیدا کردن پرداخت
        with db_manager.get_session() as session:
            payment = session.query(Payment).filter_by(payment_id=payment_id).first()
            if not payment:
                await update.message.reply_text(
                    f"{LuxEmoji.ERROR} پرداخت یافت نشد!",
                    reply_markup=lux_keyboard.admin_main_menu()
                )
                return
            
            # تایید پرداخت
            payment.status = 'completed'
            payment.completed_at = time_manager.now()
            session.commit()
            
            # فعال‌سازی VIP
            plan = payment.payment_type.replace('vip_', '')
            await self.vip_manager.activate_vip(payment.user_id, plan)
            
            # ارسال پیام به کاربر
            user = user_repo.get_by_telegram_id(payment.user_id)
            if user:
                try:
                    await context.bot.send_message(
                        chat_id=int(user.telegram_id),
                        text=f"{LuxEmoji.SUCCESS} **VIP شما فعال شد!**\n\n"
                             f"📅 **طرح:** {plan}\n"
                             f"📆 **انقضا:** {user.vip_expire.strftime('%Y-%m-%d')}\n\n"
                             f"💎 از امکانات ویژه VIP لذت ببرید! 🎉",
                        parse_mode=ParseMode.MARKDOWN
                    )
                except:
                    pass
        
        await update.message.reply_text(
            f"{LuxEmoji.SUCCESS} **پرداخت تایید شد!**\n"
            f"🆔 شناسه: {payment_id}\n"
            f"👤 کاربر: {payment.user_id}\n"
            f"✅ VIP فعال شد.",
            reply_markup=lux_keyboard.admin_main_menu()
        )

# ==================== Export ====================

vip_manager = VIPManager()
vip_handlers = VIPHandlers()

def get_vip_manager() -> VIPManager:
    return vip_manager

def get_vip_handlers() -> VIPHandlers:
    return vip_handlers
