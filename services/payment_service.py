from config import OWNER_NAME, OWNER_CARD, VIP_PRICE_TOMAN, CHANNEL_USERNAME
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def vip_text():
    return (
        f"💰 خرید VIP ماهانه

"
        f"مبلغ: <b>{VIP_PRICE_TOMAN:,} تومان</b>
"
        f"نام: <b>{OWNER_NAME}</b>
"
        f"کارت: <code>{OWNER_CARD}</code>

"
        f"✅ بعد از واریز، رسید را ارسال کن."
    )

def vip_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ ارسال رسید", callback_data="send_receipt")],
        [InlineKeyboardButton(text="📢 عضویت در کانال", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")]
    ])
