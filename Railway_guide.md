# 🚂 دليل النشر على Railway

## ✨ لماذا Railway؟
- **سهل جداً** في الاستخدام
- **مجاني** ($5 رصيد شهري)
- **سريع** في التنصيب
- **موثوق** وما بيوقف

---

## 📋 الخطوات بالتفصيل:

### 1️⃣ إنشاء حساب Railway

1. **اذهب إلى**: https://railway.app
2. **اضغط**: "Start a New Project" أو "Sign Up"
3. **سجل** بحساب GitHub (الأسهل والأفضل)

---

### 2️⃣ رفع الكود على GitHub (طريقة سهلة)

#### الطريقة الأولى: رفع عن طريق GitHub Desktop

1. **حمل GitHub Desktop**: https://desktop.github.com
2. **سجل دخول** بحسابك
3. **اضغط**: File → Add Local Repository
4. **اختر** مجلد البوت
5. **اكتب** Commit Message: "Initial commit"
6. **اضغط**: "Publish repository"
7. **خلي** Repository "Private" (مهم!)
8. **اضغط**: Publish

#### الطريقة الثانية: رفع عن طريق Git (للمحترفين)

```bash
# في مجلد البوت، شغل الأوامر دي:

# 1. إنشاء git repository
git init

# 2. إضافة جميع الملفات
git add .

# 3. عمل commit
git commit -m "Initial commit"

# 4. إنشاء repository على GitHub
# اذهب لـ https://github.com/new
# سمّيه: telegram-bot-ahmed
# خليه Private
# ما تضيفش README

# 5. ربط المجلد بـ GitHub (غير username)
git remote add origin https://github.com/username/telegram-bot-ahmed.git

# 6. رفع الكود
git branch -M main
git push -u origin main
```

---

### 3️⃣ إنشاء مشروع على Railway

1. **ادخل على**: https://railway.app
2. **اضغط**: "New Project"
3. **اختر**: "Deploy from GitHub repo"
4. **اختر**: Repository البوت
5. **انتظر** حتى يتم الربط

---

### 4️⃣ إضافة المتغيرات البيئية (Environment Variables)

هذي أهم خطوة! 🔑

1. **اضغط** على المشروع اللي انعمل
2. **اضغط** على تبويب "Variables"
3. **أضف** المتغيرات دي واحدة واحدة:

```
TELEGRAM_TOKEN=توكن_البوت_من_BotFather
AI_PROVIDER=gemini
GEMINI_API_KEY=مفتاح_Gemini_من_Google
GROQ_API_KEY=مفتاح_Groq (اختياري)
```

**مثال:**
```
Variable Name: TELEGRAM_TOKEN
Value: 7234567890:AAHfB3xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

Variable Name: AI_PROVIDER
Value: gemini

Variable Name: GEMINI_API_KEY
Value: AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

4. **اضغط** "Add" بعد كل متغير

---

### 5️⃣ Deploy البوت

Railway هيعمل Deploy تلقائياً! 🎉

1. **شوف** تبويب "Deployments"
2. **انتظر** حتى يظهر ✅ "Success"
3. **اضغط** على "View Logs" عشان تشوف البوت شغال

**لو شفت في Logs**: `Bot is starting with GEMINI AI...`
يبقى البوت **شغال**! 🚀

---

### 6️⃣ اختبار البوت

1. **افتح تليجرام**
2. **ابحث** عن البوت (الـ username اللي عملته)
3. **اضغط**: `/start`
4. **جرب** الأزرار والأسئلة

---

## 🔧 التعديلات والتحديثات

### لو عايز تعدل على الكود:

#### طريقة 1: عن طريق GitHub Desktop
1. **عدّل** الملفات على جهازك
2. **افتح** GitHub Desktop
3. **اكتب** وصف التعديل
4. **اضغط**: "Commit to main"
5. **اضغط**: "Push origin"
6. **Railway** هيعمل Deploy تلقائياً!

#### طريقة 2: عن طريق Git
```bash
# بعد التعديل:
git add .
git commit -m "وصف التعديل"
git push
```

### لو عايز تعدل المتغيرات:
1. **ادخل** على Railway
2. **اضغط** على المشروع
3. **اذهب** لـ "Variables"
4. **عدّل** المتغير اللي تريده
5. **Railway** هيعيد تشغيل البوت تلقائياً

---

## 📊 مراقبة البوت

### شوف Logs:
1. **ادخل** Railway
2. **اضغط** على المشروع
3. **اختر** تبويب "Deployments"
4. **اضغط** "View Logs"

### شوف الاستخدام:
- **اذهب** لتبويب "Metrics"
- **شوف** استهلاك الـ RAM والـ CPU

---

## 🆘 حل المشاكل الشائعة

### مشكلة: البوت مش شغال

**الحل:**
1. شوف Logs في Railway
2. تأكد من المتغيرات صح
3. تأكد من التوكنات سليمة

### مشكلة: Deploy Failed

**الحل:**
1. تأكد من ملف `requirements.txt` موجود
2. تأكد من ملف `Procfile` موجود
3. شوف رسالة الخطأ في Logs

### مشكلة: البوت بيتوقف بعد شوية

**الحل:**
- تأكد إن عندك رصيد كافي في Railway
- الرصيد المجاني: $5 شهرياً (كافي لبوت بسيط)

### مشكلة: خطأ في Gemini API

**الحل:**
1. تأكد من المفتاح صحيح
2. جرب تعمل مفتاح جديد
3. أو غيّر لـ Groq:
   ```
   AI_PROVIDER=groq
   ```

---

## 💰 التكاليف

### الخطة المجانية:
- **$5** رصيد شهري
- **500 ساعة** تشغيل (كافية جداً)
- **100 GB** bandwidth

### نصيحة:
- البوت البسيط ما بياخد رصيد كثير
- لو خلص الرصيد، ممكن تدفع $5 شهرياً فقط

---

## 🎯 نصائح مهمة

### 1. الأمان:
- **خلي** Repository على GitHub **Private**
- **ما ترفعش** ملف `.env` لـ GitHub
- **استخدم** `.gitignore`

### 2. الأداء:
- **Gemini**: أفضل للردود الذكية
- **Groq**: أسرع للردود الفورية

### 3. المراقبة:
- **شوف** Logs بشكل دوري
- **راقب** استهلاك الرصيد

---

## ✅ Checklist - قبل Deploy

- [ ] عملت Repository على GitHub
- [ ] رفعت الكود
- [ ] عملت مشروع على Railway
- [ ] ربطت GitHub بـ Railway
- [ ] أضفت TELEGRAM_TOKEN
- [ ] أضفت AI_PROVIDER
- [ ] أضفت GEMINI_API_KEY أو GROQ_API_KEY
- [ ] Deploy نجح ✅
- [ ] اختبرت البوت في تليجرام

---

## 🎉 مبروك!

البوت شغال الآن 24/7 على Railway!

لو احتجت مساعدة، شوف الـ Logs في Railway أولاً.

بالتوفيق لأحمد الصعيدي! 💪🚀
