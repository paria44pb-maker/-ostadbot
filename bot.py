import os
import json
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MEMORY_FILE = "memory.json"

def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

personalities = {
    "رسمی": {
        "emoji": "👔",
        "prompt": "تو یک دستیار رسمی و حرفه‌ای هستی. پاسخ‌هایت کامل، دقیق و محترمانه باشد. حداقل ۵ خط پاسخ بده."
    },
    "شوخ‌طبع": {
        "emoji": "😄",
        "prompt": "تو یک دستیار شوخ و بامزه هستی. با خنده و جوک پاسخ بده. پاسخ‌هات مفصل و حداقل ۵ خط باشه."
    },
    "خشک و زننده": {
        "emoji": "🗿",
        "prompt": "تو یک دستیار خشک و بی‌احساس هستی. پاسخ‌هات کامل ولی تند و بدون احساس باشه."
    },
    "علمی": {
        "emoji": "🔬",
        "prompt": "تو یک دانشمند هستی. پاسخ‌هایت بسیار مفصل، با جزئیات علمی، مثال و استناد به داده‌ها باشد. حداقل ۷ خط."
    },
    "صمیمی": {
        "emoji": "🤗",
        "prompt": "تو یک دوست صمیمی هستی. با لحن گرم و دلنشین پاسخ بده. توضیحات کامل و مفصل بده."
    },
    "فیلسوف": {
        "emoji": "🧠",
        "prompt": "تو یک فیلسوف عمیق هستی. پاسخ‌هایت طولانی، فلسفی و همراه با سوالات عمیق باشد."
    },
    "معلم": {
        "emoji": "📚",
        "prompt": "تو یک معلم صبور هستی. پاسخ‌ها رو قدم به قدم، با مثال و توضیحات کامل بده. طوری که یک دانش‌آموز هم بفهمد."
    },
    "سرسخت": {
        "emoji": "⚡",
        "prompt": "تو یک فرد سرسخت و قاطع هستی. پاسخ‌هایت محکم، کامل و با اعتماد به نفس بالا باشد."
    }
}

