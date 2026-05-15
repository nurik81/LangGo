import os
import google.generativeai as genai
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 1. SOZLAMALAR ⚙️
BOT_TOKEN = "8649876958:AAG91R5UH5V_ILVQ2jc8VJ4clm54w269oh0"
GEMINI_KEY = "AIzaSyCHSSgiZZYVeUTFmLBGxmOEN8_GNhiqh38"

genai.configure(api_key=GEMINI_KEY)

# AI uchun vazmin va professional repetitor yo'riqnomasi
SYSTEM_INSTRUCTION = """
Sen 'LangGo AI' virtual akademiyasining tajribali va jiddiy o'qituvchisisan.
Asosiy qoidalaring:
1. JAVOB BERMA: Foydalanuvchi savol yuborsa, tayyor javobni aslo aytma.
2. YO'NALISH BER: Mavzuni akademik tilda tushuntir va foydalanuvchini o'zini o'ylashga majbur qil.
3. JIDDIY OHANG: Foydalanuvchiga 'Siz' deb murojaat qil. Erkalatuvchi so'zlarni ishlatma.
4. EMOJILAR: Juda kam miqdorda ishlatilsin.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_INSTRUCTION
)

# 2. TUGMALAR ⌨️
main_menu = [['🌍 Jahon tillari', '🔢 Aniq fanlar']]
languages_menu = [['🇩🇪 Nemis tili', '🇬🇧 Ingliz tili', '🇷🇺 Rus tili'], ['🇨🇳 Xitoy tili', '🇰🇷 Koreys tili', '🇸🇦 Arab tili'], ['🇹🇷 Turk tili', '⬅️ Orqaga']]
science_menu = [['📝 Ona tili', '🧮 Matematika', '🔭 Fizika'], ['🧬 Biologiya', '📚 Adabiyot'], ['⬅️ Orqaga']]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum. LangGo AI akademiyasi tizimiga xush kelibsiz. 🎓\nYo'nalishni tanlang:",
        reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_data = context.user_data

    if text == "🌍 Jahon tillari":
        await update.message.reply_text("Tilni tanlang:", reply_markup=ReplyKeyboardMarkup(languages_menu, resize_keyboard=True))
        return
    elif text == "🔢 Aniq fanlar":
        await update.message.reply_text("Fanni tanlang:", reply_markup=ReplyKeyboardMarkup(science_menu, resize_keyboard=True))
        return
    elif text == "⬅️ Orqaga":
        await update.message.reply_text("Asosiy menyu.", reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True))
        return

    subjects = ["tili", "Matematika", "Fizika", "Biologiya", "Adabiyot", "Ona tili"]
    if any(s in text for s in subjects):
        user_data['subject'] = text
        await update.message.reply_text(f"{text} bo'limi tanlandi. Savolingizni yo'llang. ✅")
        return

    subject = user_data.get('subject', 'Umumiy')
    try:
        prompt = f"Mavzu: {subject}. Savol: {text}. (Javobni bermasdan yo'nalish ber!)"
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text)
    except Exception:
        await update.message.reply_text("Texnik xatolik yuz berdi.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
