import os
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# فایل حافظه
MEMORY_FILE = "memory.json"

# ========== مدیریت حافظه ==========
def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

# ========== تنظیمات شخصیت ==========
personalities = {
    "رسمی": {
        "emoji": "👔",
        "prompt": "تو یک دستیار رسمی و حرفه‌ای هستی. پاسخ‌هایت کوتاه، دقیق و محترمانه باشد. از کلمات غیرادبی و شوخی پرهیز کن."
    },
    "شوخ‌طبع": {
        "emoji": "😄",
        "prompt": "تو یک دستیار شوخ و بامزه هستی. با خنده و جوک پاسخ بده. انرژی مثبت بده ولی اطلاعات درست ارائه کن."
    },
    "خشک و زننده": {
        "emoji": "🗿",
        "prompt": "تو یک دستیار خشک، بی‌احساس و زننده هستی. پاسخ‌هایت کوتاه، تند و بدون هیچ احساسی باشد. حوصله نداری!"
    },
    "علمی": {
        "emoji": "🔬",
        "prompt": "تو یک دانشمند و محقق هستی. پاسخ‌هایت با جزئیات علمی، دقیق و با استناد به داده‌ها باشد."
    },
    "صمیمی": {
        "emoji": "🤗",
        "prompt": "تو یک دوست صمیمی و مهربان هستی. با لحن گرم و دلنشین پاسخ بده. همیشه حامی و مثبت باش."
    },
    "فیلسوف": {
        "emoji": "🧠",
        "prompt": "تو یک فیلسوف عمیق هستی. پاسخ‌هایت با سوالات فلسفی و تفکر عمیق همراه باشد. به معنی زندگی هم فکر کن!"
    },
    "معلم": {
        "emoji": "📚",
        "prompt": "تو یک معلم صبور هستی. پاسخ‌هایت را قدم به قدم و آموزشی بده. مثال بزن و ساده توضیح بده."
    },
    "سرسخت": {
        "emoji": "⚡",
        "prompt": "تو یک فرد سرسخت و قاطع هستی. پاسخ‌هایت محکم، بی‌چون و چرا و با اعتماد به نفس بالا باشد."
    }
}