# ========== منوی اصلی ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    personality = context.user_data.get("personality", "رسمی")
    keyboard = [
        [InlineKeyboardButton("🎭 انتخاب شخصیت AI", callback_data="personality")],
        [InlineKeyboardButton("🧠 گفتگو با هوش مصنوعی", callback_data="chat")],
        [InlineKeyboardButton("📚 حالت دانشجویی (تست)", callback_data="student")],
        [InlineKeyboardButton("📜 تاریخچه حافظه", callback_data="history")],
        [InlineKeyboardButton("🗑 پاک کردن حافظه", callback_data="clear_memory")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    await update.message.reply_text(
        "🌟 **ربات هوشمند Groq با حافظه و شخصیت** 🌟\n\n"
        "✨ **قابلیت‌ها:**\n"
        "• ۸ شخصیت مختلف برای AI\n"
        "• حافظه دائمی\n"
        "• پاسخ‌های مفصل و کامل\n"
        "• حالت دانشجویی با تست چهار جوابی\n\n"
        f"🎭 شخصیت فعلی: **{personality}** {personalities[personality]['emoji']}\n\n"
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
        "شخصیت مورد نظرت رو انتخاب کن:\n\n"
        "👔 رسمی - پاسخ‌های حرفه‌ای\n"
        "😄 شوخ‌طبع - با خنده و جوک\n"
        "🗿 خشک و زننده - بی‌احساس\n"
        "🔬 علمی - دقیق و جزئی‌نگر\n"
        "🤗 صمیمی - گرم و مهربان\n"
        "🧠 فیلسوف - عمیق و فلسفی\n"
        "📚 معلم - آموزشی و صبور\n"
        "⚡ سرسخت - قاطع و محکم",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def set_personality(update: Update, context: ContextTypes.DEFAULT_TYPE, personality: str):
    context.user_data["personality"] = personality
    context.user_data["system_prompt"] = personalities[personality]["prompt"]
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await update.callback_query.edit_message_text(
        f"✅ شخصیت به **{personality}** {personalities[personality]['emoji']} تغییر کرد!",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ========== منوی گفتگو ==========
async def chat_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    personality = context.user_data.get("personality", "رسمی")
    await update.callback_query.edit_message_text(
        f"💬 **حالت گفتگو فعال شد!** 💬\n\n"
        f"شخصیت فعلی: **{personality}** {personalities[personality]['emoji']}\n\n"
        "📝 هر سوالی بپرسی، با همون شخصیت و پاسخ مفصل جواب میدم.\n"
        "🧠 حافظه دارم!\n\n"
        "**سوالتو بپرس...**",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
    )
    context.user_data["chat_mode"] = True
    context.user_data["student_mode"] = False

# ========== حالت دانشجویی ==========
async def student_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(
        "📚 **حالت دانشجویی فعال شد!** 📚\n\n"
        "این حالت برای یادگیری و آموزش طراحی شده:\n\n"
        "• میتونی هر موضوعی که میخوای یاد بگیری رو بپرسی\n"
        "• من برات یه درس کامل با توضیحات مفصل میدم\n"
        "• بعد از درس، یه تست چهار جوابی میگیرم\n"
        "• نمره نهایی بهت اعلام میشه\n\n"
        "**لطفاً موضوع مورد نظرت رو بگو...**\n(مثل: برنامه نویسی پایتون، تاریخ ایران، ریاضی، اقتصاد، بیت‌کوین و...)\n\n"
        "⚠️ برای برگشت /start بزن",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
    )
    context.user_data["student_mode"] = True
    context.user_data["chat_mode"] = False
    context.user_data["waiting_for_topic"] = True

# ========== پاسخ معمولی با Groq (مفصل) ==========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_id = str(update.effective_user.id)
    
    # حالت دانشجویی
    if context.user_data.get("student_mode", False):
        if context.user_data.get("waiting_for_topic", False):
            context.user_data["topic"] = user_message
            context.user_data["waiting_for_topic"] = False
            await update.message.reply_text(f"📖 **در حال آماده کردن درس درباره {user_message}...** ⏳")
            await teach_topic(update, context, user_message)
        else:
            # دریافت پاسخ سوال تست
            answer = user_message.strip()
            correct = context.user_data.get("correct_answer", "")
            if answer == correct:
                score = context.user_data.get("score", 0) + 1
                context.user_data["score"] = score
                await update.message.reply_text(f"✅ **پاسخ صحیح!** 🎉\n\nنمره فعلی: {score}/5")
                await ask_next_question(update, context)
            else:
                await update.message.reply_text(f"❌ **پاسخ اشتباه!**\n\nپاسخ صحیح: {correct}\n\nنمره فعلی: {context.user_data.get('score', 0)}/5")
                await ask_next_question(update, context)
        return
    
    # حالت عادی گفتگو
    if not context.user_data.get("chat_mode", False):
        await update.message.reply_text("⚠️ اول /start رو بزن و بعد گزینه «گفتگو با هوش مصنوعی» رو انتخاب کن.")
        return
    
    personality = context.user_data.get("personality", "رسمی")
    system_prompt = context.user_data.get("system_prompt", personalities["رسمی"]["prompt"])
    
    memory = load_memory()
    user_history = memory.get(user_id, [])
    
    chat_history = ""
    for item in user_history[-5:]:
        chat_history += f"کاربر: {item['user']}\nAI: {item['ai']}\n"
    
    full_prompt = f"""{system_prompt}

تاریخچه گفتگوهای قبلی با این کاربر:
{chat_history}

حالا کاربر این پیام را فرستاده: "{user_message}"

پاسخ بده (پاسخ بسیار مفصل و کامل باشد. حداقل ۵ خط. مثال بزن. توضیحات کامل بده.):"""
    
    await update.message.reply_chat_action("typing")
    
    if not GROQ_API_KEY:
        await update.message.reply_text("⚠️ کلید API تنظیم نشده.")
        return
    
    try:
        import httpx
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": full_prompt}],
                    "max_tokens": 1500,
                    "temperature": 0.7
                }
            )
            
            if response.status_code == 200:
                ai_response = response.json()["choices"][0]["message"]["content"]
                
                user_history.append({"user": user_message, "ai": ai_response})
                if len(user_history) > 20:
                    user_history = user_history[-20:]
                memory[user_id] = user_history
                save_memory(memory)
                
                await update.message.reply_text(ai_response, parse_mode="Markdown")
            else:
                await update.message.reply_text(f"❌ خطای {response.status_code}: مشکل در ارتباط با AI. لطفاً دوباره تلاش کن.")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {str(e)}")

# ========== تدریس و تست دانشجویی ==========
async def teach_topic(update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str):
    prompt = f"""تو یک استاد حرفه‌ای هستی. میخواهی درباره موضوع "{topic}" به یک دانشجو آموزش بدی.

لطفاً یک درس کامل و مفصل بنویس شامل:
1. مقدمه و توضیح کلی درباره موضوع (حداقل ۵ خط)
2. مفاهیم اصلی و کلیدی (با مثال)
3. نکات مهم و کاربردی
4. جمع‌بندی

پاسخ بسیار مفصل و کامل باشد. حداقل ۱۵ خط."""
    
    try:
        import httpx
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 2000,
                    "temperature": 0.7
                }
            )
            
            if response.status_code == 200:
                lesson = response.json()["choices"][0]["message"]["content"]
                await update.message.reply_text(f"📚 **درس {topic}** 📚\n\n{lesson}", parse_mode="Markdown")
                
                # بعد از درس، سوال تست بپرس
                await ask_quiz_question(update, context, topic)
            else:
                await update.message.reply_text("❌ خطا در آماده‌سازی درس. دوباره تلاش کن.")
                context.user_data["student_mode"] = False
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {str(e)}")
        context.user_data["student_mode"] = False

