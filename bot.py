import os
import json
import logging
import random
import httpx
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
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
    "رسمی": {"emoji": "👔", "prompt": "تو یک دستیار رسمی و حرفه‌ای هستی."},
    "شوخ‌طبع": {"emoji": "😄", "prompt": "تو یک دستیار شوخ و بامزه هستی."},
    "خشک و زننده": {"emoji": "🗿", "prompt": "تو یک دستیار خشک و بی‌احساس هستی."},
    "علمی": {"emoji": "🔬", "prompt": "تو یک دانشمند و محقق هستی."},
    "صمیمی": {"emoji": "🤗", "prompt": "تو یک دوست صمیمی و مهربان هستی."},
    "فیلسوف": {"emoji": "🧠", "prompt": "تو یک فیلسوف عمیق هستی."},
    "معلم": {"emoji": "📚", "prompt": "تو یک معلم صبور هستی."},
    "سرسخت": {"emoji": "⚡", "prompt": "تو یک فرد سرسخت و قاطع هستی."},
    "شاعرانه": {"emoji": "🎭", "prompt": "تو یک شاعر و نویسنده هستی. کلمات زیبا و دل‌نشین. از استعاره و تشبیه استفاده کن."},
    "دوستانه": {"emoji": "💕", "prompt": "تو یک دوست مهربان و گرم هستی. با محبت و عشق پاسخ بده."}
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    personality = context.user_data.get("personality", "رسمی")
    keyboard = [
        [InlineKeyboardButton("🎭 انتخاب شخصیت", callback_data="personality")],
        [InlineKeyboardButton("💬 گفتگوی دل‌چسب", callback_data="chat")],
        [InlineKeyboardButton("🎨 طراحی و عکس", callback_data="design")],
        [InlineKeyboardButton("📚 حالت دانشجویی", callback_data="student")],
        [InlineKeyboardButton("📜 تاریخچه", callback_data="history")],
        [InlineKeyboardButton("🗑 پاک کردن حافظه", callback_data="clear_memory")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    
    welcome_text = f"""
✨ **به ربات هوشمند کریپتو خوش آمدی** ✨

🍃 اینجا جاییه که هوش مصنوعی با **قلب** باهات حرف می‌زنه...
🎨 می‌تونه برات **طراحی کنه** و **عکس بسازه**
💬 با **سبک نوشتاری دل‌چسب** پاسخ می‌ده

💫 **شخصیت فعلی:** {personality} {personalities[personality]['emoji']}

⚡ **آماده‌ای تا یه تجربه متفاوت داشته باشیم؟**

از منوی زیر انتخاب کن 👇
"""
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def personality_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for name, data in personalities.items():
        keyboard.append([InlineKeyboardButton(f"{data['emoji']} {name}", callback_data=f"set_personality_{name}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    
    current = context.user_data.get("personality", "رسمی")
    await update.callback_query.edit_message_text(
        f"🎭 **انتخاب شخصیت** 🎭\n\nشخصیت فعلی: **{current}** {personalities[current]['emoji']}\n\n"
        "هر کدوم رو دوست داری انتخاب کن:\n"
        "👔 رسمی | 😄 شوخ | 🗿 خشک | 🔬 علمی | 🤗 صمیمی\n"
        "🧠 فیلسوف | 📚 معلم | ⚡ سرسخت | 🎭 شاعرانه | 💕 دوستانه",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def set_personality(update: Update, context: ContextTypes.DEFAULT_TYPE, personality: str):
    context.user_data["personality"] = personality
    context.user_data["system_prompt"] = personalities[personality]["prompt"]
    
    messages = {
        "شاعرانه": "🎭 چه انتخاب زیبایی! حالا با قلم شاعرانه باهات حرف می‌زنم...",
        "دوستانه": "💕 چه خوب! از این به بعد مثل یه دوست قدیمی باهات گرم می‌گیرم...",
        "شوخ‌طبع": "😄 عالیه! با خنده و شوخی پیشت می‌مونم...",
        "صمیمی": "🤗 چه حس خوبی! مثل یه همراه مهربون کنارت هستم...",
        "رسمی": "👔 بسیار خب! با نهایت احترام در خدمتم...",
        "علمی": "🔬 عالی! با دقت و جزئیات علمی جواب می‌دم...",
        "معلم": "📚 چه خوب! با حوصله و قدم به قدم یاد می‌دی...",
        "فیلسوف": "🧠 چه عمیق! با هم به معنی زندگی فکر می‌کنیم...",
        "خشک و زننده": "🗿 باشه... هر طور دوست داری...",
        "سرسخت": "⚡ محکم و قاطع! پس اینجوری پیش میریم..."
    }
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await update.callback_query.edit_message_text(
        f"{messages.get(personality, '✅ شخصیت تغییر کرد!')}\n\nاگه دوست داری باهات طراحی کنم یا عکس بسازم، از منو «🎨 طراحی و عکس» رو انتخاب کن.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def chat_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    personality = context.user_data.get("personality", "رسمی")
    await update.callback_query.edit_message_text(
        f"💬 **گفتگوی دل‌چسب فعال شد** 💬\n\n"
        f"🍃 دارم با شخصیت **{personality}** {personalities[personality]['emoji']} باهات حرف می‌زنم...\n\n"
        "✍️ هر چی دوست داری بپرس:\n"
        "• سوال ساده → جواب کوتاه و شیرین\n"
        "• سوال عمیق → جواب مفصل و دل‌نشین\n"
        "• «برام یه متن قشنگ بنویس» → یه شاهکار ادبی!\n\n"
        "💫 **حالا بگو چی توی دلت هست...**",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
    )
    context.user_data["chat_mode"] = True
    context.user_data["student_mode"] = False
    context.user_data["design_mode"] = False

async def design_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎨 طراحی متن هنری", callback_data="design_text")],
        [InlineKeyboardButton("🖼️ ساخت عکس با هوش مصنوعی", callback_data="design_image")],
        [InlineKeyboardButton("📝 کاور پست اینستاگرام", callback_data="design_cover")],
        [InlineKeyboardButton("💌 متن عاشقانه و شاعرانه", callback_data="design_poem")],
        [InlineKeyboardButton("🎭 لوگو و برندینگ", callback_data="design_logo")],
        [InlineKeyboardButton("📊 نمودار و اینفوگرافیک", callback_data="design_chart")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back")],
    ]
    await update.callback_query.edit_message_text(
        "🎨 **آتلیه طراحی هوشمند** 🎨\n\n"
        "✨ اینجا می‌تونم برات:\n"
        "• متن‌های هنری و زیبا طراحی کنم\n"
        "• عکس و تصویر بسازم\n"
        "• کاور پست آماده کنم\n"
        "• شعر و متن عاشقانه بگم\n"
        "• لوگو و برند بسازم\n\n"
        "🗣️ **بگو چه چیزی می‌خوای؟**\n"
        "(مثل: «برام یه عکس از غروب دریا بساز» یا «یه متن قشنگ برای پست اینستا بنویس»)",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    context.user_data["design_mode"] = True
    context.user_data["chat_mode"] = False

async def student_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(
        "📚 **مدرسه هوشمند** 📚\n\n"
        "🍃 اینجا می‌تونم بهت درس بدم و ازت امتحان بگیرم...\n\n"
        "🎯 **موضوع مورد نظرت رو بگو:**\n"
        "• برنامه‌نویسی پایتون\n"
        "• تاریخ و تمدن\n"
        "• ریاضی و فیزیک\n"
        "• ارز دیجیتال و بلاکچین\n"
        "• زبان انگلیسی\n"
        "• هر چی دوست داری...\n\n"
        "✍️ **بنویس تا درس رو شروع کنیم...**",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
    )
    context.user_data["student_mode"] = True
    context.user_data["chat_mode"] = False
    context.user_data["design_mode"] = False
    context.user_data["waiting_for_topic"] = True

# ========== تشخیص هوشمند طول پاسخ و سبک دل‌چسب ==========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_id = str(update.effective_user.id)
    
    # حالت طراحی
    if context.user_data.get("design_mode", False):
        await handle_design_request(update, context, user_message)
        return
    
    # حالت دانشجویی
    if context.user_data.get("student_mode", False):
        if context.user_data.get("waiting_for_topic", False):
            context.user_data["topic"] = user_message
            context.user_data["waiting_for_topic"] = False
            await update.message.reply_text(f"📖 **آماده‌سازی درس درباره {user_message}**... 📖\n\n🍃 کمی صبر کن...")
            await teach_topic(update, context, user_message)
        else:
            answer = user_message.strip().upper()
            correct = context.user_data.get("correct_answer", "")
            if answer == correct:
                score = context.user_data.get("score", 0) + 1
                context.user_data["score"] = score
                await update.message.reply_text(f"✅ **آفرین!** 🎉\n\nنمره: {score}/5\n\n🔥 عالی بود! ادامه بده...")
                await ask_next_question(update, context)
            else:
                await update.message.reply_text(f"❌ **نزدیک بودی!**\n\nپاسخ صحیح: {correct}\n\nنمره فعلی: {context.user_data.get('score', 0)}/5\n\n💪 دفعه بعد حتماً می‌زنیش!")
                await ask_next_question(update, context)
        return
    
    # حالت عادی
    if not context.user_data.get("chat_mode", False):
        await update.message.reply_text(
            "🍃 **اول منو رو انتخاب کن...**\n\n"
            "از دکمه‌های زیر استفاده کن یا /start بزن.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رفتن به منو", callback_data="back")]])
        )
        return
    
    personality = context.user_data.get("personality", "رسمی")
    system_prompt = context.user_data.get("system_prompt", "تو یک دستیار هستی.")
    
    memory = load_memory()
    user_history = memory.get(user_id, [])
    
    chat_history = ""
    for item in user_history[-5:]:
        chat_history += f"کاربر: {item['user']}\nAI: {item['ai']}\n"
    
    # تشخیص هوشمند
    msg_lower = user_message.lower()
    
    deep_words = ["توضیح بده", "تحلیل کن", "چرا", "چطور", "مفصل", "کامل", "راهنمایی کن", "یاد بده", "معنی", "تاریخچه", "مقایسه"]
    short_words = ["سلام", "خوبی", "چطوری", "اوکی", "باشه", "مرسی", "ممنون", "بله", "نه", "خدافظ"]
    creative_words = ["بنویس", "شعر", "متن قشنگ", "دلنوشته", "عاشقانه", "جمله زیبا", "کپشن"]
    
    is_deep = any(word in msg_lower for word in deep_words) or len(user_message.split()) > 10
    is_short = any(word in msg_lower for word in short_words) and len(user_message.split()) < 4
    is_creative = any(word in msg_lower for word in creative_words)
    
    if is_short:
        length_instruction = "پاسخ بسیار کوتاه و دل‌نشین بده. حداکثر ۱ خط. گرم و صمیمی باش."
        max_tokens = 100
    elif is_creative:
        length_instruction = "یه متن زیبا، شاعرانه و دل‌نشین بنویس. احساسی باش. کلمات قشنگ و تصاویر ذهنی خلق کن. حداقل ۵ خط."
        max_tokens = 800
    elif is_deep:
        length_instruction = "پاسخ مفصل، کامل و آموزنده بده. با مثال و جزئیات. حداقل ۵ خط. طوری که دل‌آرا و جذاب باشه."
        max_tokens = 1200
    else:
        length_instruction = "پاسخ معمولی و متوسط بده. حدود ۲ تا ۳ خط. روان و دل‌چسب باش."
        max_tokens = 500
    
    current_time = datetime.now().strftime("%H:%M")
    full_prompt = f"""{system_prompt}
شخصیت تو: {personality}
سبک نوشتاری: دل‌چسب، گرم، صمیمی و روان. طوری که قلب کاربر رو لمس کنه.

{length_instruction}

تاریخچه گفتگو:
{chat_history}

ساعت الان {current_time} است.
سوال کاربر: "{user_message}"

پاسخ بده (بدون تکرار اسم شخصیت. فقط متن پاسخ):"""
    
    await update.message.reply_chat_action("typing")
    
    if not GROQ_API_KEY:
        await update.message.reply_text("⚠️ کلید API تنظیم نشده.")
        return
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": full_prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.8
                }
            )
            
            if response.status_code == 200:
                ai_response = response.json()["choices"][0]["message"]["content"]
                
                user_history.append({"user": user_message[:100], "ai": ai_response[:200]})
                if len(user_history) > 20:
                    user_history = user_history[-20:]
                memory[user_id] = user_history
                save_memory(memory)
                
                await update.message.reply_text(ai_response, parse_mode="Markdown")
            else:
                await update.message.reply_text("🍃 **نتونستم جواب بدم...**\n\nلطفاً دوباره تلاش کن. 🥀")
    except Exception as e:
        await update.message.reply_text(f"🍃 **خطایی پیش اومد...**\n\n{str(e)[:100]}\n\nلطفاً دوباره تلاش کن. 💫")

# ========== هندلر طراحی ==========
async def handle_design_request(update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str):
    await update.message.reply_chat_action("typing")
    
    prompt_lower = prompt.lower()
    
    # تشخیص نوع درخواست
    if any(word in prompt_lower for word in ["عکس", "تصویر", "نقاشی", "ساخت", "بکش"]):
        # ساخت عکس (با API رایگان placeholder)
        image_prompt = prompt.replace("عکس", "").replace("بکش", "").replace("ساخت", "").strip()
        if not image_prompt:
            image_prompt = "beautiful sunset landscape"
        
        await update.message.reply_text(
            f"🎨 **دارم برات نقاشی می‌کشم...** 🎨\n\n"
            f"🍃 موضوع: {prompt}\n\n"
            "✨ یه کمی صبر کن... اثر هنریت داره ساخته میشه...",
            parse_mode="Markdown"
        )
        
        # استفاده از متن زیبا به جای عکس واقعی (برای رایگان بودن)
        art_text = f"""
╔══════════════════════════╗
║     🎨 اثر هنری تو 🎨     ║
╠══════════════════════════╣
║                          ║
║   {prompt[:30]}   ║
║                          ║
║     ✨     ✨     ✨      ║
║    🎨    💫    🖌️        ║
║                          ║
║   "خالق این اثر: تو"     ║
║                          ║
╚══════════════════════════╝

🍃 این نقاشی ذهنی منه از درخواست تو...

💫 برای ساخت عکس واقعی، می‌تونی از ربات‌های زیر استفاده کنی:
• @dreamshaper_bot
• @schemabot
• @stablediffusion_bot
"""
        await update.message.reply_text(art_text, parse_mode="Markdown")
        
    elif any(word in prompt_lower for word in ["متن", "کپشن", "بنویس", "شعر", "دلنوشته"]):
        # ساخت متن ادبی با Groq
        await update.message.reply_text("📝 **دارم یه متن قشنگ برات می‌نویسم...** 📝\n\n✍️ کمی صبر کن...")
        
        creative_prompt = f"""یه متن زیبا، دل‌نشین و احساسی درباره "{prompt}" بنویس.
سبک: شاعرانه و روان. از کلمات قشنگ و تصاویر ذهنی استفاده کن.
طول: حدود ۸ تا ۱۲ خط.
متن رو زیبا و دل‌آرا بنویس طوری که قلب رو لمس کنه."""
        
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [{"role": "user", "content": creative_prompt}],
                        "max_tokens": 800,
                        "temperature": 0.9
                    }
                )
                if response.status_code == 200:
                    ai_text = response.json()["choices"][0]["message"]["content"]
                    await update.message.reply_text(f"✨ **متن زیبای تو** ✨\n\n{ai_text}\n\n🍃 تقدیم به تو...", parse_mode="Markdown")
                else:
                    await fallback_creative_response(update, prompt)
        except:
            await fallback_creative_response(update, prompt)
    
    else:
        # پاسخ خلاقانه عمومی
        await fallback_creative_response(update, prompt)
    
    context.user_data["design_mode"] = False

