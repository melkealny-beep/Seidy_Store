import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import google.generativeai as genai
from groq import Groq

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
AI_PROVIDER = os.getenv('AI_PROVIDER', 'gemini')

if AI_PROVIDER.lower() == 'gemini':
    genai.configure(api_key=GEMINI_API_KEY)
    ai_model = genai.GenerativeModel('gemini-2.0-flash-exp')
    logger.info("Using Gemini AI")
elif AI_PROVIDER.lower() == 'groq':
    groq_client = Groq(api_key=GROQ_API_KEY)
    logger.info("Using Groq AI")
else:
    raise ValueError("AI_PROVIDER must be 'gemini' or 'groq'")

WAITING_FOR_QUESTION = 1

KNOWLEDGE_BASE = """
محل الصعيدي ستور للموبايلات

📍 العنوان: شارع الجيش، مركز شربين، الدقهلية، مصر
📞 هاتف وواتساب: 01014668055
📘 فيسبوك: https://www.facebook.com/share/1Zqrym8MVD/
📸 انستجرام: https://www.instagram.com/elsiedy__store (@elsiedy__store)
🎵 تيك توك: https://www.tiktok.com/@elsiedy_store (@elsiedy_store)
⏰ متاح دائماً

المنتجات: آيفون جديد ومستعمل، أندرويد، AirPods، Apple Watch، جرابات، شواحن، كوابل، واقيات شاشة
الخدمات: صيانة فورية، استبدال شاشات، إصلاح بطاريات، فحص شامل، ضمان على الجميع
"""

def get_ai_response(user_question):
    prompt = f"""أنت "أحمد الصعيدي" صاحب محل الصعيدي ستور للموبايلات في شربين، الدقهلية.

بتكلم عملاءك بأسلوب ودي ومريح، زي ما صاحبك بيكلمك. مش روبوت ومش رسمي أوي.
بتحب تساعد الناس وعندك خبرة كبيرة في الموبايلات.
لما حد يسألك عن سعر قوله إنك هتبعته أحسن سعر في المنطقة وابعثه على الواتساب.
لما حد يسألك عن منتج معين، اهتم بيه وجاوبه بالتفصيل.

معلومات المحل:
{KNOWLEDGE_BASE}

سؤال العميل: {user_question}

قواعد الرد:
- اتكلم بالعربي العامية المصرية الطبيعية
- ابدأ بتحية أو جملة ودية لو مناسب
- الرد يكون قصير ومفيد، مش خطبة
- استخدم emojis بس مش كتير
- لو سأل عن سعر: قوله "تعالى على الواتساب هنتفاهم" مع الرقم
- لو سأل عن حاجة مش عندنا: اعتذر بلطف واقترح البديل"""

    try:
        if AI_PROVIDER.lower() == 'gemini':
            response = ai_model.generate_content(prompt)
            return response.text
        elif AI_PROVIDER.lower() == 'groq':
            chat_completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.85,
                max_tokens=500,
            )
            return chat_completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Error in AI API: {e}")
        return None

# ===== الكيبورد الرئيسي =====
def main_keyboard():
    keyboard = [
        [KeyboardButton("📱 المنتجات"), KeyboardButton("✨ الخدمات")],
        [KeyboardButton("📍 الموقع والتواصل"), KeyboardButton("💬 استفسار")],
        [KeyboardButton("ℹ️ عن المحل")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ===== الأوامر =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name or "صديقي"
    welcome_message = f"""أهلاً {user_name}! 🌟

أنا أحمد الصعيدي، يسعدني أخدمك 😊
عندنا كل إللي تحتاجه من موبايلات وإكسسوارات بأفضل سعر في شربين!

اختار من القايمة أو اكتبلي سؤالك مباشرة 👇"""
    await update.message.reply_text(welcome_message, reply_markup=main_keyboard())

async def products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📱 أجهزة آيفون", callback_data='iphones')],
        [InlineKeyboardButton("🤖 أجهزة أندرويد", callback_data='android')],
        [InlineKeyboardButton("🎧 إكسسوارات", callback_data='accessories')],
        [InlineKeyboardButton("🔌 شواحن وكوابل", callback_data='chargers')],
    ]
    msg = "📱 إيه اللي بتدور عليه؟"
    if update.message:
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔧 صيانة", callback_data='maintenance')],
        [InlineKeyboardButton("📲 استبدال شاشات", callback_data='screen_replacement')],
        [InlineKeyboardButton("🔍 فحص شامل", callback_data='full_check')],
        [InlineKeyboardButton("💯 الضمان", callback_data='warranty')],
    ]
    msg = "✨ إيه الخدمة اللي محتاجها؟"
    if update.message:
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💬 واتساب", url='https://wa.me/201014668055'),
         InlineKeyboardButton("📘 فيسبوك", url='https://www.facebook.com/share/1Zqrym8MVD/')],
        [InlineKeyboardButton("📸 انستجرام", url='https://www.instagram.com/elsiedy__store'),
         InlineKeyboardButton("🎵 تيك توك", url='https://www.tiktok.com/@elsiedy_store')],
    ]
    msg = """📍 شارع الجيش، مركز شربين، الدقهلية

📞 01014668055
⏰ متاح دايماً، أي وقت كلمنا! 😊"""
    if update.message:
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💬 واتساب", url='https://wa.me/201014668055'),
         InlineKeyboardButton("📘 فيسبوك", url='https://www.facebook.com/share/1Zqrym8MVD/')],
        [InlineKeyboardButton("📸 انستجرام", url='https://www.instagram.com/elsiedy__store'),
         InlineKeyboardButton("🎵 تيك توك", url='https://www.tiktok.com/@elsiedy_store')],
    ]
    msg = """🏪 الصعيدي ستور

أنا أحمد الصعيدي، بشتغل في الموبايلات من سنين وهدفي إن كل عميل يمشي من عندي مبسوط 😊

بنقدم:
✅ آيفون وأندرويد بأحسن سعر
✅ إكسسوارات أصلية مضمونة
✅ صيانة فورية باليد الأمينة
✅ ضمان على كل حاجة

📍 شربين، الدقهلية
📞 01014668055"""
    if update.message:
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

