import os
import json
import logging
import random
import httpx
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MEMORY_FILE = "memory.json"
DESIGNS_FILE = "designs.json"

def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def load_designs():
    try:
        with open(DESIGNS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_designs(designs):
    with open(DESIGNS_FILE, "w") as f:
        json.dump(designs, f, indent=2)

personalities = {
    "رسمی": {"emoji": "👔", "prompt": "تو یک دستیار رسمی و حرفه‌ای هستی.", "color": "🔵"},
    "شوخ‌طبع": {"emoji": "😄", "prompt": "تو یک دستیار شوخ و بامزه هستی.", "color": "🟡"},
    "خشک و زننده": {"emoji": "🗿", "prompt": "تو یک دستیار خشک و بی‌احساس هستی.", "color": "⚪"},
    "علمی": {"emoji": "🔬", "prompt": "تو یک دانشمند و محقق هستی.", "color": "🧪"},
    "صمیمی": {"emoji": "🤗", "prompt": "تو یک دوست صمیمی و مهربان هستی.", "color": "💕"},
    "فیلسوف": {"emoji": "🧠", "prompt": "تو یک فیلسوف عمیق هستی.", "color": "📚"},
    "معلم": {"emoji": "📚", "prompt": "تو یک معلم صبور هستی.", "color": "✏️"},
    "سرسخت": {"emoji": "⚡", "prompt": "تو یک فرد سرسخت و قاطع هستی.", "color": "🔥"},
    "شاعرانه": {"emoji": "🎭", "prompt": "تو یک شاعر و نویسنده هستی. کلمات زیبا و دل‌نشین.", "color": "🌸"},
    "دوستانه": {"emoji": "💕", "prompt": "تو یک دوست مهربان و گرم هستی.", "color": "🌟"},
    "مدیتیشن": {"emoji": "🧘", "prompt": "تو یک مرشد آرامش‌بخش هستی. کلماتت آرام و عمیق.", "color": "🌙"},
    "انرژی‌بخش": {"emoji": "⚡", "prompt": "تو یک کوچ انگیزشی هستی. پر از انرژی و امید.", "color": "☀️"}
}

# ASCII Art های زیبا
ascii_arts = {
    "flower": """
    🌸
   🌸🌸
  🌸🌸🌸
 🌸🌸🌸🌸
🌸🌸🌸🌸🌸
    """,
    "heart": """
    ❤️💛💚💙💜
   ❤️💛💚💙💜
  ❤️💛💚💙💜
    """,
    "star": """
     ⭐
    ⭐⭐
   ⭐⭐⭐
  ⭐⭐⭐⭐
 ⭐⭐⭐⭐⭐
    """,
    "moon": """
     🌙
    🌙🌙
   🌙🌙🌙
  🌙🌙🌙🌙
    """,
    "butterfly": """
     🦋
    🦋🦋
   🦋🦋🦋
  🦋🦋🦋🦋
    """
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    personality = context.user_data.get("personality", "رسمی")
    keyboard = [
        [InlineKeyboardButton("🎭 شخصیت‌ها", callback_data="personality")],
        [InlineKeyboardButton("💬 گفتگو", callback_data="chat")],
        [InlineKeyboardButton("🎨 طراحی", callback_data="design")],
        [InlineKeyboardButton("📚 دانشجویی", callback_data="student")],
        [InlineKeyboardButton("🧘 مدیتیشن", callback_data="meditation")],
        [InlineKeyboardButton("💎 ایده‌پرداز", callback_data="ideas")],
        [InlineKeyboardButton("📜 تاریخچه", callback_data="history")],
        [InlineKeyboardButton("🗑 پاک کردن", callback_data="clear_memory")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
    ]
    
    welcome_art = random.choice(list(ascii_arts.values()))
    
    welcome_text = f"""
{random.choice(['✨', '🌟', '💫', '⭐', '🌙'])} **به ربات هوشمند کریپتو خوش آمدی** {random.choice(['✨', '🌟', '💫', '⭐', '🌙'])}

`{welcome_art}`

🍃 **اینجا جاییه که هوش مصنوعی با قلب باهات حرف می‌زنه...**
🎨 می‌تونه برات **طراحی کنه** و **عکس بسازه**
💬 با **سبک نوشتاری دل‌چسب** پاسخ می‌ده
🧘 می‌تونه **آرامشت** بده
💎 **ایده‌های ناب** برات بسازه

---
💫 **شخصیت فعلی:** {personality} {personalities[personality]['emoji']} {personalities[personality]['color']}
⚡ **آماده‌ای تا یه تجربه متفاوت داشته باشیم؟**
---

📌 **از منوی زیر انتخاب کن:** 👇
"""
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def personality_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for name, data in personalities.items():
        keyboard.append([InlineKeyboardButton(f"{data['emoji']} {data['color']} {name}", callback_data=f"set_personality_{name}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    
    current = context.user_data.get("personality", "رسمی")
    await update.callback_query.edit_message_text(
        f"🎭 **گالری شخصیت‌ها** 🎭\n\n"
        f"⭐ شخصیت فعلی: **{current}** {personalities[current]['emoji']} {personalities[current]['color']}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "👔 رسمی | 😄 شوخ | 🗿 خشک | 🔬 علمی\n"
        "🤗 صمیمی | 🧠 فیلسوف | 📚 معلم | ⚡ سرسخت\n"
        "🎭 شاعرانه | 💕 دوستانه | 🧘 مدیتیشن | ☀️ انرژی‌بخش\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🌸 **هر کدوم رو دوست داری انتخاب کن...**",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def set_personality(update: Update, context: ContextTypes.DEFAULT_TYPE, personality: str):
    context.user_data["personality"] = personality
    context.user_data["system_prompt"] = personalities[personality]["prompt"]
    
    messages = {
        "مدیتیشن": "🧘 **آرامش انتخاب کردی...**\n\nاز این به بعد مثل نسیم صبحگاهی آرامت می‌کنم...",
        "انرژی‌بخش": "⚡ **انرژی گرفتی!** ☀️\n\nپر از امید و انگیزه باهات حرف می‌زنم...",
        "شاعرانه": "🎭 **چه انتخاب نابی!** 🌸\n\nبا قلم شاعرانه و کلمات آهنگین باهات حرف می‌زنم...",
        "دوستانه": "💕 **چه گرم!** 🤗\n\nمثل یه دوست قدیمی همیشه کنارت هستم...",
        "شوخ‌طبع": "😄 **چه حال خوبی!** 🎉\n\nبا خنده و انرژی مثبت پیشت می‌مونم...",
        "صمیمی": "🤗 **چه حس قشنگی!** 💫\n\nمثل یه همراه مهربون همیشه باهات گرم می‌گیرم...",
        "علمی": "🔬 **چه دقیق!** 📊\n\nبا جزئیات و دانش عمیق جواب می‌دم...",
        "فیلسوف": "🧠 **چه عمیق!** 📚\n\nباهمدیگه به معنی زندگی فکر می‌کنیم...",
        "معلم": "📚 **چه صبورانه!** ✏️\n\nقدم به قدم با حوصله یاد می‌دی...",
        "رسمی": "👔 **بسیار خب!** 📋\n\nبا نهایت احترام در خدمتم...",
        "خشک و زننده": "🗿 **باشه...** 🤐\n\nهمونطور که دوست داری...",
        "سرسخت": "⚡ **محکم و قاطع!** 🔥\n\nاین جوری پیش میریم..."
    }
    
    art = random.choice(list(ascii_arts.values()))
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
    
    await update.callback_query.edit_message_text(
        f"{messages.get(personality, '✅ شخصیت تغییر کرد!')}\n\n"
        f"`{art}`\n\n"
        f"✨ **حالا از منوی اصلی می‌تونی:**\n"
        f"• با من گفتگو کنی 💬\n"
        f"• طراحی بکشی 🎨\n"
        f"• مدیتیشن کنی 🧘\n"
        f"• ایده بگیری 💎\n\n"
        f"🌸 **منتظرتم...**",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def chat_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    personality = context.user_data.get("personality", "رسمی")
    await update.callback_query.edit_message_text(
        f"💬 **گفتگوی دل‌چسب فعال شد** 💬\n\n"
        f"{personalities[personality]['color']} دارم با شخصیت **{personality}** {personalities[personality]['emoji']} باهات حرف می‌زنم...\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "✍️ **چطوری می‌تونم بهت کمک کنم؟**\n\n"
        "• سوال ساده → جواب کوتاه و شیرین\n"
        "• سوال عمیق → جواب مفصل و دل‌نشین\n"
        "• «برام یه متن قشنگ بنویس» → شاهکار ادبی!\n"
        "• «حالم خوب نیست» → آرامشت می‌دم\n"
        "• «یه انرژی بده بهم» → انگیزه می‌گیری\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{random.choice(['🌸', '💫', '✨', '🌟', '🍃'])} **حالا بگو چی توی دلت هست...**",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
    )
    context.user_data["chat_mode"] = True
    context.user_data["student_mode"] = False
    context.user_data["design_mode"] = False
    context.user_data["meditation_mode"] = False
    context.user_data["ideas_mode"] = False

async def design_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎨 متن هنری", callback_data="design_text")],
        [InlineKeyboardButton("🖼️ ASCII Art", callback_data="design_ascii")],
        [InlineKeyboardButton("📝 شعر و دلنوشته", callback_data="design_poem")],
        [InlineKeyboardButton("🎵 متن موزون", callback_data="design_rhythm")],
        [InlineKeyboardButton("💌 کاور پست", callback_data="design_cover")],
        [InlineKeyboardButton("🎭 لوگو و برند", callback_data="design_logo")],
        [InlineKeyboardButton("📊 اینفوگرافیک", callback_data="design_chart")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back")],
    ]
    await update.callback_query.edit_message_text(
        "🎨 **آتلیه طراحی هوشمند** 🎨\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "✨ **اینجا می‌تونم برات:**\n\n"
        "• **متن هنری** → کلمات قشنگ و پراحساس\n"
        "• **ASCII Art** → نقاشی با کاراکترها\n"
        "• **شعر و دلنوشته** → قافیه‌های زیبا\n"
        "• **متن موزون** → ریتم و آهنگ در کلمات\n"
        "• **کاور پست** → برای اینستاگرام\n"
        "• **لوگو و برند** → هویت بصری\n"
        "• **اینفوگرافیک** → نمودارهای متنی\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🗣️ **بگو چی می‌خوای:**\n"
        "مثال: «برام یه شعر عاشقانه بگو»\n"
        "مثال: «یه نقاشی با ستاره بکش»\n"
        "مثال: «کاور پست برای روز مادر»\n\n"
        "🍃 **منتظرم تا بگی...**",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    context.user_data["design_mode"] = True
    context.user_data["chat_mode"] = False

async def meditation_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(
        "🧘 **مدیتیشن و آرامش** 🧘\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🌙 **اینجا می‌تونم آرامت کنم:**\n\n"
        "• «یه مدیتیشن کوتاه بگو»\n"
        "• «برام یه جمله آرامش‌بخش بگو»\n"
        "• «حالم خوب نیست»\n"
        "• «دلم گرفته»\n"
        "• «انرژی بده بهم»\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"`{ascii_arts['moon']}`\n\n"
        "🍃 **نفس عمیق بکش... آرام باش... من اینجام...**\n\n"
        "حالا هر چی دلت می‌خواد بگو...",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
    )
    context.user_data["meditation_mode"] = True
    context.user_data["chat_mode"] = False
    context.user_data["design_mode"] = False

async def ideas_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(
        "💎 **ایده‌پرداز خلاق** 💎\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "✨ **اینجا می‌تونم برات ایده بسازم:**\n\n"
        "• «ایده برای شروع بیزینس»\n"
        "• «ایده برای تولید محتوا»\n"
        "• «ایده برای یه استارتاپ»\n"
        "• «ایده برای یه کتاب»\n"
        "• «ایده برای یه اختراع»\n"
        "• «هر ایده دیگه‌ای که دوست داری»\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎯 **بگو توی چه زمینه‌ای ایده می‌خوای...**\n"
        "من برات چندتا ایده ناب و خلاقانه می‌سازم.\n\n"
        "🌟 **منتظرم...**",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
    )
    context.user_data["ideas_mode"] = True
    context.user_data["chat_mode"] = False
    context.user_data["design_mode"] = False
    context.user_data["meditation_mode"] = False

async def student_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(
        "📚 **مدرسه هوشمند** 📚\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🍃 **اینجا می‌تونم بهت یاد بدم:**\n\n"
        "• برنامه‌نویسی (Python, JavaScript, ...)\n"
        "• طراحی گرافیک\n"
        "• زبان انگلیسی\n"
        "• ریاضی و فیزیک\n"
        "• تاریخ و تمدن\n"
        "• ارز دیجیتال و بلاکچین\n"
        "• هر موضوع دیگه‌ای که دوست داری\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎯 **موضوع مورد نظرت رو بگو...**\n"
        "برات یه درس شیرین و مفصل می‌دم و بعدش امتحان می‌گیرم.\n\n"
        "✍️ **بنویس...**",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]])
    )
    context.user_data["student_mode"] = True
    context.user_data["chat_mode"] = False
    context.user_data["design_mode"] = False
    context.user_data["meditation_mode"] = False
    context.user_data["ideas_mode"] = False
    context.user_data["waiting_for_topic"] = True

# ========== پردازش اصلی پیام‌ها ==========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_id = str(update.effective_user.id)
    
    # حالت مدیتیشن
    if context.user_data.get("meditation_mode", False):
        await handle_meditation(update, context, user_message)
        return
    
    # حالت ایده‌پرداز
    if context.user_data.get("ideas_mode", False):
        await handle_ideas(update, context, user_message)
        return
    
    # حالت طراحی
    if context.user_data.get("design_mode", False):
        await handle_design(update, context, user_message)
        return
    
    # حالت دانشجویی
    if context.user_data.get("student_mode", False):
        await handle_student(update, context, user_message)
        return
    
    # حالت عادی
    if not context.user_data.get("chat_mode", False):
        await update.message.reply_text(
            "🍃 **اول منو رو انتخاب کن...**\n\n"
            "از دکمه‌های زیر استفاده کن یا /start بزن.\n\n"
            f"`{random.choice(list(ascii_arts.values()))}`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رفتن به منو", callback_data="back")]])
        )
        return
    
    await handle_normal_chat(update, context, user_message)

async def handle_meditation(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str):
    await update.message.reply_chat_action("typing")
    
    msg_lower = message.lower()
    
    if any(word in msg_lower for word in ["نفس", "آرامش", "مدیتیشن"]):
        prompt = """یه متن آرامش‌بخش و مدیتیشنی بنویس. کوتاه و عمیق. مثل یک مرشد آرامش. از کلماتی مثل آرامش، صلح، سکوت، بودن در لحظه استفاده کن. حداکثر ۵ خط."""
    elif any(word in msg_lower for word in ["گرفته", "ناراحت", "خوب نیست", "بد"]):
        prompt = """یه متن دلداری و آرامش‌بخش بنویس برای کسی که حالش خوب نیست. پر از امید و آرامش. بگو که همه چیز درست میشه. از کلماتی مثل "من اینجام"، "اشکالی نداره"، "خواهد گذشت" استفاده کن. حداکثر ۶ خط."""
    else:
        prompt = f"""یه جمله یا متن آرامش‌بخش و عمیق درباره "{message}" بنویس. طوری که آرامش بده و انرژی مثبت. حداکثر ۴ خط."""
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 300,
                    "temperature": 0.8
                }
            )
            if response.status_code == 200:
                ai_response = response.json()["choices"][0]["message"]["content"]
                await update.message.reply_text(
                    f"🧘 **آرامش...** 🧘\n\n{ai_response}\n\n`{ascii_arts['moon']}`\n\n🍃 **نفس عمیق... لبخند بزن... همه چیز خوبه...**",
                    parse_mode="Markdown"
                )
            else:
                await fallback_meditation(update, message)
    except:
        await fallback_meditation(update, message)
    
    context.user_data["meditation_mode"] = False

