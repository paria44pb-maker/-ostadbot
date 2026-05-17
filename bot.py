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
        "prompt": "تو یک دستیار رسمی و حرفه‌ای هستی."
    },
    "شوخ‌طبع": {
        "emoji": "😄",
        "prompt": "تو یک دستیار شوخ و بامزه هستی."
    },
    "خشک و زننده": {
        "emoji": "🗿",
        "prompt": "تو یک دستیار خشک و بی‌احساس هستی."
    },
    "علمی": {
        "emoji": "🔬",
        "prompt": "تو یک دانشمند و محقق هستی."
    },
    "صمیمی": {
        "emoji": "🤗",
        "prompt": "تو یک دوست صمیمی و مهربان هستی."
    },
    "فیلسوف": {
        "emoji": "🧠",
        "prompt": "تو یک فیلسوف عمیق هستی."
    },
    "معلم": {
        "emoji": "📚",
        "prompt": "تو یک معلم صبور هستی."
    },
    "سرسخت": {
        "emoji": "⚡",
        "prompt": "تو یک فرد سرسخت و قاطع هستی."
    }
}

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
        "🌟 **ربات هوشمند Groq** 🌟\n\n"
        "✨ **قابلیت‌ها:**\n"
        "• ۸ شخصیت مختلف\n"
        "• حافظه دائمی\n"
        "• تشخیص هوشمند طول پاسخ (ساده→کوتاه، عمیق→مفصل)\n"
        "• حالت دانشجویی با تست\n\n"
        f"🎭 شخصیت فعلی: **{personality}** {personalities[personality]['emoji']}\n\n"
        "از منوی زیر انتخاب کن 👇",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def personality_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for name, data in personalities.items():
        keyboard.append([InlineKeyboardButton(f"{data['emoji']} {name}", callback_data=f"set_personality_{name}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    
    current = context.user_data.get("personality", "رسمی")
    await update.callback_query.edit_message_text(
        f"🎭 **انتخاب شخصیت** 🎭\n\nشخصیت فعلی: **{current}** {personalities[current]['emoji']}\n\n"
        "👔 رسمی | 😄 شوخ | 🗿 خشک | 🔬 علمی | 🤗 صمیمی | 🧠 فیلسوف | 📚 معلم | ⚡ سرسخت",
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

async def chat_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    personality = context.user_data.get("personality", "رسمی")
    await update.callback_query.edit_message_text(
        f"💬 **گفتگو فعال شد!**\n\nشخصیت: **{personality}** {personalities[personality]['emoji']}\n\n"
        "🧠 **نکته:** سوال ساده بپرسی → جواب کوتاه\n"
        "سوال تخصصی یا «توضیح بده» بگی → جواب مفصل\n\n"
        "سوالت رو بپرس...",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
    )
    context.user_data["chat_mode"] = True
    context.user_data["student_mode"] = False

async def student_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(
        "📚 **حالت دانشجویی** 📚\n\n"
        "• موضوع مورد نظرت رو بگو (مثل: پایتون، تاریخ، ریاضی، بیت‌کوین)\n"
        "• برات درس کامل میدم\n"
        "• بعدش ۵ سوال چهارگزینه‌ای میگیرم\n"
        "• نمره نهایی رو میبینی\n\n"
        "**موضوع رو بنویس...**",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
    )
    context.user_data["student_mode"] = True
    context.user_data["chat_mode"] = False
    context.user_data["waiting_for_topic"] = True

# ========== هسته اصلی: تشخیص هوشمند طول پاسخ ==========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_id = str(update.effective_user.id)
    
    # حالت دانشجویی
    if context.user_data.get("student_mode", False):
        if context.user_data.get("waiting_for_topic", False):
            context.user_data["topic"] = user_message
            context.user_data["waiting_for_topic"] = False
            await update.message.reply_text(f"📖 **آماده‌سازی درس درباره {user_message}...** ⏳")
            await teach_topic(update, context, user_message)
        else:
            answer = user_message.strip().upper()
            correct = context.user_data.get("correct_answer", "")
            if answer == correct:
                score = context.user_data.get("score", 0) + 1
                context.user_data["score"] = score
                await update.message.reply_text(f"✅ صحیح! نمره: {score}/5")
                await ask_next_question(update, context)
            else:
                await update.message.reply_text(f"❌ اشتباه! پاسخ صحیح: {correct}\nنمره: {context.user_data.get('score', 0)}/5")
                await ask_next_question(update, context)
        return
    
    # حالت عادی
    if not context.user_data.get("chat_mode", False):
        await update.message.reply_text("⚠️ اول /start و بعد «گفتگو با هوش مصنوعی» رو انتخاب کن.")
        return
    
    personality = context.user_data.get("personality", "رسمی")
    system_prompt = context.user_data.get("system_prompt", "تو یک دستیار هستی.")
    
    memory = load_memory()
    user_history = memory.get(user_id, [])
    
    chat_history = ""
    for item in user_history[-5:]:
        chat_history += f"کاربر: {item['user']}\nAI: {item['ai']}\n"
    
    # 🔥 تشخیص هوشمند طول پاسخ 🔥
    length_instruction = ""
    msg_lower = user_message.lower()
    
    # کلمات کلیدی برای پاسخ مفصل
    deep_words = ["توضیح بده", "تحلیل کن", "چرا", "چطور", "مفصل", "کامل", "راهنمایی کن", "یاد بده", "معنی", "تاریخچه", "مقایسه", "فرق", "مزایا", "معایب"]
    # کلمات کلیدی برای پاسخ کوتاه
    short_words = ["سلام", "خوبی", "چطوری", "هی", "اوکی", "باشه", "مرسی", "ممنون", "بله", "نه", "اسمت", "کی هستی"]
    
    is_deep = any(word in msg_lower for word in deep_words) or len(user_message.split()) > 8
    is_short = any(word in msg_lower for word in short_words) and len(user_message.split()) < 4
    
    if is_short and not is_deep:
        length_instruction = "پاسخ بسیار کوتاه و مستقیم بده. حداکثر ۱ خط."
    elif is_deep:
        length_instruction = "پاسخ مفصل و کامل بده. حداقل ۵ خط. مثال بزن. جزئیات بده."
    else:
        length_instruction = "پاسخ معمولی و متوسط بده. حدود ۲ تا ۳ خط."
    
    full_prompt = f"""{system_prompt}
شخصیت تو: {personality}

{length_instruction}

تاریخچه گفتگو:
{chat_history}

سوال کاربر: "{user_message}"

پاسخ بده (بدون تکرار اسم شخصیت در ابتدای پاسخ):"""
    
    await update.message.reply_chat_action("typing")
    
    if not GROQ_API_KEY:
        await update.message.reply_text("⚠️ کلید API تنظیم نشده.")
        return
    
    try:
        import httpx
        max_tokens = 300 if is_short else 1200 if is_deep else 600
        
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": full_prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                }
            )
            
            if response.status_code == 200:
                ai_response = response.json()["choices"][0]["message"]["content"]
                
                user_history.append({"user": user_message, "ai": ai_response[:200]})
                if len(user_history) > 20:
                    user_history = user_history[-20:]
                memory[user_id] = user_history
                save_memory(memory)
                
                await update.message.reply_text(ai_response, parse_mode="Markdown")
            else:
                await update.message.reply_text(f"❌ خطا: {response.status_code}")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {str(e)}")

# ========== توابع دانشجویی ==========
async def teach_topic(update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str):
    prompt = f"""درباره "{topic}" یک درس مفصل بنویس (حداقل ۱۰ خط):
1. مقدمه
2. مفاهیم اصلی با مثال
3. نکات مهم
4. جمع‌بندی"""
    
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
                await ask_quiz_question(update, context, topic)
            else:
                await update.message.reply_text("❌ خطا در آماده‌سازی درس.")
                context.user_data["student_mode"] = False
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {str(e)}")
        context.user_data["student_mode"] = False

async def ask_quiz_question(update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str):
    prompt = f"""درباره "{topic}" یک سوال چهارگزینه‌ای سخت طراحی کن.
فرمت دقیق:
سوال: [متن]
A: [گزینه]
B: [گزینه]
C: [گزینه]
D: [گزینه]
پاسخ: [حرف]"""
    
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
                lines = quiz.split("\n")
                correct = ""
                for line in lines:
                    if line.startswith("پاسخ:"):
                        correct = line.replace("پاسخ:", "").strip()
                        break
                
                context.user_data["correct_answer"] = correct
                context.user_data["score"] = 0
                context.user_data["question_count"] = 0
                
                await update.message.reply_text(f"📝 **تست - {topic}** 📝\n\n{quiz}\n\nپاسخت رو با A, B, C یا D بفرست:")
            else:
                await update.message.reply_text("❌ خطا در ساخت سوال.")
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
            f"🎉 **پایان آزمون!** 🎉\n\nنمره: {score} از 5 ({score*20}%)\n\n"
            f"{'🔥 عالی!' if score >= 4 else '📚 دوباره تلاش کن!'}\n"
            "برای درس جدید، دوباره «حالت دانشجویی» رو انتخاب کن."
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
        text = "📜 حافظه خالی است"
    else:
        text = "📜 **تاریخچه** 📜\n\n"
        for i, item in enumerate(history[-5:], 1):
            text += f"{i}. شما: {item['user'][:50]}\n   🤖: {item['ai'][:50]}\n\n"
        text += f"\n📊 مجموع: {len(history)}"
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def clear_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    memory = load_memory()
    if user_id in memory:
        del memory[user_id]
        save_memory(memory)
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await update.callback_query.edit_message_text("🗑 حافظه پاک شد!", reply_markup=InlineKeyboardMarkup(keyboard))

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "❓ **راهنما** ❓\n\n" + \
           "🎭 شخصیت‌ها: لحن AI رو عوض کن\n" + \
           "🧠 گفتگو: سوال بپرس\n" + \
           "📚 دانشجویی: درس + تست\n" + \
           "🧠 تشخیص هوشمند:\n" + \
           "   • سوال ساده (سلام، خوبی) → جواب کوتاه\n" + \
           "   • سوال تخصصی (توضیح بده، چرا) → جواب مفصل\n" + \
           "   • سوال معمولی → جواب متوسط\n\n" + \
           "برای شروع /start"
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

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
    print("🤖 ربات هوشمند با تشخیص طول پاسخ روشن شد...")
    app.run_polling()

if __name__ == "__main__":
    main()
