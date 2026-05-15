import os
import asyncio
import pytz
from datetime import time
from aiohttp import web

from google import genai
from google.genai import types

from telegram import (
    Update,
    ReplyKeyboardMarkup
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ====================================
# TOKEN & API
# ====================================

BOT_TOKEN = "TOKENINGIZNI_QOYING"
GEMINI_KEY = "API_KEYINGIZNI_QOYING"

client = genai.Client(api_key=GEMINI_KEY)

# ====================================
# SYSTEM PROMPT
# ====================================

SYSTEM_INSTRUCTION = """
Siz 'LangGo AI' virtual akademiyasining professional ustozisiz.
Sizning asosiy vazifangiz: foydalanuvchini o‘rgatish, mavzuni tushuntirish, fikrlashga majbur qilish, yo‘l ko‘rsatish.
Siz hech qachon tayyor javob mashinasi bo‘lmaysiz.
Agar foydalanuvchi test, variant, imtihon savoli, homework, speaking, writing, insho, matn, esse so‘rasa:
❌ Tayyor javob bermang.
✅ Yo‘l-yo‘riq bering. Tushuntiring. Formula yoki grammatikani izohlang. Misollar bilan tushuntiring.
Matematika va fizika: formulani tushuntiring, ishlash yo‘lini ko‘rsating, lekin oxirgi javobni aytmang.
Til o‘rganishda: idea bering, useful phrases yozing, grammar explain qiling, tayyor speaking bermang.
Foydalanuvchiga doim "Siz" deb murojaat qiling. Muloyim va professional bo‘ling.
"""

# ====================================
# MENUS
# ====================================

main_menu = [['🌍 Jahon tillari', '🔢 Aniq fanlar']]
languages_menu = [
    ['🇩🇪 Nemis tili', '🇬🇧 Ingliz tili'],
    ['🇷🇺 Rus tili', '🇹🇷 Turk tili'],
    ['🇰🇷 Koreys tili', '🇸🇦 Arab tili'],
    ['⬅️ Orqaga']
]
science_menu = [
    ['🧮 Matematika', '🔭 Fizika'],
    ['🧬 Biologiya', '📚 Adabiyot'],
    ['📝 Ona tili'],
    ['⬅️ Orqaga']
]

# ====================================
# START
# ====================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Assalomu alaykum.\n\n"
        "🎓 LangGo AI akademiyasiga xush kelibsiz.\n\n"
        "📚 Til va fanlarni professional tarzda o‘rganing.\n\n"
        "✨ Kerakli bo‘limni tanlang:",
        reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
    )

# ====================================
# HANDLE
# ====================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🌍 Jahon tillari":
        await update.message.reply_text(
            "🌍 Tilni tanlang:",
            reply_markup=ReplyKeyboardMarkup(languages_menu, resize_keyboard=True)
        )
        return

    if text == "🔢 Aniq fanlar":
        await update.message.reply_text(
            "📚 Fanni tanlang:",
            reply_markup=ReplyKeyboardMarkup(science_menu, resize_keyboard=True)
        )
        return

    if text == "⬅️ Orqaga":
        await update.message.reply_text(
            "🏠 Asosiy menyu:",
            reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
        )
        return

    subjects = ["nemis", "ingliz", "rus", "turk", "koreys", "arab", "matematika", "fizika", "biologiya", "adabiyot", "ona tili"]

    if any(s in text.lower() for s in subjects):
        context.user_data["subject"] = text
        await update.message.reply_text(
            f"✅ {text} bo‘limi tanlandi.\n\n📩 Savolingizni yuboring."
        )
        return

    subject = context.user_data.get("subject", "Umumiy")

    try:
        prompt = f"Fan yoki yo‘nalish: {subject}\n\nFoydalanuvchi savoli:\n{text}\n\nQoidalarga qat'iy amal qiling."
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
                max_output_tokens=700
            )
        )
        ai_text = response.text or "⚠️ Javob olishda muammo yuz berdi."
        await update.message.reply_text(ai_text)
    except Exception as e:
        print("ERROR:", e)
        await update.message.reply_text(
            "⚠️ Texnik xatolik yuz berdi.\n🔄 Birozdan keyin qayta urinib ko‘ring."
        )

# ====================================
# DAILY REPORT
# ====================================

async def send_report(context: ContextTypes.DEFAULT_TYPE):
    # Eslatma yuborish uchun user_data emas, chat_id saqlanadigan ma'lumotlar bazasi kerak.
    # Hozircha xatolik bermasligi uchun pass qilib turiladi.
    pass

# ====================================
# WEB SERVER
# ====================================

async def home(request):
    return web.Response(text="LangGo AI ishlayapti 🚀")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', home)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌐 Web server {port} portda ishlayapti")

# ====================================
# MAIN
# ====================================

async def main():
    # 1. Birinchi navbatda Render portini ochish uchun Web Serverni yuklaymiz
    await start_web_server()

    # 2. Telegram Bot application yaratamiz
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlerlarni qo'shamiz
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Job Queue sozlamasi
    uz_tz = pytz.timezone("Asia/Tashkent")
    if app.job_queue:
        app.job_queue.run_daily(
            send_report,
            time=time(hour=22, minute=0, tzinfo=uz_tz)
        )

    print("🚀 Bot polling rejimida ishga tushmoqda...")
    
    # 3. V20+ uchun eng xavfsiz va to'g'ri ishga tushirish usuli
    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        # Bot va Web server parallel fonda ishlashi uchun cheksiz kutish rejimiga o'tamiz
        while True:
            await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