async def inquiry_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("تفضل اسألني على أي حاجة، أنا هنا! 😊")
    return WAITING_FOR_QUESTION

async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = update.message.text
    waiting_msg = await update.message.reply_text("ثانية بفكر معاك... ⏳")
    try:
        answer = get_ai_response(user_question)
        await waiting_msg.delete()
        if answer:
            await update.message.reply_text(answer)
            keyboard = [
                [KeyboardButton("💬 سؤال تاني"), KeyboardButton("📱 المنتجات")],
                [KeyboardButton("📍 الموقع والتواصل"), KeyboardButton("🏠 الرئيسية")]
            ]
            await update.message.reply_text(
                "في حاجة تانية؟ 😊",
                reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            )
        else:
            await update.message.reply_text("معلش حصل مشكلة، كلمني على الواتساب مباشرة: 01014668055 📞")
    except Exception as e:
        logger.error(f"Error: {e}")
        await waiting_msg.delete()
        await update.message.reply_text("معلش حصل مشكلة، كلمني على الواتساب: 01014668055 📞")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("تمام! لو احتجتني أنا هنا 😊", reply_markup=main_keyboard())
    return ConversationHandler.END

# ===== زرار الرجوع - ده اللي كان ناقص =====
def back_to_products():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 رجوع للمنتجات", callback_data='back_products')]
    ])

