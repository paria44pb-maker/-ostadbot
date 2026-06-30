#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CryptoPulse AI Bot v3.0 - Background Tasks Module
ماژول تسک‌های پس‌زمینه، زمانبندی و پردازش خودکار
"""

import asyncio
import gc
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from bot2 import get_config
from bot3 import db_manager
from bot4 import get_time, get_cache
from bot5 import get_market
from bot6 import get_ai
from bot8 import LuxEmoji
from bot12 import get_channel_manager, get_auto_channel_tasks

config = get_config()
time_manager = get_time()
cache = get_cache()
market = get_market()
ai_manager = get_ai()

# ==================== کلاس تسک‌های پس‌زمینه ====================

class BackgroundTasks:
    """مدیریت تسک‌های پس‌زمینه"""
    
    def __init__(self, bot=None):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        self.tasks = []
    
    async def start_all(self):
        """شروع همه تسک‌ها"""
        self.is_running = True
        
        # تسک‌های زمانبندی شده
        self.scheduler.add_job(
            self.cleanup_cache,
            IntervalTrigger(minutes=5),
            id='cleanup_cache'
        )
        
        self.scheduler.add_job(
            self.update_market_data,
            IntervalTrigger(minutes=10),
            id='update_market_data'
        )
        
        self.scheduler.add_job(
            self.check_vip_expiry,
            IntervalTrigger(hours=1),
            id='check_vip_expiry'
        )
        
        self.scheduler.add_job(
            self.generate_daily_backup,
            CronTrigger(hour=2, minute=0),
            id='daily_backup'
        )
        
        self.scheduler.add_job(
            self.cleanup_old_data,
            CronTrigger(hour=3, minute=0),
            id='cleanup_old_data'
        )
        
        self.scheduler.start()
        
        # تسک‌های دائمی
        asyncio.create_task(self.auto_channel_task())
        asyncio.create_task(self.health_monitor())
        asyncio.create_task(self.memory_optimizer())
        
        print("✅ Background tasks started")
    
    async def stop_all(self):
        """توقف همه تسک‌ها"""
        self.is_running = False
        self.scheduler.shutdown()
        print("⏹️ Background tasks stopped")
    
    # ==================== تسک‌های زمانبندی ====================
    
    async def cleanup_cache(self):
        """پاکسازی کش"""
        cache.clear()
        gc.collect()
    
    async def update_market_data(self):
        """بروزرسانی داده‌های بازار"""
        try:
            tickers = await market.get_all_prices()
            cache.set('market_data', tickers)
        except:
            pass
    
    async def check_vip_expiry(self):
        """بررسی انقضای VIP"""
        try:
            with db_manager.get_session() as session:
                from bot3 import User
                expired_users = session.query(User).filter(
                    User.is_vip == True,
                    User.vip_expire < time_manager.now()
                ).all()
                
                for user in expired_users:
                    user.is_vip = False
                    user.vip_level = 0
                    session.commit()
        except:
            pass
    
    async def generate_daily_backup(self):
        """ایجاد بکاپ روزانه"""
        try:
            result = db_manager.backup()
            if result.get('success'):
                # حذف بکاپ‌های قدیمی
                import os
                backup_dir = "./backups"
                if os.path.exists(backup_dir):
                    files = sorted(
                        [os.path.join(backup_dir, f) for f in os.listdir(backup_dir)],
                        key=os.path.getctime
                    )
                    # نگهداری ۷ روز
                    for f in files[:-7]:
                        os.remove(f)
        except:
            pass
    
    async def cleanup_old_data(self):
        """پاکسازی داده‌های قدیمی"""
        try:
            # حذف سیگنال‌های منقضی شده
            with db_manager.get_session() as session:
                from bot3 import Signal
                expired = session.query(Signal).filter(
                    Signal.is_active == True,
                    Signal.created_at < time_manager.now() - timedelta(days=7)
                ).all()
                
                for signal in expired:
                    signal.is_active = False
                session.commit()
        except:
            pass
    
    # ==================== تسک‌های دائمی ====================
    
    async def auto_channel_task(self):
        """ارسال خودکار به کانال"""
        if self.bot:
            channel_tasks = get_auto_channel_tasks(self.bot)
            await channel_tasks.start()
    
    async def health_monitor(self):
        """مانیتورینگ سلامت"""
        while self.is_running:
            try:
                # بررسی دیتابیس
                db_health = db_manager.health_check()
                
                # بررسی بازار
                ticker = await market.get_market_data("BTC")
                
                # ذخیره وضعیت
                status = {
                    "database": db_health['status'],
                    "market": "healthy" if ticker else "unhealthy",
                    "time": time_manager.now_persian()
                }
                cache.set("health_status", status)
                
                await asyncio.sleep(300)
            except:
                await asyncio.sleep(60)
    
    async def memory_optimizer(self):
        """بهینه‌سازی حافظه"""
        while self.is_running:
            try:
                gc.collect()
                await asyncio.sleep(600)
            except:
                await asyncio.sleep(300)

# ==================== Export ====================

background_tasks = BackgroundTasks()

def get_background_tasks() -> BackgroundTasks:
    return background_tasks