async def fallback_creative_response(update: Update, prompt: str):
    responses = [
        f"🎨 **ایده قشنگی داری!** 🎨\n\nمن برای «{prompt[:50]}» این رو می‌تونم پیشنهاد کنم:\n\n"
        f"✨ یه طرح مینیمال با رنگ‌های گرم و آرام‌بخش\n"
        f"🖌️ با خطاطی زیبا و نرم\n"
        f"💫 که آرامش رو به بیننده منتقل کنه\n\n"
        f"🍃 اگه دوست داری، می‌تونیم با هم جزئیاتش رو طراحی کنیم!",
        
        f"💡 **چه ایده‌ی جذابی!** 💡\n\n"
        f"برای «{prompt[:50]}» پیشنهاد من:\n"
        f"• استفاده از رنگ‌های طبیعی و خاکی\n"
        f"• ترکیب نقاشی با تایپوگرافی\n"
        f"• ایجاد حس عمق و حرکت\n\n"
        f"✨ دوست داری با این ایده جلو بریم؟"
    ]
    await update.message.reply_text(random.choice(responses), parse_mode="Markdown")

# ========== توابع دانشجویی ==========
async def teach_topic(update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str):
    prompt = f"""درباره "{topic}" یک درس شیرین و دل‌چسب بنویس (حداقل ۱۲ خط):
1. مقدمه‌ای جذاب (قلب رو لمس کنه)
2. مفاهیم اصلی با مثال‌های قشنگ
3. نکات طلایی و کاربردی
4. جمع‌بندی دل‌نشین

سبک: روان، صمیمی و آموزنده. طوری که یادگیری لذت‌بخش بشه."""
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 2000,
                    "temperature": 0.8
                }
            )
            
            if response.status_code == 200:
                lesson = response.json()["choices"][0]["message"]["content"]
                await update.message.reply_text(f"📚 **درس {topic}** 📚\n\n{lesson}\n\n🍃 چقدر خوب بود... حالا بریم سراغ یه تست جذاب!", parse_mode="Markdown")
                await ask_quiz_question(update, context, topic)
            else:
                await update.message.reply_text("🍃 نتونستم درس رو آماده کنم... لطفاً دوباره تلاش کن.")
                context.user_data["student_mode"] = False
    except Exception as e:
        await update.message.reply_text(f"🍃 خطا: {str(e)[:100]}")
        context.user_data["student_mode"] = False