async def fallback_meditation(update: Update, message: str):
    responses = [
        f"🧘 **آرامش درون...**\n\nهمین حالا که هستی، همینه که باید باشه.\nنفس عمیق... رها کن...\nهمه چیز در مسیر درسته.\n🍃",
        f"🌙 **آرامش...**\n\n{message}\n\nگاهی سکوت بهترین جوابه.\nبه خودت گوش کن.\n🌸",
        f"💫 **تو قوی‌تر از اونی که فکر می‌کنی...**\n\nاین لحظه هم می‌گذرد، مثل همه لحظه‌های دیگه.\nفقط نفس بکش...\n✨"
    ]
    await update.message.reply_text(random.choice(responses), parse_mode="Markdown")

async def handle_ideas(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str):
    await update.message.reply_chat_action("typing")
    
    prompt = f"""برای موضوع "{message}"، ۳ ایده خلاقانه، ناب و اجرایی بده.
هر ایده رو در ۲ خط توضیح بده.
ایده‌ها باید عملی و جذاب باشن.
فرمت: 
1. [نام ایده]
   [توضیح کوتاه]
2. ..."""
    
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 800,
                    "temperature": 0.9
                }
            )
            if response.status_code == 200:
                ai_response = response.json()["choices"][0]["message"]["content"]
                await update.message.reply_text(
                    f"💎 **ایده‌های ناب برای:** {message}\n\n{ai_response}\n\n✨ **کدوم یکی رو می‌خوای شروع کنی؟**",
                    parse_mode="Markdown"
                )
            else:
                await fallback_ideas(update, message)
    except:
        await fallback_ideas(update, message)
    
    context.user_data["ideas_mode"] = False