# ========== منوی اصلی ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎭 انتخاب شخصیت AI", callback_data="personality")],
        [InlineKeyboardButton("🧠 گفتگو با هوش مصنوعی", callback_data="chat")],
        [InlineKeyboardButton("📜 تاریخچه حافظه", callback_data="history")],
        [InlineKeyboardButton("🗑 پاک کردن حافظه", callback_data="clear_memory")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    await update.message.reply_text(
        "🌟 **ربات هوشمند Groq با حافظه و شخصیت** 🌟\n\n"
        "✨ **قابلیت‌ها:**\n"
        "• ۸ شخصیت مختلف برای AI\n"
        "• حافظه دائمی (چیزی که گفتی یادش میاد)\n"
        "• پاسخ‌های سریع و هوشمند\n\n"
        f"🎭 شخصیت فعلی: **رسمی** 👔\n\n"
        "از منوی زیر انتخاب کن 👇",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ========== منوی انتخاب شخصیت ==========
async def personality_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for name, data in personalities.items():
        keyboard.append([InlineKeyboardButton(f"{data['emoji']} {name}", callback_data=f"set_personality_{name}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    
    current = context.user_data.get("personality", "رسمی")
    await update.callback_query.edit_message_text(
        f"🎭 **انتخاب شخصیت هوش مصنوعی** 🎭\n\n"
        f"شخصیت فعلی: **{current}** {personalities[current]['emoji']}\n\n"
        "هر کدوم رو دوست داری انتخاب کن:\n\n"
        "👔 رسمی - پاسخ‌های حرفه‌ای و محترمانه\n"
        "😄 شوخ‌طبع - با خنده و جوک\n"
        "🗿 خشک و زننده - بی‌احساس و تند\n"
        "🔬 علمی - دقیق و جزئی‌نگر\n"
        "🤗 صمیمی - گرم و مهربان\n"
        "🧠 فیلسوف - عمیق و فلسفی\n"
        "📚 معلم - آموزشی و صبور\n"
        "⚡ سرسخت - قاطع و محکم",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ========== تغییر شخصیت ==========
async def set_personality(update: Update, context: ContextTypes.DEFAULT_TYPE, personality: str):
    context.user_data["personality"] = personality
    context.user_data["system_prompt"] = personalities[personality]["prompt"]
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await update.callback_query.edit_message_text(
        f"✅ شخصیت به **{personality}** {personalities[personality]['emoji']} تغییر کرد!\n\n"
        "حالا می‌تونی با من گفتگو کنی.\n"
        "از منوی اصلی /start هر سوالی بپرسی با همین شخصیت جواب می‌دم.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ========== منوی گفتگو ==========
async def chat_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    personality = context.user_data.get("personality", "رسمی")
    await update.callback_query.edit_message_text(
        f"💬 **حالت گفتگو فعال شد!** 💬\n\n"
        f"شخصیت فعلی: **{personality}** {personalities[personality]['emoji']}\n\n"
        "📝 هر چی بپرسی با همین لحن جواب می‌دم.\n"
        "🧠 حافظه دارم! چیزایی که قبلاً گفتی رو یادم میاد.\n\n"
        "⚠️ فقط دقت کن: پیام‌هات خیلی طولانی نباشه.\n\n"
        "**سوالتو بپرس...**",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
    )
    context.user_data["chat_mode"] = True

# ========== پاسخ با Groq و حافظه ==========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("chat_mode", False):
        await update.message.reply_text("⚠️ اول /start رو بزن و بعد گزینه «گفتگو با هوش مصنوعی» رو انتخاب کن.")
        return
    
    user_id = str(update.effective_user.id)
    user_message = update.message.text
    personality = context.user_data.get("personality", "رسمی")
    system_prompt = context.user_data.get("system_prompt", personalities["رسمی"]["prompt"])
    
    # بارگذاری حافظه کاربر
    memory = load_memory()
    user_history = memory.get(user_id, [])
    
    # آخرین ۵ گفتگو رو نگه دار (برای حافظه)
    chat_history = ""
    for item in user_history[-5:]:
        chat_history += f"کاربر: {item['user']}\nAI: {item['ai']}\n"
    
    # ساخت پرامپت کامل
    full_prompt = f"""{system_prompt}

تاریخچه گفتگوهای قبلی با این کاربر:
{chat_history}

حالا کاربر این پیام را فرستاده: "{user_message}"

پاسخ بده (کوتاه و مفید باش، حداکثر ۳ خط):"""
    
    # ارسال به Groq
    await update.message.reply_chat_action("typing")
    
    if not GROQ_API_KEY:
        await update.message.reply_text("⚠️ کلید API تنظیم نشده.")
        return
    
    try:
        import httpx
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "llama3-70b-8192",
                    "messages": [{"role": "user", "content": full_prompt}],
                    "max_tokens": 300,
                    "temperature": 0.7
                }
            )
            
            if response.status_code == 200:
                ai_response = response.json()["choices"][0]["message"]["content"]
                
                # ذخیره در حافظه
                user_history.append({"user": user_message, "ai": ai_response})
                if len(user_history) > 20:
                    user_history = user_history[-20:]
                memory[user_id] = user_history
                save_memory(memory)
                
                # ارسال پاسخ با شخصیت
                emoji = personalities[personality]["emoji"]
                await update.message.reply_text(f"{emoji} **{personality}:** {ai_response}", parse_mode="Markdown")
            else:
                await update.message.reply_text(f"❌ خطا: {response.status_code}")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {str(e)}")

# ========== نمایش تاریخچه حافظه ==========
async def show_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    memory = load_memory()
    history = memory.get(user_id, [])
    
    if not history:
        text = "📜 **حافظه خالی است**\n\nهنوز هیچ گفتگویی نکردی. یه سوال بپرس تا حافظه پر بشه!"
    else:
        text = "📜 **تاریخچه گفتگوهای تو با AI** 📜\n\n"
        for i, item in enumerate(history[-5:], 1):
            text += f"{i}. شما: {item['user'][:50]}\n   🤖 AI: {item['ai'][:50]}\n\n"
        text += f"\n📊 مجموع گفتگوها: {len(history)}"
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== پاک کردن حافظه ==========
async def clear_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    memory = load_memory()
    if user_id in memory:
        del memory[user_id]
        save_memory(memory)
    text = "🗑 **حافظه پاک شد!**\n\nتمام گفتگوهای قبلی از حافظه حذف شدن."
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== راهنما ==========
async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "❓ **راهنما** ❓\n\n"
    text += "🎭 **شخصیت‌ها:** می‌تونی از منوی انتخاب شخصیت، لحن AI رو عوض کنی.\n\n"
    text += "🧠 **حافظه:** AI چیزایی که گفتی رو یادش میاد! تاریخچه گفتگوها رو می‌تونی ببینی.\n\n"
    text += "💬 **گفتگو:** بعد از انتخاب شخصیت، گزینه گفتگو رو بزن و هر سوالی بپرس.\n\n"
    text += "⚠️ **نکته:** برای شروع دوباره /start رو بزن."
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== هندلر دکمه‌ها ==========
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "back":
        context.user_data["chat_mode"] = False
        await start(update, context)
    elif data == "personality":
        await personality_menu(update, context)
    elif data == "chat":
        await chat_menu(update, context)
    elif data == "history":
        await show_history(update, context)
    elif data == "clear_memory":
        await clear_memory(update, context)
    elif data == "help":
        await help_menu(update, context)
    elif data.startswith("set_personality_"):
        personality = data.replace("set_personality_", "")
        await set_personality(update, context, personality)

# ========== اجرا ==========
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 ربات هوشمند با حافظه و شخصیت روشن شد...")
    app.run_polling()

if __name__ == "__main__":
    main()