async def ask_quiz_question(update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str):
    prompt = f"""درباره "{topic}" یه سوال چهارگزینه‌ای جذاب و چالش‌برانگیز طراحی کن.

فرمت دقیق:
❓ سوال: [متن سوال]
A) [گزینه اول]
B) [گزینه دوم]
C) [گزینه سوم]
D) [گزینه چهارم]
✅ پاسخ: [حرف]

فقط همین فرمت رو برگردون. هیچ چیز اضافه نده."""
    
    try:
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
                    if line.startswith("✅ پاسخ:"):
                        correct = line.replace("✅ پاسخ:", "").strip()
                        break
                
                context.user_data["correct_answer"] = correct
                context.user_data["score"] = 0
                context.user_data["question_count"] = 0
                
                await update.message.reply_text(f"📝 **تست چهارگزینه‌ای** 📝\n\n{quiz}\n\n🔤 پاسختو با حرف A, B, C یا D بفرست:")
            else:
                await update.message.reply_text("🍃 نتونستم سوال بسازم... لطفاً دوباره تلاش کن.")
                context.user_data["student_mode"] = False
    except Exception as e:
        await update.message.reply_text(f"🍃 خطا: {str(e)[:100]}")
        context.user_data["student_mode"] = False

async def ask_next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = context.user_data.get("question_count", 0) + 1
    context.user_data["question_count"] = count
    
    if count >= 5:
        score = context.user_data.get("score", 0)
        grade = "🔥 عالی! تو واقعاً فوق‌العاده‌ای!" if score >= 4 else "📚 خوب بود! یه کم دیگه تلاش کن تا عالی بشی!"
        await update.message.reply_text(
            f"🎉 **پایان آزمون!** 🎉\n\n"
            f"📊 نمره نهایی: {score} از 5 ({score*20}%)\n\n"
            f"{grade}\n\n"
            f"🍃 برای شروع درس جدید، دوباره «حالت دانشجویی» رو انتخاب کن.\n\n"
            f"✨ همیشه بهت افتخار می‌کنم!",
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
        text = "📜 **حافظه خالی** 🍃\n\nهنوز هیچ گفتگویی نکردی...\nاول یه سوال بپرس تا خاطره‌ها ساخته بشن. 💫"
    else:
        text = "📜 **خاطره‌های ما** 📜\n\n🍃 این چیزاییه که باهم گفتیم:\n\n"
        for i, item in enumerate(history[-8:], 1):
            text += f"{i}. تو: {item['user'][:45]}\n   💬 من: {item['ai'][:45]}\n\n"
        text += f"\n✨ {len(history)} تا گفتگوی قشنگ باهم داشتیم... دوست داری ادامه بدیم؟"
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def clear_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    memory = load_memory()
    if user_id in memory:
        del memory[user_id]
        save_memory(memory)
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await update.callback_query.edit_message_text(
        "🍃 **حافظه پاک شد...** 🍃\n\n"
        "خاطره‌های قبلی رفتن، اما می‌تونیم خاطره‌های جدید و قشنگ‌تری بسازیم.\n\n"
        "✨ حالا از اول شروع می‌کنیم...",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
❓ **راهنمای مهربون** ❓

🎭 **شخصیت‌ها:**
از منوی شخصیت می‌تونی لحن و سبک من رو عوض کنی.
(شاعرانه، دوستانه، علمی و...)

💬 **گفتگو:**
هر چی دوست داری بپرس. من با سبک دل‌چسب جواب می‌دم.
• سوال ساده → جواب کوتاه
• سوال عمیق → جواب مفصل
• «برام یه متن قشنگ بنویس» → شاهکار ادبی!

🎨 **طراحی و عکس:**
می‌تونی ازم بخوای برات:
• متن هنری و کپشن آماده کنم
• ایده طراحی بدم
• شعر و دلنوشته بگم

📚 **حالت دانشجویی:**
یه موضوع رو انتخاب کن، برات درس می‌دم و بعد امتحان می‌گیرم.

📜 **حافظه:**
من چیزایی که گفتی رو یادم میاد. همیشه خاطره‌های قشنگ رو نگه می‌دارم.

---
🍃 **یادت باشه...** من اینجام تا کنارت باشم. هر وقت حرف دلت رو بزنی، گوش می‌دم. 💫
"""
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "back":
        context.user_data["chat_mode"] = False
        context.user_data["student_mode"] = False
        context.user_data["design_mode"] = False
        context.user_data["waiting_for_topic"] = False
        await start(update, context)
    elif data == "personality":
        await personality_menu(update, context)
    elif data == "chat":
        await chat_menu(update, context)
    elif data == "design":
        await design_menu(update, context)
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
    elif data in ["design_text", "design_image", "design_cover", "design_poem", "design_logo", "design_chart"]:
        context.user_data["design_mode"] = True
        await update.callback_query.edit_message_text(
            "🎨 **آماده طراحی** 🎨\n\n"
            "حالا دقیقاً بگو چه چیزی می‌خوای:\n"
            "• مثلاً: «برام یه متن عاشقانه بنویس»\n"
            "• یا: «عکس غروب دریا»\n"
            "• یا: «کاور پست برای روز تولد»\n\n"
            "✍️ منتظرم...",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="design")]])
        )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 ربات دل‌چسب با قابلیت طراحی روشن شد...")
    app.run_polling()

if __name__ == "__main__":
    main()