async def fallback_ideas(update: Update, message: str):
    await update.message.reply_text(
        f"💎 **ایده‌های جذاب برای {message}** 💎\n\n"
        f"1. **ایده طلایی** ✨\n"
        f"   یه راه خلاقانه که می‌تونه بازار رو متحول کنه...\n\n"
        f"2. **ایده ناب** 🌟\n"
        f"   ساده اما قدرتمند. با کمترین هزینه میشه شروع کرد.\n\n"
        f"3. **ایده خلاقانه** 🎨\n"
        f"   یه نگاه جدید به موضوع که کمتر کسی بهش فکر کرده.\n\n"
        f"🌸 دوست داری درباره یکی از اینا بیشتر بگم؟",
        parse_mode="Markdown"
    )

async def handle_design(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str):
    await update.message.reply_chat_action("typing")
    
    msg_lower = message.lower()
    
    if any(word in msg_lower for word in ["شعر", "دلنوشته", "عاشقانه"]):
        await create_poem(update, message)
    elif any(word in msg_lower for word in ["ascii", "نقاشی", "کاراکتر"]):
        await create_ascii_art(update, message)
    elif any(word in msg_lower for word in ["کاور", "پست", "اینستاگرام"]):
        await create_cover(update, message)
    elif any(word in msg_lower for word in ["موزون", "آهنگ", "ریتم"]):
        await create_rhythm_text(update, message)
    else:
        await create_general_art(update, message)
    
    context.user_data["design_mode"] = False

