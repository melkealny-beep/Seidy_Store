import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import google.generativeai as genai
from groq import Groq

# إعداد الـ logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# المتغيرات البيئية
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
AI_PROVIDER = os.getenv('AI_PROVIDER', 'gemini')  # gemini أو groq (الافتراضي: gemini)

# إعداد AI حسب الاختيار
if AI_PROVIDER.lower() == 'gemini':
    genai.configure(api_key=GEMINI_API_KEY)
    ai_model = genai.GenerativeModel('gemini-2.0-flash-exp')
    logger.info("Using Gemini AI")
elif AI_PROVIDER.lower() == 'groq':
    groq_client = Groq(api_key=GROQ_API_KEY)
    logger.info("Using Groq AI")
else:
    logger.error("Invalid AI_PROVIDER. Use 'gemini' or 'groq'")
    raise ValueError("AI_PROVIDER must be 'gemini' or 'groq'")

# حالات المحادثة
WAITING_FOR_QUESTION = 1

# تحميل قاعدة المعرفة
def load_knowledge():
    try:
        with open('Knowledge.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return """
محل أحمد الصعيدي للموبايلات واكسسواراتها

🏪 نبذة عن المحل:
محل متخصص في بيع الموبايلات وخاصة الايفونات بجميع أنواعها، بالإضافة إلى جميع الإكسسوارات الأصلية والمضمونة.

📱 منتجاتنا:
- أجهزة آيفون (جديدة ومستعملة نظيفة)
- أجهزة أندرويد بجميع الماركات
- إكسسوارات آيفون أصلية
- شواحن وكوابل معتمدة
- جرابات وواقيات شاشة
- سماعات AirPods
- ساعات آبل ووتش

✨ خدماتنا:
- ضمان على جميع المنتجات
- صيانة فورية
- استبدال الشاشات
- تنظيف الأجهزة
- فحص شامل قبل البيع
- أسعار منافسة

📍 العنوان: [يرجى إضافة العنوان هنا]
📞 رقم التواصل: [يرجى إضافة رقم الهاتف هنا]
⏰ أوقات العمل: من السبت إلى الخميس - من 10 صباحاً إلى 10 مساءً

💯 نضمن لك:
- أسعار مناسبة للجميع
- جودة عالية
- خدمة عملاء ممتازة
- ضمان موثوق
"""

KNOWLEDGE_BASE = load_knowledge()

# دالة للحصول على رد من AI
def get_ai_response(user_question):
    prompt = f"""أنت مساعد ذكي في محل أحمد الصعيدي للموبايلات واكسسواراتها. 
المحل متخصص في بيع الآيفونات وجميع أنواع الموبايلات والإكسسوارات الأصلية.

معلومات المحل:
{KNOWLEDGE_BASE}

سؤال العميل: {user_question}

يرجى الإجابة على السؤال بشكل احترافي ومفيد. إذا كان السؤال خارج نطاق المحل، وجه العميل بلطف.
استخدم الرموز التعبيرية (emojis) بشكل مناسب لجعل الإجابة أكثر جاذبية.
كن ودوداً ومحترفاً في نفس الوقت.
الرد باللغة العربية فقط."""

    try:
        if AI_PROVIDER.lower() == 'gemini':
            response = ai_model.generate_content(prompt)
            return response.text
        elif AI_PROVIDER.lower() == 'groq':
            chat_completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=1000,
            )
            return chat_completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Error in AI API: {e}")
        return None

# دالة البداية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("📱 المنتجات"), KeyboardButton("✨ الخدمات")],
        [KeyboardButton("📍 الموقع والتواصل"), KeyboardButton("💬 استفسار")],
        [KeyboardButton("ℹ️ عن المحل")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_message = """
🌟 أهلاً وسهلاً بك في محل أحمد الصعيدي للموبايلات 🌟

📱 متخصصون في الآيفونات والإكسسوارات الأصلية

يمكنك الاختيار من القائمة أدناه:
• 📱 المنتجات - لمعرفة ما نقدمه
• ✨ الخدمات - خدماتنا المميزة
• 📍 الموقع والتواصل - للوصول إلينا
• 💬 استفسار - اسأل أي سؤال
• ℹ️ عن المحل - معلومات عنا

أو اكتب سؤالك مباشرة وسأساعدك! 😊
"""
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📱 أجهزة آيفون", callback_data='iphones')],
        [InlineKeyboardButton("🤖 أجهزة أندرويد", callback_data='android')],
        [InlineKeyboardButton("🎧 إكسسوارات", callback_data='accessories')],
        [InlineKeyboardButton("🔌 شواحن وكوابل", callback_data='chargers')],
        [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    products_message = "📱 منتجاتنا المتميزة:\n\nاختر الفئة التي تهمك:"
    
    if update.message:
        await update.message.reply_text(products_message, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(products_message, reply_markup=reply_markup)

async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔧 الصيانة", callback_data='maintenance')],
        [InlineKeyboardButton("📲 استبدال الشاشات", callback_data='screen_replacement')],
        [InlineKeyboardButton("🔍 الفحص الشامل", callback_data='full_check')],
        [InlineKeyboardButton("💯 الضمان", callback_data='warranty')],
        [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    services_message = "✨ خدماتنا المميزة:\n\nنقدم لك أفضل الخدمات لجهازك:"
    
    if update.message:
        await update.message.reply_text(services_message, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(services_message, reply_markup=reply_markup)

async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data='main_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    location_message = """
📍 موقعنا ومعلومات التواصل:

📍 العنوان: [يرجى إضافة العنوان الفعلي هنا]
📞 رقم التواصل: [رقم الهاتف]
⏰ أوقات العمل: من السبت إلى الخميس - من 10 صباحاً حتى 10 مساءً
📱 يمكنك أيضاً التواصل معنا عبر هذا البوت في أي وقت!
"""
    if update.message:
        await update.message.reply_text(location_message, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(location_message, reply_markup=reply_markup)

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data='main_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    about_message = """
ℹ️ عن محل أحمد الصعيدي:

🏪 نحن متخصصون في:
   • بيع أجهزة الآيفون بجميع إصداراتها
   • توفير الإكسسوارات الأصلية المعتمدة
   • خدمات الصيانة والدعم الفني
   • ضمان الجودة والسعر المناسب

💪 نقاط قوتنا:
   ✅ خبرة طويلة في السوق
   ✅ أسعار منافسة
   ✅ ضمان على جميع المنتجات
   ✅ خدمة عملاء ممتازة
"""
    if update.message:
        await update.message.reply_text(about_message, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(about_message, reply_markup=reply_markup)

async def inquiry_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    inquiry_message = """
💬 مرحباً! أنا مساعدك الذكي في محل أحمد الصعيدي

اكتب سؤالك الآن وسأجيبك فوراً! 😊
لإلغاء الاستفسار، اكتب /cancel
"""
    await update.message.reply_text(inquiry_message)
    return WAITING_FOR_QUESTION

async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = update.message.text
    waiting_msg = await update.message.reply_text("⏳ جاري البحث عن إجابة لسؤالك...")
    
    try:
        answer = get_ai_response(user_question)
        await waiting_msg.delete()
        
        if answer:
            await update.message.reply_text(answer)
            keyboard = [
                [KeyboardButton("💬 استفسار آخر"), KeyboardButton("📱 المنتجات")],
                [KeyboardButton("📍 الموقع والتواصل"), KeyboardButton("🔙 القائمة الرئيسية")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text("هل تريد المساعدة في شيء آخر؟ 😊", reply_markup=reply_markup)
        else:
            await update.message.reply_text("❌ عذراً، حدث خطأ. يرجى المحاولة مرة أخرى.")
    except Exception as e:
        logger.error(f"Error handling question: {e}")
        await waiting_msg.delete()
        await update.message.reply_text("❌ عذراً، حدث خطأ. يرجى المحاولة مرة أخرى.")
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("تم إلغاء الاستفسار. يمكنك العودة للقائمة الرئيسية. 👍")
    return ConversationHandler.END

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == 'main_menu':
        keyboard = [
            [KeyboardButton("📱 المنتجات"), KeyboardButton("✨ الخدمات")],
            [KeyboardButton("📍 الموقع والتواصل"), KeyboardButton("💬 استفسار")],
            [KeyboardButton("ℹ️ عن المحل")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await query.edit_message_text("اختر من القائمة الرئيسية:")
        await query.message.reply_text("اختر ما تريد:", reply_markup=reply_markup)
    
    elif data == 'iphones':
        message = """
📱 أجهزة الآيفون المتوفرة:

🌟 آيفون 16 Pro Max - أحدث إصدار
🌟 آيفون 16 Pro / 16 Plus / 16
🌟 آيفون 15 Pro Max / 15 Pro / 15
🌟 آيفون 14 Pro Max وجميع الإصدارات السابقة

✨ جميع الأجهزة مفحوصة بضمان موثوق وأسعار منافسة
💬 للاستفسار عن الأسعار، اضغط "استفسار"
"""
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data='products')]]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == 'android':
        message = """
🤖 أجهزة الأندرويد المتوفرة:

📱 Samsung Galaxy S24 Series
📱 Xiaomi / Redmi / Poco
📱 OPPO & Realme
📱 OnePlus وماركات أخرى

✨ جميع الأجهزة بضمان وبأسعار مميزة
"""
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data='products')]]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == 'accessories':
        message = """
🎧 إكسسوارات الموبايل:

🎧 AirPods Pro / AirPods 2nd & 3rd Gen
⌚ Apple Watch / Samsung Watch
📱 جرابات وواقيات شاشة
🔊 سماعات بلوتوث

✨ جميع المنتجات أصلية 100%
"""
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data='products')]]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == 'chargers':
        message = """
🔌 شواحن وكوابل:

⚡ شواحن آبل الأصلية / MagSafe
🔌 كوابل Lightning / USB-C
🔋 بنوك طاقة بسعات مختلفة

✨ جميع المنتجات أصلية ومعتمدة
"""
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data='products')]]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == 'maintenance':
        message = """
🔧 خدمات الصيانة:

✅ استبدال الشاشات
✅ إصلاح البطاريات
✅ حل مشاكل الشحن
✅ إصلاح السماعات والمايكروفون
✅ حل مشاكل السوفتوير
✅ تنظيف الجهاز من الداخل

⏱️ صيانة فورية في معظم الحالات
"""
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data='services')]]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == 'screen_replacement':
        message = """
📲 استبدال الشاشات:

✅ شاشات أصلية عالية الجودة
✅ استبدال فوري (30-60 دقيقة)
✅ ضمان 3-6 أشهر
✅ فحص كامل بعد التركيب
✅ أسعار منافسة

📞 احجز موعدك الآن!
"""
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data='services')]]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == 'full_check':
        message = """
🔍 خدمة الفحص الشامل:

✅ فحص الشاشة والبطارية والكاميرات
✅ فحص السماعات والمايكروفون
✅ فحص Face ID / Touch ID
✅ فحص الواي فاي والبلوتوث

💰 الخدمة مجانية عند الشراء من عندنا!
⏱️ مدة الفحص: 15-20 دقيقة
"""
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data='services')]]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == 'warranty':
        message = """
💯 سياسة الضمان:

📱 الأجهزة الجديدة: ضمان المصنع الأصلي
📱 الأجهزة المستعملة: ضمان 3-6 أشهر
🔧 الشاشات والبطاريات: 3 أشهر
🎧 السماعات: 6 أشهر
🔌 الشواحن الأصلية: سنة

✨ نثق بجودة منتجاتنا ونضمنها لك!
"""
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data='services')]]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "📱 المنتجات":
        await products(update, context)
    elif text == "✨ الخدمات":
        await services(update, context)
    elif text == "📍 الموقع والتواصل":
        await location(update, context)
    elif text == "💬 استفسار" or text == "💬 استفسار آخر":
        await inquiry_start(update, context)
    elif text == "ℹ️ عن المحل":
        await about(update, context)
    elif text == "🔙 القائمة الرئيسية":
        await start(update, context)
    else:
        await handle_question(update, context)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception while handling an update: {context.error}")

def main():
    # إنشاء التطبيق
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^💬 استفسار|💬 استفسار آخر$"), inquiry_start)],
        states={
            WAITING_FOR_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    application.add_error_handler(error_handler)
    
    logger.info(f"Bot is starting with {AI_PROVIDER.upper()} AI...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
