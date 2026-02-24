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
    # إعداد Gemini
    genai.configure(api_key=GEMINI_API_KEY)
    ai_model = genai.GenerativeModel('gemini-2.0-flash-exp')
    logger.info("Using Gemini AI")
elif AI_PROVIDER.lower() == 'groq':
    # إعداد Groq
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
    """الحصول على رد من Gemini أو Groq"""
    
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
            # استخدام Gemini
            response = ai_model.generate_content(prompt)
            return response.text
        
        elif AI_PROVIDER.lower() == 'groq':
            # استخدام Groq
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
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
    """إرسال رسالة الترحيب عند إرسال /start"""
    
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

# دالة المنتجات
async def products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض المنتجات المتوفرة"""
    
    keyboard = [
        [InlineKeyboardButton("📱 أجهزة آيفون", callback_data='iphones')],
        [InlineKeyboardButton("🤖 أجهزة أندرويد", callback_data='android')],
        [InlineKeyboardButton("🎧 إكسسوارات", callback_data='accessories')],
        [InlineKeyboardButton("🔌 شواحن وكوابل", callback_data='chargers')],
        [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    products_message = """
📱 منتجاتنا المتميزة:

اختر الفئة التي تهمك:
"""
    
    if update.message:
        await update.message.reply_text(products_message, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(products_message, reply_markup=reply_markup)

# دالة الخدمات
async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض الخدمات المتوفرة"""
    
    keyboard = [
        [InlineKeyboardButton("🔧 الصيانة", callback_data='maintenance')],
        [InlineKeyboardButton("📲 استبدال الشاشات", callback_data='screen_replacement')],
        [InlineKeyboardButton("🔍 الفحص الشامل", callback_data='full_check')],
        [InlineKeyboardButton("💯 الضمان", callback_data='warranty')],
        [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    services_message = """
✨ خدماتنا المميزة:

نقدم لك أفضل الخدمات لجهازك:
"""
    
    if update.message:
        await update.message.reply_text(services_message, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(services_message, reply_markup=reply_markup)

# دالة الموقع والتواصل
async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض معلومات الموقع والتواصل"""
    
    keyboard = [
        [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    location_message = """
📍 موقعنا ومعلومات التواصل:

📍 العنوان: [يرجى إضافة العنوان الفعلي هنا]

📞 رقم التواصل: [رقم الهاتف]

⏰ أوقات العمل:
   من السبت إلى الخميس
   من 10 صباحاً حتى 10 مساءً
   
🚗 كيفية الوصول:
   [تفاصيل الوصول إلى المحل]

📱 يمكنك أيضاً التواصل معنا عبر هذا البوت في أي وقت!
"""
    
    if update.message:
        await update.message.reply_text(location_message, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(location_message, reply_markup=reply_markup)

# دالة معلومات عن المحل
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض معلومات عن المحل"""
    
    keyboard = [
        [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data='main_menu')]
    ]
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
   ✅ صيانة فورية
   ✅ فحص شامل قبل البيع

🎯 رسالتنا:
   تقديم أفضل تجربة شراء للعملاء مع ضمان الجودة والسعر المناسب

🌟 رؤيتنا:
   أن نكون الخيار الأول لكل من يبحث عن الآيفون والإكسسوارات الأصلية
"""
    
    if update.message:
        await update.message.reply_text(about_message, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(about_message, reply_markup=reply_markup)

# دالة الاستفسار
async def inquiry_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء محادثة الاستفسار"""
    
    inquiry_message = """
💬 مرحباً! أنا مساعدك الذكي في محل أحمد الصعيدي

يمكنك سؤالي عن:
• أسعار الأجهزة
• مواصفات معينة
• توفر منتج
• خدمات الصيانة
• أي استفسار آخر

اكتب سؤالك الآن وسأجيبك فوراً! 😊

لإلغاء الاستفسار، اكتب /cancel
"""
    
    await update.message.reply_text(inquiry_message)
    return WAITING_FOR_QUESTION

# دالة معالجة الأسئلة
async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة أسئلة المستخدم باستخدام AI"""
    
    user_question = update.message.text
    
    # إرسال رسالة انتظار
    waiting_msg = await update.message.reply_text("⏳ جاري البحث عن إجابة لسؤالك...")
    
    try:
        # الحصول على رد من AI
        answer = get_ai_response(user_question)
        
        if answer:
            # حذف رسالة الانتظار
            await waiting_msg.delete()
            
            # إرسال الإجابة
            await update.message.reply_text(answer)
            
            # عرض خيارات المتابعة
            keyboard = [
                [KeyboardButton("💬 استفسار آخر"), KeyboardButton("📱 المنتجات")],
                [KeyboardButton("📍 الموقع والتواصل"), KeyboardButton("🔙 القائمة الرئيسية")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            await update.message.reply_text(
                "هل تريد المساعدة في شيء آخر؟ 😊",
                reply_markup=reply_markup
            )
        else:
            await waiting_msg.delete()
            await update.message.reply_text(
                "❌ عذراً، حدث خطأ أثناء معالجة سؤالك. يرجى المحاولة مرة أخرى أو التواصل معنا مباشرة."
            )
        
    except Exception as e:
        logger.error(f"Error handling question: {e}")
        await waiting_msg.delete()
        await update.message.reply_text(
            "❌ عذراً، حدث خطأ أثناء معالجة سؤالك. يرجى المحاولة مرة أخرى أو التواصل معنا مباشرة."
        )
    
    return ConversationHandler.END

# دالة إلغاء الاستفسار
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إلغاء محادثة الاستفسار"""
    await update.message.reply_text(
        "تم إلغاء الاستفسار. يمكنك العودة للقائمة الرئيسية. 👍"
    )
    return ConversationHandler.END

# معالج الأزرار الداخلية
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الأزرار الداخلية"""
    
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
🌟 آيفون 16 Pro
🌟 آيفون 16 Plus
🌟 آيفون 16
🌟 آيفون 15 Pro Max
🌟 آيفون 15 Pro
🌟 آيفون 15 Plus
🌟 آيفون 15
🌟 آيفون 14 Pro Max
🌟 وجميع الإصدارات السابقة

✨ جميع الأجهزة:
• مفحوصة بالكامل
• بضمان موثوق
• أسعار منافسة
• إمكانية التقسيط

💬 للاستفسار عن الأسعار والتوفر، اضغط "استفسار"
"""
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data='products')]]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == 'android':
        message = """
🤖 أجهزة الأندرويد المتوفرة:

📱 Samsung Galaxy Series:
   • S24 Ultra
   • S24+
   • S24
   • A Series

📱 Xiaomi:
   • Redmi Note Series
   • Poco Series
   • Mi Series

📱 OPPO & Realme
📱 OnePlus
📱 وماركات عالمية أخرى

✨ جميع الأجهزة بضمان وبأسعار مميزة

💬 للاستفسار عن الأسعار والتوفر، اضغط "استفسار"
"""
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data='products')]]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == 'accessories':
        message = """
🎧 إكسسوارات الموبايل:

🎧 سماعات:
   • AirPods Pro
   • AirPods (2nd & 3rd Gen)
   • سماعات لاسلكية متنوعة

⌚ ساعات ذكية:
   • Apple Watch Series 9
   • Apple Watch SE
   • ساعات سامسونج الذكية

📱 جرابات وحماية:
   • جرابات آيفون أصلية
   • واقيات شاشة زجاجية
   • جرابات مقاومة للصدمات

💼 حقائب وحوامل
🔊 سماعات بلوتوث

✨ جميع المنتجات أصلية 100%

💬 للاستفسار عن الأسعار، اضغط "استفسار"
"""
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data='products')]]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == 'chargers':
        message = """
🔌 شواحن وكوابل:

⚡ شواحن سريعة:
   • شواحن آبل الأصلية
   • شواحن USB-C PD
   • شواحن لاسلكية MagSafe
   • شواحن متعددة المنافذ

🔌 كوابل:
   • كوابل Lightning أصلية
   • كوابل USB-C to Lightning
   • كوابل Type-C
   • بأطوال مختلفة (1م، 2م، 3م)

🔋 بنوك طاقة (Power Banks):
   • سعات مختلفة
   • دعم الشحن السريع
   • ماركات معتمدة

✨ جميع المنتجات أصلية ومعتمدة

💬 للاستفسار عن الأسعار، اضغط "استفسار"
"""
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data='products')]]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == 'maintenance':
        message = """
🔧 خدمات الصيانة:

🛠️ نقدم صيانة احترافية لجميع أنواع الموبايلات:

✅ استبدال الشاشات
✅ إصلاح البطاريات
✅ إصلاح الأزرار
✅ حل مشاكل الشحن
✅ إصلاح السماعات والمايكروفون
✅ حل مشاكل السوفتوير
✅ تنظيف الجهاز من الداخل

⏱️ صيانة فورية في معظم الحالات
💯 ضمان على جميع قطع الغيار

📞 تواصل معنا للحجز
"""
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data='services')]]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == 'screen_replacement':
        message = """
📲 استبدال الشاشات:

✨ خدمة استبدال الشاشات الاحترافية:

📱 نستبدل شاشات:
   • جميع إصدارات الآيفون
   • أجهزة السامسونج
   • جميع أنواع الأندرويد

🌟 مميزات الخدمة:
   ✅ شاشات أصلية عالية الجودة
   ✅ استبدال فوري (30-60 دقيقة)
   ✅ ضمان 3-6 أشهر
   ✅ فحص كامل بعد التركيب
   ✅ أسعار منافسة

⚠️ ننصح بالاستبدال الفوري عند تشقق الشاشة لحماية الجهاز

📞 احجز موعدك الآن!
"""
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data='services')]]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == 'full_check':
        message = """
🔍 خدمة الفحص الشامل:

📋 فحص كامل ودقيق لجهازك:

✅ ما نفحصه:
   • الشاشة والتاتش
   • البطارية وسعتها
   • الكاميرات الأمامية والخلفية
   • السماعات والمايكروفون
   • أزرار الجهاز
   • منافذ الشحن
   • Face ID / Touch ID
   • الواي فاي والبلوتوث
   • GPS والشبكة
   • حالة الجهاز الداخلية

📊 تحصل على:
   • تقرير مفصل عن حالة الجهاز
   • توصيات للإصلاح إن لزم
   • تقييم سعر الجهاز

💰 الخدمة مجانية عند الشراء من عندنا!

⏱️ مدة الفحص: 15-20 دقيقة
"""
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data='services')]]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == 'warranty':
        message = """
💯 سياسة الضمان:

🛡️ نحن نضمن لك:

📱 ضمان الأجهزة:
   • الأجهزة الجديدة: ضمان المصنع الأصلي
   • الأجهزة المستعملة: ضمان 3-6 أشهر
   • تغطية شاملة للعيوب المصنعية

🔧 ضمان الصيانة:
   • 3 أشهر على الشاشات
   • 3 أشهر على البطاريات
   • شهر على باقي قطع الغيار

🎧 ضمان الإكسسوارات:
   • 6 أشهر على السماعات
   • سنة على الشواحن الأصلية
   • 3 أشهر على الجرابات

⚠️ شروط الضمان:
   ✅ عدم كسر الجهاز أو تعريضه للماء
   ✅ عدم فتح الجهاز من مكان آخر
   ✅ إحضار فاتورة الشراء

✨ نحن نثق بجودة منتجاتنا ونضمنها لك!
"""
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data='services')]]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

# معالج الرسائل النصية العادية
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الرسائل النصية من القائمة الرئيسية"""
    
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
        # إذا كان نص حر، استخدم AI للإجابة
        await handle_question(update, context)

# دالة معالجة الأخطاء
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الأخطاء"""
    logger.error(f"Exception while handling an update: {context.error}")

def main():
    """تشغيل البوت"""
    
    # إنشاء التطبيق
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # إضافة معالجات الأوامر
    application.add_handler(CommandHandler("start", start))
    
    # معالج المحادثة للاستفسارات
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^💬 استفسار|💬 استفسار آخر$"), inquiry_start)],
        states={
            WAITING_FOR_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    application.add_handler(conv_handler)
    
    # معالج الأزرار الداخلية
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # معالج الرسائل النصية
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    # معالج الأخطاء
    application.add_error_handler(error_handler)
    
    # تشغيل البوت
    logger.info(f"Bot is starting with {AI_PROVIDER.upper()} AI...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