async def create_poem(update: Update, topic: str):
    prompt = f"""یه شعر زیبا و دل‌نشین درباره "{topic}" بنویس.
شعر باید قافیه داشته باشه و روان باشه.
حداقل ۸ بیت.
از کلمات قشنگ و احساسی استفاده کن."""
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1000,
                    "temperature": 0.9
                }
            )
            if response.status_code == 200:
                poem = response.json()["choices"][0]["message"]["content"]
                await update.message.reply_text(
                    f"🎭 **شعر زیبا** 🎭\n\n{poem}\n\n`{ascii_arts['flower']}`\n🌸 تقدیم به تو...",
                    parse_mode="Markdown"
                )
            else:
                await fallback_poem(update, topic)
    except:
        await fallback_poem(update, topic)

async def fallback_poem(update: Update, topic: str):
    poems = [
        f"🎭 **دلنوشته** 🎭\n\nدر دل شب، در خلوت خود\n{random.choice(['🌸', '💫', '✨'])} تو را خواندم با چشم تر\nهمه جا سکوت، اما دلم پر از توست\nمثل باران که می‌بارد، آرام و نرم...\n\n🍃 تقدیم به تو",
        f"💕 **عاشقانه** 💕\n\n{random.choice(['🌙', '⭐', '🌟'])} در آسمان دلم، تو را دیدم\nمثل یک ستاره درخشان و زیبا\nهمه شب‌ها به یاد تو بیدارم\nبمان در قلبم، مثل همیشه...\n\n🌸 برای تو"
    ]
    await update.message.reply_text(random.choice(poems), parse_mode="Markdown")