async def ask_quiz_question(update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str):
    prompt = f"""درباره موضوع "{topic}" یک سوال چهارگزینه‌ای طراحی کن.
سوال باید مفهومی و نسبتاً سخت باشه.

فرمت پاسخ دقیقاً به این شکل باشه:
سوال: [متن سوال]
گزینه A: [متن]
گزینه B: [متن]
گزینه C: [متن]
گزینه D: [متن]
پاسخ صحیح: [حرف گزینه]

فقط همین فرمت رو برگردون، هیچ توضیح اضافه نده."""
    
    try:
        import httpx
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 500,
                    "temperature": 0.8
                }
            )
            
            if response.status_code == 200:
                quiz = response.json()["choices"][0]["message"]["content"]
                
                # استخراج پاسخ صحیح
                lines = quiz.split("\n")
                correct = ""
                for line in lines:
                    if line.startswith("پاسخ صحیح:"):
                        correct = line.replace("پاسخ صحیح:", "").strip()
                        break
                
                context.user_data["correct_answer"] = correct
                context.user_data["score"] = 0
                context.user_data["question_count"] = 0
                
                await update.message.reply_text(
                    f"📝 **تست چهارگزینه‌ای - {topic}** 📝\n\n{quiz}\n\n"
                    "لطفاً پاسخ خود را به صورت حرف A, B, C یا D وارد کن.",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text("❌ خطا در ساخت سوال. دوباره تلاش کن.")
                context.user_data["student_mode"] = False
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {str(e)}")
        context.user_data["student_mode"] = False

async def ask_next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = context.user_data.get("question_count", 0) + 1
    context.user_data["question_count"] = count
    
    if count >= 5:
        score = context.user_data.get("score", 0)
        await update.message.reply_text(
            f"🎉 **پایان آزمون!** 🎉\n\n"
            f"نمره نهایی شما: {score} از ۵\n"
            f"درصد موفقیت: {score*20}%\n\n"
            f"{'🔥 عالی! ادامه بده!' if score >= 4 else '📚 خوب بود، دوباره تلاش کن!'}\n\n"
            "برای شروع درس جدید، دوباره گزینه «حالت دانشجویی» رو انتخاب کن.",
            parse_mode="Markdown"
        )
        context.user_data["student_mode"] = False
        return
    
    topic = context.user_data.get("topic", "")
    await ask_quiz_question(update, context, topic)

# ========== بقیه منوها ==========
async def show_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    memory = load_memory()
    history = memory.get(user_id, [])
    
    if not history:
        text = "📜 **حافظه خالی است**\n\nهنوز هیچ گفتگویی نکردی."
    else:
        text = "📜 **تاریخچه گفتگوها** 📜\n\n"
        for i, item in enumerate(history[-5:], 1):
            text += f"{i}. شما: {item['user'][:60]}\n   🤖 AI: {item['ai'][:60]}\n\n"
        text += f"\n📊 مجموع گفتگوها: {len(history)}"
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def clear_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    memory = load_memory()
    if user_id in memory:
        del memory[user_id]
        save_memory(memory)
    text = "🗑 **حافظه پاک شد!**"
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "❓ **راهنما** ❓\n\n"
    text += "🎭 **شخصیت‌ها:** از منوی انتخاب شخصیت، لحن AI رو عوض کن.\n\n"
    text += "🧠 **گفتگو:** هر سوالی بپرس، پاسخ مفصل میگیری.\n\n"
    text += "📚 **حالت دانشجویی:** یه موضوع انتخاب کن، درس کامل میگیری و بعد تست چهار جوابی.\n\n"
    text += "📜 **حافظه:** تاریخچه گفتگوها ذخیره میشه.\n\n"
    text += "⚠️ برای شروع دوباره /start رو بزن."
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ========== هندلر دکمه‌ها ==========
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "back":
        context.user_data["chat_mode"] = False
        context.user_data["student_mode"] = False
        context.user_data["waiting_for_topic"] = False
        await start(update, context)
    elif data == "personality":
        await personality_menu(update, context)
    elif data == "chat":
        await chat_menu(update, context)
    elif data == "student":
        await student_menu(update, context)
    elif data == "history":
        await show_history(update, context)
    elif data == "clear_memory":
        await clear_memory(update, context)
    elif data == "help":
        await help_menu(update, context)
    elif data.startswith("set_personality_"):
        personality = data.replace("set_personality_", "")
        await set_personality(update, context, personality)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 ربات هوشمند با حالت دانشجویی روشن شد...")
    app.run_polling()

if __name__ == "__main__":
    main()
