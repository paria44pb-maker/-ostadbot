import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_USERNAME = "@CryptoPulse606"  # یوزرنیم کانال خود را وارد کنید
CHANNEL_LINK = "https://t.me/CryptoPulse606"

# ========== بررسی عضویت در کانال ==========
async def is_member(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        logger.info(f"User {user_id} status: {member.status}")
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Error checking membership: {e}")
        return False

# ========== منوی اصلی بعد از عضویت ==========
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📊 قیمت لحظه‌ای", callback_data="prices")],
        [InlineKeyboardButton("🎯 سیگنال لحظه‌ای", callback_data="signal")],
        [InlineKeyboardButton("📈 تحلیل تکنیکال", callback_data="technical")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ========== صفحه شروع با دو دکمه ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

# ========== بررسی عضویت و ورود به ربات ==========
async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    logger.info(f"Checking membership for user: {user_id}")

    if await is_member(user_id, context):
        logger.info(f"User {user_id} is a member - ACCESS GRANTED")
        context.user_data["is_member"] = True
        await query.edit_message_caption(
            caption="✅ *عضویت شما تأیید شد!* ✅\n\nبه ربات خوش آمدید.\nاز منوی زیر استفاده کنید:",
            parse_mode="Markdown",
            reply_markup=get_main_menu()
        )
    else:
        logger.warning(f"User {user_id} is NOT a member - ACCESS DENIED")
        await query.edit_message_caption(
            caption="❌ *شما هنوز عضو کانال نشده‌اید.* ❌\n\n"
                    "لطفاً ابتدا در کانال عضو شوید، سپس روی دکمه «عضو شدم» کلیک کنید.\n\n"
                    "⚠️ توجه: ربات ادمین کانال است و می‌تواند عضویت شما را بررسی کند.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_LINK)],
                [InlineKeyboardButton("✅ عضو شدم", callback_data="check_membership")]
            ])
        )

# ========== قیمت لحظه‌ای ==========
async def prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not context.user_data.get("is_member"):
        await query.edit_message_text("🔔 لطفاً ابتدا در کانال عضو شوید.")
        return
    await query.edit_message_text("📊 *قیمت لحظه‌ای*\n\nدر حال توسعه...", parse_mode="Markdown")

# ========== سیگنال لحظه‌ای ==========
async def signal_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not context.user_data.get("is_member"):
        await query.edit_message_text("🔔 لطفاً ابتدا در کانال عضو شوید.")
        return
    await query.edit_message_text("🎯 *سیگنال لحظه‌ای*\n\nدر حال توسعه...", parse_mode="Markdown")

# ========== تحلیل تکنیکال ==========
async def technical(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not context.user_data.get("is_member"):
        await query.edit_message_text("🔔 لطفاً ابتدا در کانال عضو شوید.")
        return
    await query.edit_message_text("📈 *تحلیل تکنیکال*\n\nدر حال توسعه...", parse_mode="Markdown")

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
    await query.edit_message_text(text, parse_mode="Markdown")

# ========== هندلر دکمه‌ها ==========
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    logger.info(f"Button pressed: {data}")

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

# ========== اجرای اصلی ==========
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("🚀 ربات پلاتینیوم V34 راه‌اندازی شد.")
    logger.info(f"Channel: {CHANNEL_USERNAME}")
    app.run_polling()

if __name__ == "__main__":
    main()