async def create_ascii_art(update: Update, topic: str):
    art = random.choice(list(ascii_arts.values()))
    await update.message.reply_text(
        f"🎨 **نقاشی با کاراکترها** 🎨\n\n"
        f"موضوع: {topic}\n\n"
        f"`{art}`\n\n"
        f"✨ این یه اثر هنری ساده بود... دوست داری یه طرح دیگه بکشم؟",
        parse_mode="Markdown"
    )

async def create_cover(update: Update, topic: str):
    await update.message.reply_text(
        f"📝 **کاور پست برای:** {topic} 📝\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"**✨ {topic.upper()} ✨**\n\n"
        f"{random.choice(['🌸', '💫', '⭐', '🌟'])} *یه تجربه جدید*\n"
        f"{random.choice(['🍃', '💕', '🎭', '📚'])} *با ما همراه شو*\n\n"
        f"#{topic.replace(' ', '_')}_\n#crypto_art\n#ناب\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎨 این کاور رو می‌تونی برای پستت استفاده کنی!",
        parse_mode="Markdown"
    )

async def create_rhythm_text(update: Update, topic: str):
    prompt = f"""یه متن موزون و آهنگین درباره "{topic}" بنویس.
کلماتت قافیه داشته باشن و ریتمیک باشن.
مثل یه ترانه یا رپ زیبا.
حداقل ۸ خط."""
    
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 800,
                    "temperature": 0.9
                }
            )
            if response.status_code == 200:
                rhythm_text = response.json()["choices"][0]["message"]["content"]
                await update.message.reply_text(
                    f"🎵 **متن موزون** 🎵\n\n{rhythm_text}\n\n🎶 با ریتم بخون...",
                    parse_mode="Markdown"
                )
            else:
                await fallback_rhythm(update, topic)
    except:
        await fallback_rhythm(update, topic)

