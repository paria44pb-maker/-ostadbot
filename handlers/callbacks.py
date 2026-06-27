from aiogram import Router, F, types
from services.coinex_service import get_ticker
from services.payment_service import vip_text
from db import get_user, is_premium, q
from handlers.user import get_ai_count

router = Router()

@router.callback_query(F.data == "price")
async def cb_price(callback: types.CallbackQuery):
    data = await get_ticker("BTCUSDT")
    ticker = data.get("data") or {}
    await callback.message.answer(
        f"📊 BTCUSDT
"
        f"آخرین: {ticker.get('last', 'N/A')}
"
        f"باز: {ticker.get('open', 'N/A')}
"
        f"بسته: {ticker.get('close', 'N/A')}"
    )
    await callback.answer()

@router.callback_query(F.data == "ai")
async def cb_ai(callback: types.CallbackQuery):
    await callback.message.answer("🤖 از /ai استفاده کن و سوالت را بنویس.")
    await callback.answer()

@router.callback_query(F.data == "profile")
async def cb_profile(callback: types.CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.message.answer("❌ ابتدا /start را بزنید.")
        await callback.answer()
        return
    premium = await is_premium(user)
    count = await get_ai_count(callback.from_user.id)
    await callback.message.answer(
        f"👤 پروفایل

نام: {user[2]}
پلن: {user[5]}
پریمیوم: {'بله' if premium else 'خیر'}
AI امروز: {count}"
    )
    await callback.answer()

@router.callback_query(F.data == "buy_vip")
async def cb_buy_vip(callback: types.CallbackQuery):
    await callback.message.answer(vip_text())
    await callback.answer()

@router.callback_query(F.data == "send_receipt")
async def cb_send_receipt(callback: types.CallbackQuery):
    await callback.message.answer("📤 لطفاً رسید یا شماره پیگیری را به صورت متن ارسال کن.")
    await callback.answer()