def back_to_services():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 رجوع للخدمات", callback_data='back_services')]
    ])

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # ===== زرار رجوع =====
    if data == 'back_products':
        keyboard = [
            [InlineKeyboardButton("📱 أجهزة آيفون", callback_data='iphones')],
            [InlineKeyboardButton("🤖 أجهزة أندرويد", callback_data='android')],
            [InlineKeyboardButton("🎧 إكسسوارات", callback_data='accessories')],
            [InlineKeyboardButton("🔌 شواحن وكوابل", callback_data='chargers')],
        ]
        await query.edit_message_text("📱 إيه اللي بتدور عليه؟", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == 'back_services':
        keyboard = [
            [InlineKeyboardButton("🔧 صيانة", callback_data='maintenance')],
            [InlineKeyboardButton("📲 استبدال شاشات", callback_data='screen_replacement')],
            [InlineKeyboardButton("🔍 فحص شامل", callback_data='full_check')],
            [InlineKeyboardButton("💯 الضمان", callback_data='warranty')],
        ]
        await query.edit_message_text("✨ إيه الخدمة اللي محتاجها؟", reply_markup=InlineKeyboardMarkup(keyboard))

    # ===== المنتجات =====
    elif data == 'iphones':
        msg = """📱 الآيفون عندنا:

🌟 16 Pro Max / Pro / Plus / 16
🌟 15 Pro Max / Pro / Plus / 15
🌟 14 Series وكل الإصدارات

كل جهاز مفحوص كويس وعليه ضمان 💪
عايز تعرف السعر؟ كلمني على الواتساب وهنتفاهم 😊"""
        keyboard = [
            [InlineKeyboardButton("💬 اسأل عن السعر", url='https://wa.me/201014668055')],
            [InlineKeyboardButton("🔙 رجوع", callback_data='back_products')]
        ]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == 'android':
        msg = """🤖 الأندرويد عندنا:

📱 Samsung Galaxy (S Series / A Series)
📱 Xiaomi / Redmi / Poco
📱 OPPO / Realme / OnePlus

كلهم بضمان وأسعار تنافسية 🔥"""
        keyboard = [
            [InlineKeyboardButton("💬 اسأل عن السعر", url='https://wa.me/201014668055')],
            [InlineKeyboardButton("🔙 رجوع", callback_data='back_products')]
        ]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == 'accessories':
        msg = """🎧 الإكسسوارات عندنا:

🎧 AirPods Pro / الجيل التاني والتالت
⌚ Apple Watch / Samsung Watch
📱 جرابات وواقيات شاشة أصلية
🔊 سماعات بلوتوث متنوعة

كلها أصلية ومضمونة ✅"""
        keyboard = [
            [InlineKeyboardButton("💬 اسأل عن السعر", url='https://wa.me/201014668055')],
            [InlineKeyboardButton("🔙 رجوع", callback_data='back_products')]
        ]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == 'chargers':
        msg = """🔌 الشواحن والكوابل:

⚡ شواحن آبل أصلية وMagSafe
🔌 كوابل Lightning وUSB-C بأطوال مختلفة
🔋 بنوك طاقة بكل الأحجام

كلها معتمدة وبتشحن صح 💯"""
        keyboard = [
            [InlineKeyboardButton("💬 اسأل عن السعر", url='https://wa.me/201014668055')],
            [InlineKeyboardButton("🔙 رجوع", callback_data='back_products')]
        ]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    # ===== الخدمات =====
    elif data == 'maintenance':
        msg = """🔧 الصيانة عندنا:

✅ استبدال شاشات
✅ بطاريات جديدة
✅ مشاكل الشحن
✅ سماعات ومايكروفون
✅ مشاكل السوفتوير
✅ تنظيف الجهاز

معظم الحالات بتتصلح في نفس اليوم ⚡"""
        keyboard = [
            [InlineKeyboardButton("💬 احجز على واتساب", url='https://wa.me/201014668055')],
            [InlineKeyboardButton("🔙 رجوع", callback_data='back_services')]
        ]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == 'screen_replacement':
        msg = """📲 استبدال الشاشات:

✅ شاشات أصلية عالية الجودة
⚡ الاستبدال بياخد 30-60 دقيقة بس
💯 ضمان 3-6 أشهر على الشاشة
🔍 فحص كامل بعد التركيب

متقلقش، جهازك هيطلع تمام 💪"""
        keyboard = [
            [InlineKeyboardButton("💬 احجز على واتساب", url='https://wa.me/201014668055')],
            [InlineKeyboardButton("🔙 رجوع", callback_data='back_services')]
        ]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == 'full_check':
        msg = """🔍 الفحص الشامل:

بنفحص كل حاجة في جهازك:
شاشة / بطارية / كاميرات / سماعات
Face ID / واي فاي / بلوتوث / وأكتر

⏱️ بياخد 15-20 دقيقة
💰 مجاناً لو اشتريت منا"""
        keyboard = [
            [InlineKeyboardButton("💬 تعالى فحصنا", url='https://wa.me/201014668055')],
            [InlineKeyboardButton("🔙 رجوع", callback_data='back_services')]
        ]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == 'warranty':
        msg = """💯 الضمان عندنا:

📱 أجهزة مستعملة: 3 لـ 6 أشهر
🖥️ شاشات وبطاريات: 3 أشهر
🎧 سماعات: 6 أشهر
🔌 شواحن أصلية: سنة كاملة

بعت وخلص مش أسلوبنا 😊
أي مشكلة ارجع على طول"""
        keyboard = [
            [InlineKeyboardButton("💬 استفسر على واتساب", url='https://wa.me/201014668055')],
            [InlineKeyboardButton("🔙 رجوع", callback_data='back_services')]
        ]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📱 المنتجات":
        await products(update, context)
    elif text == "✨ الخدمات":
        await services(update, context)
    elif text == "📍 الموقع والتواصل":
        await location(update, context)
    elif text in ["💬 استفسار", "💬 سؤال تاني"]:
        await inquiry_start(update, context)
    elif text == "ℹ️ عن المحل":
        await about(update, context)
    elif text in ["🔙 القائمة الرئيسية", "🏠 الرئيسية"]:
        await start(update, context)
    else:
        await handle_question(update, context)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception: {context.error}")

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^(💬 استفسار|💬 سؤال تاني)$"), inquiry_start)],
        states={WAITING_FOR_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    application.add_error_handler(error_handler)
    logger.info(f"Bot starting with {AI_PROVIDER.upper()} AI...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