async def fallback_rhythm(update: Update, topic: str):
    await update.message.reply_text(
        f"🎵 **ریتم و آهنگ** 🎵\n\n"
        f"بیا باهم برقصیم تو این شب بلند\n{random.choice(['⭐', '🌟', '✨'])} بزنیم یه راه تازه، یه مسیر خوش‌بخت\nدل ما پر از امیده، پر از نور و صدا\n{random.choice(['🌸', '🍃', '💫'])} بیا که زندگی یعنی همینمون تنها...\n\n🎶 تقدیم به تو",
        parse_mode="Markdown"
    )

async def create_general_art(update: Update, topic: str):
    prompt = f"""یه متن خلاقانه و هنری درباره "{topic}" بنویس.
سبک: شاعرانه و زیبا. از کلمات قشنگ استفاده کن.
حداقل ۶ خط."""
    
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 800,
                    "temperature": 0.9
                }
            )
            if response.status_code == 200:
                art_text = response.json()["choices"][0]["message"]["content"]
                await update.message.reply_text(
                    f"🎨 **اثر هنری** 🎨\n\n{art_text}\n\n`{ascii_arts['star']}`\n✨ تقدیم به تو...",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    f"🎨 **خلاقیت** 🎨\n\n"
                    f"برای «{topic}» این رو برات ساخته‌ام:\n\n"
                    f"یه {random.choice(['نقاشی ذهنی', 'طرح زیبا', 'ایده ناب'])} با رنگ‌های {random.choice(['گرم', 'آرام', 'شاد'])}...\n\n"
                    f"🍃 دوست داری یه چیز دیگه برات بسازم؟",
                    parse_mode="Markdown"
                )
    except:
        await update.message.reply_text(
            f"🎨 **ایده هنری** 🎨\n\n"
            f"برای «{topic}» پیشنهاد من:\n"
            f"یه ترکیب زیبا از {random.choice(['رنگ‌های پاستیلی', 'خطوط نرم', 'فرم‌های ارگانیک'])}...\n\n"
            f"🌸 دوست داری با هم جزئیاتش رو طراحی کنیم؟",
            parse_mode="Markdown"
        )

async def handle_student(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str):
    if context.user_data.get("waiting_for_topic", False):
        context.user_data["topic"] = message
        context.user_data["waiting_for_topic"] = False
        await update.message.reply_text(
            f"📖 **آماده‌سازی درس درباره {message}**... 📖\n\n"
            f"`{ascii_arts['star']}`\n\n"
            f"🍃 کمی صبر کن... دارم بهترین درس رو برات آماده می‌کنم...",
            parse_mode="Markdown"
        )
        await teach_topic(update, context, message)
    else:
        answer = message.strip().upper()
        correct = context.user_data.get("correct_answer", "")
        if answer == correct:
            score = context.user_data.get("score", 0) + 1
            context.user_data["score"] = score
            await update.message.reply_text(
                f"✅ **آفرین!** 🎉\n\n"
                f"نمره: {score}/5\n\n"
                f"{random.choice(['🔥 عالی بود!', '💪 به راهت ادامه بده!', '✨ فوق‌العاده‌ای!', '🌟 خیلی خوب!'])}",
                parse_mode="Markdown"
            )
            await ask_next_question(update, context)
        else:
            await update.message.reply_text(
                f"❌ **نزدیک بودی!**\n\n"
                f"پاسخ صحیح: **{correct}**\n\n"
                f"نمره فعلی: {context.user_data.get('score', 0)}/5\n\n"
                f"💪 **دفعه بعد حتماً می‌زنیش!**",
                parse_mode="Markdown"
            )
            await ask_next_question(update, context)

