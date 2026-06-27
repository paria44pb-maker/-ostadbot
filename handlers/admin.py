from aiogram import Router, types, F
from aiogram.filters import Command
from config import ADMIN_IDS
from db import q, set_plan
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

def is_admin(user_id: int):
    return user_id in ADMIN_IDS

@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("پنل ادمین فعال است.")

@router.callback_query(F.data.startswith("approve_"))
async def approve_payment(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer("Unauthorized", show_alert=True)
    user_id = int(callback.data.split("_", 1)[1])
    await set_plan(user_id, "vip", 30, f"approved_by_{callback.from_user.id}")
    await callback.message.answer(f"✅ VIP برای کاربر {user_id} فعال شد.")
    await callback.answer()

@router.callback_query(F.data.startswith("reject_"))
async def reject_payment(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer("Unauthorized", show_alert=True)
    user_id = int(callback.data.split("_", 1)[1])
    await callback.message.answer(f"❌ درخواست VIP کاربر {user_id} رد شد.")
    await callback.answer()
