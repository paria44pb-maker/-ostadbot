import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_USERNAME = "@CryptoPulse606"
CHANNEL_LINK = "https://t.me/CryptoPulse606"

# ========== بررسی عضویت ==========
async def is_member(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Error checking membership: {e}")
        return False

# ========== منوی اصلی ==========
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📊 قیمت لحظه‌ای", callback_data="prices")],
        [InlineKeyboardButton("🎯 سیگنال لحظه‌ای", callback_data="signal")],
        [InlineKeyboardButton("📈 تحلیل تکنیکال", callback_data="technical")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ========== شروع ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # بررسی سریع عضویت قبلی
    if await is_member(user_id, context):
        context.user_data["is_member"] = True
        await update.message.reply_text(
            "✅ *به ربات خوش آمدید!*\n\nاز منوی زیر استفاده کنید:",
            parse_mode="Markdown",
            reply_markup=get_main_menu()
        )
        return
    
    keyboard = [
        [InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ عضو شدم", callback_data="check_membership")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    caption = """
🌟 *پلاتینیوم VIP V34* 🌟

🔔 برای استفاده از ربات، **ابتدا در کانال ما عضو شوید**.

✨ پس از عضویت، روی دکمه «عضو شدم» کلیک کنید.
"""

    try:
        with open("images/platinum_vip.jpg", "rb") as photo:
            await update.message.reply_photo(
                photo=InputFile(photo, filename="platinum_vip.jpg"),
                caption=caption,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
    except:
        await update.message.reply_text(caption, parse_mode="Markdown", reply_markup=reply_markup)

# ========== عضو شدم ==========
async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    if await is_member(user_id, context):
        context.user_data["is_member"] = True
        await query.edit_message_caption(
            caption="✅ *عضویت شما تأیید شد!*\n\nبه ربات خوش آمدید.\nاز منوی زیر استفاده کنید:",
            parse_mode="Markdown",
            reply_markup=get_main_menu()
        )
    else:
        await query.answer("❌ شما هنوز عضو کانال نشده‌اید! لطفاً ابتدا عضو شوید.", show_alert=True)

# ========== قیمت لحظه‌ای ==========
async def prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not context.user_data.get("is_member"):
        await query.edit_message_text("🔔 لطفاً ابتدا در کانال عضو شوید.")
        return
    await query.edit_message_text("📊 *قیمت لحظه‌ای*\n\nدر حال توسعه...", parse_mode="Markdown", reply_markup=get_main_menu())

# ========== سیگنال ==========
async def signal_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not context.user_data.get("is_member"):
        await query.edit_message_text("🔔 لطفاً ابتدا در کانال عضو شوید.")
        return
    await query.edit_message_text("🎯 *سیگنال لحظه‌ای*\n\nدر حال توسعه...", parse_mode="Markdown", reply_markup=get_main_menu())

# ========== تحلیل تکنیکال ==========
async def technical(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not context.user_data.get("is_member"):
        await query.edit_message_text("🔔 لطفاً ابتدا در کانال عضو شوید.")
        return
    await query.edit_message_text("📈 *تحلیل تکنیکال*\n\nدر حال توسعه...", parse_mode="Markdown", reply_markup=get_main_menu())

# ========== راهنما ==========
async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not context.user_data.get("is_member"):
        await query.edit_message_text("🔔 لطفاً ابتدا در کانال عضو شوید.")
        return
    text = """
❓ *راهنما* ❓

📊 قیمت لحظه‌ای: نمایش قیمت ارزها
🎯 سیگنال لحظه‌ای: سیگنال خرید/فروش
📈 تحلیل تکنیکال: تحلیل تکنیکال

⚠️ فقط جنبه آموزشی
"""
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_main_menu())

# ========== هندلر ==========
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data == "check_membership":
        await check_membership(update, context)
    elif data == "prices":
        await prices(update, context)
    elif data == "signal":
        await signal_now(update, context)
    elif data == "technical":
        await technical(update, context)
    elif data == "help":
        await help_menu(update, context)
    else:
        await query.answer()

# ========== اجرا ==========
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("🚀 ربات پلاتینیوم V34 راه‌اندازی شد.")
    app.run_polling()

if __name__ == "__main__":
    main()