async def handle_normal_chat(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str):
    personality = context.user_data.get("personality", "رسمی")
    system_prompt = context.user_data.get("system_prompt", "تو یک دستیار هستی.")
    
    memory = load_memory()
    user_id = str(update.effective_user.id)
    user_history = memory.get(user_id, [])
    
    chat_history = ""
    for item in user_history[-5:]:
        chat_history += f"کاربر: {item['user']}\nAI: {item['ai']}\n"
    
    msg_lower = message.lower()
    
    # تشخیص نوع پاسخ
    deep_words = ["توضیح بده", "تحلیل", "چرا", "چطور", "مفصل", "کامل", "راهنمایی"]
    short_words = ["سلام", "خوبی", "چطوری", "مرسی", "ممنون", "بله", "نه"]
    creative_words = ["بنویس", "شعر", "متن قشنگ", "دلنوشته", "کپشن"]
    emotional_words = ["حالم خوب نیست", "ناراحتم", "دلم گرفته", "خسته‌ام", "انرژی"]
    
    if any(word in msg_lower for word in emotional_words):
        length_instruction = "یه پاسخ دلداری‌دهنده و آرامش‌بخش بده. پر از امید و انرژی مثبت. بگو که همه چیز درست میشه. ۳-۴ خط."
        max_tokens = 400
    elif any(word in msg_lower for word in creative_words):
        length_instruction = "یه متن زیبا و شاعرانه بنویس. احساسی باش. کلمات قشنگ و دل‌نشین. ۶-۸ خط."
        max_tokens = 800
    elif any(word in msg_lower for word in short_words) and len(message.split()) < 4:
        length_instruction = "پاسخ بسیار کوتاه و دل‌نشین. حداکثر ۱ خط. گرم و صمیمی."
        max_tokens = 80
    elif any(word in msg_lower for word in deep_words) or len(message.split()) > 10:
        length_instruction = "پاسخ مفصل و کامل. با مثال و جزئیات. حداقل ۵ خط. آموزنده و جذاب."
        max_tokens = 1200
    else:
        length_instruction = "پاسخ معمولی و متوسط. ۲-۳ خط. روان و دل‌چسب."
        max_tokens = 500
    
    full_prompt = f"""{system_prompt}
شخصیت تو: {personality}
سبک: {length_instruction}
همیشه با گرمی و صمیمیت پاسخ بده. طوری که کاربر حس کنه با یه دوست قدیمی حرف می‌زنه.

تاریخچه:
{chat_history}

سوال کاربر: "{message}"

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
                
                user_history.append({"user": message[:100], "ai": ai_response[:200]})
                if len(user_history) > 20:
                    user_history = user_history[-20:]
                memory[user_id] = user_history
                save_memory(memory)
                
                await update.message.reply_text(ai_response, parse_mode="Markdown")
            else:
                await update.message.reply_text(
                    f"🍃 **ی کم مشکلات فنی...**\n\n"
                    f"لطفاً دوباره تلاش کن.\n\n`{ascii_arts['heart']}`",
                    parse_mode="Markdown"
                )
    except Exception as e:
        await update.message.reply_text(
            f"🍃 **خطایی پیش اومد...**\n\n{str(e)[:150]}\n\nلطفاً دوباره تلاش کن. 💫",
            parse_mode="Markdown"
        )

async def teach_topic(update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str):
    prompt = f"""درباره "{topic}" یه درس شیرین و دل‌چسب بنویس (حداقل ۱۵ خط):

1. **مقدمه جذاب**: طوری شروع کن که قلب رو لمس کنه
2. **مفاهیم اصلی**: با مثال‌های قشنگ و ساده
3. **نکات طلایی**: کاربردی و مهم
4. **جمع‌بندی دل‌نشین**: با یه انرژی مثبت تموم کن

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
                await update.message.reply_text(
                    f"📚 **درس {topic}** 📚\n\n{lesson}\n\n`{ascii_arts['star']}`\n🍃 چقدر خوب بود... حالا بریم سراغ یه تست جذاب!",
                    parse_mode="Markdown"
                )
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
❓ **سوال:** [متن سوال]
A) [گزینه اول]
B) [گزینه دوم]
C) [گزینه سوم]
D) [گزینه چهارم]
✅ **پاسخ صحیح:** [حرف]

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
                    if "پاسخ صحیح" in line:
                        correct = line.split(":")[-1].strip().replace("**", "").strip()
                        break
                
                context.user_data["correct_answer"] = correct
                context.user_data["score"] = 0
                context.user_data["question_count"] = 0
                
                await update.message.reply_text(
                    f"📝 **تست چهارگزینه‌ای** 📝\n\n{quiz}\n\n"
                    f"🔤 **پاسختو با حرف A, B, C یا D بفرست:**\n\n"
                    f"`{ascii_arts['heart']}`",
                    parse_mode="Markdown"
                )
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
        if score >= 4:
            grade = "🔥 **عالی! تو واقعاً فوق‌العاده‌ای!** 🌟"
            art = ascii_arts['star']
        elif score >= 3:
            grade = "📚 **خوب بود! یه کم دیگه تلاش کن تا عالی بشی!** 💪"
            art = ascii_arts['flower']
        else:
            grade = "🍃 **اشکالی نداره! دفعه بعد حتماً بهتر میشی!** 💫"
            art = ascii_arts['heart']
        
        await update.message.reply_text(
            f"🎉 **پایان آزمون!** 🎉\n\n"
            f"📊 **نمره نهایی:** {score} از 5 ({score*20}%)\n\n"
            f"{grade}\n\n`{art}`\n\n"
            f"🍃 **برای شروع درس جدید، دوباره «حالت دانشجویی» رو انتخاب کن.**\n\n"
            f"✨ **همیشه بهت افتخار می‌کنم!**",
            parse_mode="Markdown"
        )
        context.user_data["student_mode"] = False
        return
    
    topic = context.user_data.get("topic", "")
    await ask_quiz_question(update, context, topic)

async def show_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    memory = load_memory()
    history = memory.get(user_id, [])
    
    if not history:
        text = f"📜 **حافظه خالی** 🍃\n\n`{ascii_arts['butterfly']}`\n\nهنوز هیچ گفتگویی نکردی...\nاول یه سوال بپرس تا خاطره‌ها ساخته بشن. 💫"
    else:
        text = "📜 **خاطره‌های ما** 📜\n\n🍃 این چیزاییه که باهم گفتیم:\n\n"
        for i, item in enumerate(history[-8:], 1):
            text += f"{i}. **تو:** {item['user'][:50]}\n   **💬 من:** {item['ai'][:50]}\n\n"
        text += f"\n✨ **{len(history)} تا گفتگوی قشنگ باهم داشتیم...**\n\n🌸 دوست داری ادامه بدیم؟"
    
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
        f"🍃 **حافظه پاک شد...** 🍃\n\n"
        f"`{ascii_arts['butterfly']}`\n\n"
        f"خاطره‌های قبلی رفتن، اما می‌تونیم خاطره‌های جدید و قشنگ‌تری بسازیم.\n\n"
        f"✨ **حالا از اول شروع می‌کنیم...**\n\n🌸 **منتظرتم...**",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"""
❓ **راهنمای مهربون** ❓

`{ascii_arts['star']}`

━━━━━━━━━━━━━━━━━━━━
🎭 **شخصیت‌ها:**
از منوی شخصیت می‌تونی لحن و سبک من رو عوض کنی.
(شاعرانه، دوستانه، علمی، مدیتیشن و...)

💬 **گفتگو:**
هر چی دوست داری بپرس. من با سبک دل‌چسب جواب می‌دم.

🎨 **طراحی:**
می‌تونی ازم بخوای برات شعر بگم، نقاشی بکشم، کاور پست بسازم.

📚 **دانشجویی:**
یه موضوع رو انتخاب کن، برات درس می‌دم و بعد امتحان می‌گیرم.

🧘 **مدیتیشن:**
وقتی حوصله نداری یا ناراحتی، بیا باهم آرامش پیدا کنیم.

💎 **ایده‌پرداز:**
برای هر چیزی که فکر می‌کنی، برات ایده‌های ناب می‌سازم.

📜 **حافظه:**
من چیزایی که گفتی رو یادم میاد. همیشه خاطره‌های قشنگ رو نگه می‌دارم.
━━━━━━━━━━━━━━━━━━━━

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
        context.user_data["meditation_mode"] = False
        context.user_data["ideas_mode"] = False
        context.user_data["waiting_for_topic"] = False
        await start(update, context)
    elif data == "personality":
        await personality_menu(update, context)
    elif data == "chat":
        await chat_menu(update, context)
    elif data == "design":
        await design_menu(update, context)
    elif data == "meditation":
        await meditation_menu(update, context)
    elif data == "ideas":
        await ideas_menu(update, context)
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
    elif data in ["design_text", "design_ascii", "design_poem", "design_rhythm", "design_cover", "design_logo", "design_chart"]:
        context.user_data["design_mode"] = True
        await update.callback_query.edit_message_text(
            "🎨 **آماده طراحی** 🎨\n\n"
            "حالا دقیقاً بگو چه چیزی می‌خوای:\n"
            "• «برام یه شعر عاشقانه بگو»\n"
            "• «یه نقاشی با ستاره بکش»\n"
            "• «کاور پست برای روز مادر»\n"
            "• «یه متن موزون بگو»\n\n"
            "✍️ **منتظرم...**",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="design")]])
        )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 ربات فوق‌العاده با ۱۲ شخصیت و قابلیت‌های جدید روشن شد...")
    app.run_polling()

if __name__ == "__main__":
    main()
