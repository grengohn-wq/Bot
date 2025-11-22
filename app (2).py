# app.py (القسم الأول: التهيئة، الإعدادات، وقواعد البيانات)

import os
import logging
import sqlite3
import json
import uuid 
import asyncio 
import time 
import google.generativeai as genai
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes, 
    ConversationHandler,
    CallbackQueryHandler 
)

print("🚀 بدء تشغيل البوت التعليمي المتكامل...")

# الأساسيات
BASE_DIR = "/home/container"
BOT_TOKEN = "8593626753:AAH56_3qbITygFucwSDc7jeYEIjX0P-eAfU"
GEMINI_API_KEY = "AIzaSyDnui6UUJclEy-Li1zNo9KghJndxeFHe9A"
CONFIG_FILE = f'{BASE_DIR}/البيانات/config.json' 

# إعدادات المدير والإعلانات والبريميوم
ADMIN_PASSWORD = "mosap@123123"
AD_LINK = "https://otieu.com/4/10160934"
AD_RESPONSE_LIMIT = 2 
# معلومات التواصل يتم تحميلها ديناميكياً

# قائمة الدول والمراحل (للشمولية)
ARAB_COUNTRIES = [
    "المملكة العربية السعودية", "مصر", "الإمارات العربية المتحدة", 
    "الكويت", "قطر", "البحرين", "سلطنة عمان", "الأردن", 
    "فلسطين", "سوريا", "لبنان", "العراق", "اليمن", 
    "ليبيا", "تونس", "الجزائر", "المغرب", "السودان", 
    "جيبوتي", "موريتانيا", "الصومال", "جزر القمر"
]
EDUCATION_STAGES = [
    "التعليم الابتدائي (1-6)", 
    "التعليم المتوسط/الإعدادي (7-9)", 
    "التعليم الثانوي/الثالثي (10-12)", 
    "الجامعة/التعليم العالي"
]


# حالات المحادثة
NAME, STAGE_SELECTION, COUNTRY_SELECTION, MAIN_MENU = range(4) 
# حالات المحادثة للمدير 
ADMIN_PASSWORD_ENTRY, ADMIN_MENU, PREMIUM_ID_ENTRY, PREMIUM_DEACTIVATE_ID_ENTRY, BROADCAST_MESSAGE_ENTRY, CHANGE_PRICE_ENTRY, CONTACT_SETTINGS_MENU, CHANGE_EMAIL_ENTRY, CHANGE_INSTAGRAM_ENTRY = range(4, 13) 

# إعدادات الإعلان للتحقق من 5 ثوانٍ
AD_START_CALLBACK_DATA = "start_ad_timer"      
AD_CHECK_CALLBACK_DATA = "check_ad_timer"      

# إعدادات التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# دوال تحميل وحفظ الإعدادات (السعر الديناميكي ومعلومات التواصل)
def load_config():
    """تحميل الإعدادات من ملف JSON، وإذا لم يوجد ينشئ الإعداد الافتراضي."""
    os.makedirs(f'{BASE_DIR}/البيانات', exist_ok=True) 
    default_config = {
        "premium_price": "10 ريال سعودي", # تم تحديث القيمة الافتراضية بناء على طلبك
        "contact_email": "mosapadn@gmail.com",
        "contact_instagram": "mos_adn",
        "show_email": True,
        "show_instagram": True
    }
    if not os.path.exists(CONFIG_FILE):
        save_config(default_config)
        return default_config
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # ضمان وجود كل المفاتيح
            for key, default_value in default_config.items():
                config.setdefault(key, default_value)
            return config
    except Exception as e:
        logger.error(f"خطأ في تحميل ملف الإعدادات: {e}")
        return default_config

def save_config(config):
    """حفظ الإعدادات إلى ملف JSON."""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"خطأ في حفظ ملف الإعدادات: {e}")

# تحميل الإعدادات عند بدء التشغيل
GLOBAL_CONFIG = load_config()
PREMIUM_PRICE = GLOBAL_CONFIG.get('premium_price', '10 ريال سعودي')
CONTACT_EMAIL = GLOBAL_CONFIG.get('contact_email', 'mosapadn@gmail.com')
CONTACT_INSTAGRAM = GLOBAL_CONFIG.get('contact_instagram', 'mos_adn')


# تهيئة الذكاء الاصطناعي
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
    AI_جاهز = True
    print("✅ تم تهيئة الذكاء الاصطناعي بنجاح!")
except Exception as e:
    AI_جاهز = False
    print(f"❌ خطأ في الذكاء الاصطناعي: {e}")

# إنشاء هيكل المجلدات وقاعدة البيانات
def انشاء_الهيكل():
    مجلدات_الكتب = [
        f"{BASE_DIR}/الكتب_النصية/الاول_ثانوي",
        f"{BASE_DIR}/الكتب_النصية/الثاني_ثانوي", 
        f"{BASE_DIR}/الكتب_النصية/الثالث_علمي",
        f"{BASE_DIR}/الكتب_النصية/الثالث_ادبي",
        f"{BASE_DIR}/البيانات"
    ]
    for مجلد in مجلدات_الكتب:
        os.makedirs(مجلد, exist_ok=True)
انشاء_الهيكل()

def تهيئة_قاعدة_البيانات():
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS الطلاب (
                معرف_المستخدم INTEGER PRIMARY KEY,
                الاسم TEXT NOT NULL,
                الصف TEXT NOT NULL,           
                معرف_التحقق_الفريد TEXT UNIQUE,
                عدد_الاسئلة INTEGER DEFAULT 0,
                تاريخ_التسجيل TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                آخر_نشاط TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ردود_منذ_الإعلان INTEGER DEFAULT 0,  
                is_premium INTEGER DEFAULT 0         
            )
        ''')

        try:
            cursor.execute("SELECT الدولة FROM الطلاب LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE الطلاب ADD COLUMN الدولة TEXT DEFAULT 'المملكة العربية السعودية'") 
            logger.info("تم إضافة عمود 'الدولة' إلى جدول الطلاب.")


        cursor.execute('''
            CREATE TABLE IF NOT EXISTS الاسئلة (
                معرف_سؤال INTEGER PRIMARY KEY AUTOINCREMENT,
                معرف_المستخدم INTEGER,
                السؤال TEXT NOT NULL,
                الكتاب TEXT,
                نوع_البحث TEXT,
                تاريخ_السؤال TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (معرف_المستخدم) REFERENCES الطلاب (معرف_المستخدم)
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ خطأ في قاعدة البيانات: {e}")

تهيئة_قاعدة_البيانات() 

# دوال إدارة البيانات 
def جلب_طالب(معرف_المستخدم):
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('SELECT الاسم, الصف, الدولة, معرف_التحقق_الفريد, is_premium FROM الطلاب WHERE معرف_المستخدم = ?', (معرف_المستخدم,))
        result = cursor.fetchone()
        conn.close()
        return result
    except Exception as e:
        logger.error(f"خطأ في جلب الطالب: {e}")
        return None

def حفظ_طالب(معرف_المستخدم, الاسم, المرحلة_الدراسية, الدولة, معرف_التحقق_الفريد=None):
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO الطلاب (معرف_المستخدم, الاسم, الصف, الدولة, معرف_التحقق_الفريد, آخر_نشاط)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (معرف_المستخدم, الاسم, المرحلة_الدراسية, الدولة, معرف_التحقق_الفريد))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ خطأ في حفظ الطالب: {e}")
        return False

def تسجيل_سؤال(معرف_المستخدم, السؤال, الكتاب=None, نوع_البحث="عام"):
    """تسجيل السؤال وزيادة عداد الإعلانات (تم إصلاح NameError هنا)"""
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO الاسئلة (معرف_المستخدم, السؤال, الكتاب, نوع_البحث)
            VALUES (?, ?, ?, ?)
        ''', (معرف_المستخدم, السؤال, الكتاب, نوع_البحث))
        
        # زيادة عداد الأسئلة وعداد الإعلانات 
        cursor.execute('''
            UPDATE الطلاب 
            SET عدد_الاسئلة = عدد_الاسئلة + 1, 
                آخر_نشاط = CURRENT_TIMESTAMP,
                ردود_منذ_الإعلان = ردود_منذ_الإعلان + 1 
            WHERE معرف_المستخدم = ?
        ''', (معرف_المستخدم,)) # 💡 تم تصحيح 'معرف_المخدم' إلى 'معرف_المستخدم'
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ خطأ في تسجيل السؤال: {e}")
        return False

# نظام الإعلانات و Premium (بقي كما هو)
async def pre_check_ad_block(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    """يتحقق مما إذا كان يجب عرض إعلان ومنع الإجابة عن السؤال التالي."""
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute('SELECT is_premium, ردود_منذ_الإعلان FROM الطلاب WHERE معرف_المستخدم = ?', (user_id,))
        result = cursor.fetchone()
        
        if result is None:
            conn.close()
            return False

        is_premium, ad_count = result[-2], result[-1]
        conn.close()
        
        if is_premium == 0 and ad_count >= AD_RESPONSE_LIMIT:
            keyboard = [
                [InlineKeyboardButton("🔗 انقر هنا لتفعيل زر المتابعة", callback_data=AD_START_CALLBACK_DATA)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"🛑 **نحتاج دعمك (إعلان):**\n\n"
                f"أنت بحاجة لدعم البوت لتمويل استمرار الخدمة.\n"
                f"يرجى **الضغط على الزر أدناه**، ثم اتبع التعليمات في الرسالة التالية لتمكين سؤالك.",
                reply_markup=reply_markup
            )
            context.user_data['last_question_text'] = update.message.text 
            return True 
        
        return False 
        
    except Exception as e:
        logger.error(f"خطأ في فحص الإعلان: {e}")
        return False 

async def handle_ad_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة ضغط زر بدء الإعلان (تسجيل الوقت وإظهار الرابط الفعلي)"""
    query = update.callback_query
    await query.answer("يرجى الضغط على الرابط وانتظار 5 ثوانٍ...")
    user_id = query.from_user.id
    
    if query.data == AD_START_CALLBACK_DATA:
        context.user_data['ad_start_time'] = time.time()
        
        keyboard = [
            [InlineKeyboardButton("🌐 رابط الإعلان (اضغط هنا)", url=AD_LINK)],
            [InlineKeyboardButton("✅ المتابعة بعد 5 ثواني", callback_data=AD_CHECK_CALLBACK_DATA)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=f"⚠️ **الخطوات المطلوبة:**\n"
                 f"1. **اضغط على الرابط أعلاه** وانتظر في الصفحة لمدة 5 ثوانٍ على الأقل.\n"
                 f"2. اضغط على زر **'المتابعة بعد 5 ثواني'**.",
            reply_markup=reply_markup
        )

async def handle_ad_check_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """التحقق من مرور 5 ثوانٍ وتصفير العداد"""
    query = update.callback_query
    await query.answer() 
    user_id = query.from_user.id
    
    start_time = context.user_data.get('ad_start_time')
    
    if query.data == AD_CHECK_CALLBACK_DATA and start_time:
        elapsed_time = time.time() - start_time
        REQUIRED_TIME = 5 # 5 ثواني
        
        if elapsed_time >= REQUIRED_TIME:
            try:
                conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
                cursor = conn.cursor()
                
                # تصفير العداد
                cursor.execute('UPDATE الطلاب SET ردود_منذ_الإعلان = 0 WHERE معرف_المستخدم = ?', (user_id,))
                conn.commit()
                conn.close()
                
                context.user_data.pop('ad_start_time', None)
                last_q = context.user_data.pop('last_question_text', "سؤالك الأخير")

                await query.edit_message_text(
                    text=f"✅ **شكراً لدعمك!**\n\nتم تصفير العداد. يمكنك الآن إعادة طرح سؤالك السابق: `{last_q}`",
                    reply_markup=None 
                )
                
            except Exception as e:
                logger.error(f"خطأ في تصفير عداد الإعلان: {e}")
                await query.edit_message_text(f"❌ حدث خطأ في تصفير العداد. حاول /start.")
        else:
            remaining_time = int(REQUIRED_TIME - elapsed_time) + 1
            await query.answer(f"⏳ يجب الانتظار {remaining_time} ثانية أخرى قبل المتابعة.", show_alert=True)
            
# دوال إدارة المدير (بقت كما هي)
def جلب_جميع_الطلاب():
    """جلب معلومات جميع الطلاب (الاسم، الرمز، المرحلة، معرف المستخدم)"""
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('SELECT الاسم, معرف_التحقق_الفريد, الصف, معرف_المستخدم FROM الطلاب') 
        result = cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        logger.error(f"خطأ في جلب جميع الطلاب: {e}")
        return []

def جلب_المشتركين_البريميم():
    """جلب معلومات المشتركين البريميم فقط"""
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('SELECT الاسم, معرف_التحقق_الفريد, معرف_المستخدم FROM الطلاب WHERE is_premium = 1')
        result = cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        logger.error(f"خطأ في جلب المشتركين البريميم: {e}")
        return []

def إلغاء_اشتراك_بريميم(معرف_فريد):
    """إلغاء تفعيل البريميم بناءً على الرمز الفريد"""
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE الطلاب 
            SET is_premium = 0, ردود_منذ_الإعلان = 0
            WHERE معرف_التحقق_الفريد = ? AND is_premium = 1
        ''', (معرف_فريد,))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        return rows_affected > 0
    except Exception as e:
        logger.error(f"خطأ في إلغاء تفعيل البريميم: {e}")
        return False
        
# دوال مساعدة (لإدارة الكتب والإحصائيات) (تم إصلاح IndentationError هنا)
def جلب_احصائيات_الطالب(معرف_المستخدم):
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT الاسم, الصف, عدد_الاسئلة, تاريخ_التسجيل, آخر_نشاط, معرف_التحقق_الفريد, is_premium
            FROM الطلاب WHERE معرف_المستخدم = ?
        ''', (معرف_المستخدم,))
        result = cursor.fetchone()
        conn.close()
        return result
    except Exception as e:
        return None

def احصل_على_الكتب_حسب_الصف(الصف):
    مجلد_الصف = {
        "📚 الأول الثانوي": "الاول_ثانوي", "📚 الثاني الثانوي": "الثاني_ثانوي",
        "📚 الثالث الثانوي (علمي)": "الثالث_علمي", "📚 الثالث الثانوي (أدبي)": "الثالث_ادبي"
    }.get(الصف)
    if not مجلد_الصف: return []
    مسار_المجلد = f"{BASE_DIR}/الكتب_النصية/{مجلد_الصف}"
    if not os.path.exists(مسار_المجلد): return []
    كتب = []
    for ملف in os.listdir(مسار_المجلد):
        if ملف.endswith('.txt'):
            اسم_بسيط = ملف.replace('.txt', '').replace('_', ' ')
            كتب.append({'اسم_ملف': ملف, 'اسم_عرض': f"📖 {اسم_بسيط}", 'مسار': f"{مسار_المجلد}/{ملف}"})
    return sorted(كتب, key=lambda x: x['اسم_عرض'])

def استخراج_اجزاء_ذكية(مسار_الكتاب, السؤال, عدد_الاجزاء=3):
    """استخراج الأجزاء الأكثر صلة بالسؤال من الكتاب (تم إصلاح IndentationError)"""
    try:
        with open(مسار_الكتاب, 'r', encoding='utf-8') as ملف:
            محتوى = ملف.read()
        
        فقرات = [ف for ف in محتوى.split('\n\n') if len(ف.strip()) > 50]
        
        if not فقرات:
            return محتوى[:3000]
        
        كلمات_مهمة = [كلمة for كلمة in السؤال.split() if len(كلمة) > 3]
        
        فقرات_مرتبة = []
        for فقرة in فقرات:
            نقاط = sum(1 for كلمة in كلمات_مهمة if كلمة in فقرة)
            if نقاط > 0:
                   فقرات_مرتبة.append((نقاط, فقرة))
        
        # 💡 تم التأكد من المسافة البادئة هنا
        فقرات_مرتبة.sort(reverse=True)
        فقرات_مختارة = [ف[1] for ف in فقرات_مرتبة[:عدد_الاجزاء]]
        
        if فقرات_مختارة:
            return "\n\n".join( فقرات_مختارة)
        else:
            return "\n\n".join( فقرات[:2])
            
    except Exception as e:
        logger.error(f"❌ خطأ في استخراج الأجزاء: {e}")
        return ""
    # app.py (القسم الثاني: معالجات المستخدم - التسجيل والقائمة الرئيسية والأسئلة)

# ------------------------------------
# Handlers - التسجيل
# ------------------------------------
async def start(update: Update, context):
    user = update.message.from_user
    معلومات_الطالب = جلب_طالب(user.id) 

    if معلومات_الطالب:
        # الترتيب: الاسم، المرحلة (الصف)، الدولة، الرمز، البريميوم
        context.user_data['الاسم'], context.user_data['المرحلة_الدراسية'], context.user_data['الدولة'], context.user_data['معرف_التحقق_الفريد'], context.user_data['is_premium'] = معلومات_الطالب
        await update.message.reply_text(f"🎓 أهلاً بعودتك {context.user_data['الاسم']}!\n\n")
        await عرض_القائمة_الرئيسية(update, context)
        return MAIN_MENU
    else:
        await update.message.reply_text(
            f"🎓 أهلاً بك {user.first_name}!\n\n"
            f"أنـا بـوت **جـاوِب صـح** 🧠 للإجابات المنهجية الشاملة.\n"
            f"ما هو **اسمك الثلاثي**؟"
        )
        return NAME

async def get_name(update: Update, context):
    context.user_data['الاسم'] = update.message.text
    
    # قائمة الأزرار للمراحل الدراسية
    keyboard = []
    for stage in EDUCATION_STAGES:
        keyboard.append([KeyboardButton(stage)])

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(f"👤 تم التسجيل: {context.user_data['الاسم']}\n\n🏫 الآن اختر **مرحلتك الدراسية**:", reply_markup=reply_markup)
    return STAGE_SELECTION 

async def get_stage(update: Update, context):
    stage = update.message.text
    if stage not in EDUCATION_STAGES:
        await update.message.reply_text("❌ مرحلة دراسية غير صالحة. الرجاء اختيار من القائمة:")
        return STAGE_SELECTION
    
    context.user_data['المرحلة_الدراسية'] = stage
    
    # قائمة الأزرار للدول العربية
    keyboard = []
    for i in range(0, len(ARAB_COUNTRIES), 2):
        row = [KeyboardButton(ARAB_COUNTRIES[i])]
        if i + 1 < len(ARAB_COUNTRIES):
            row.append(KeyboardButton(ARAB_COUNTRIES[i+1]))
        keyboard.append(row)

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(f"✅ المرحلة المختارة: {stage}\n\n🌍 الآن اختر **دولتك** ليتم توجيه الإجابات حسب المنهج:", reply_markup=reply_markup)
    return COUNTRY_SELECTION 

async def get_country(update: Update, context):
    user_id = update.message.from_user.id
    country = update.message.text
    
    if country not in ARAB_COUNTRIES:
        await update.message.reply_text("❌ دولة غير صالحة. الرجاء اختيار من القائمة:")
        return COUNTRY_SELECTION
        
    context.user_data['الدولة'] = country
    
    # حفظ البيانات في قاعدة البيانات
    معرف_فريد = str(uuid.uuid4()).split('-')[0].upper()
    context.user_data['معرف_التحقق_الفريد'] = معرف_فريد
    context.user_data['is_premium'] = 0 
    
    حفظ_طالب(user_id, context.user_data['الاسم'], context.user_data['المرحلة_الدراسية'], context.user_data['الدولة'], معرف_فريد)
    
    await update.message.reply_text(
        f"✅ **تم التسجيل بنجاح!**\n\n"
        f"👤 الطالب: {context.user_data['الاسم']}\n"
        f"🏫 المرحلة: {context.user_data['المرحلة_الدراسية']}\n"
        f"🌍 الدولة: {context.user_data['الدولة']}\n"
        f"🔑 **معرف التفعيل (Premium ID):** `{معرف_فريد}`\n\n"
    )
    
    await عرض_القائمة_الرئيسية(update, context)
    return MAIN_MENU

async def عرض_القائمة_الرئيسية(update, context):
    المرحلة = context.user_data.get('المرحلة_الدراسية')
    الدولة = context.user_data.get('الدولة', 'السعودية')
    
    # الكتب المتاحة
    كتب = احصل_على_الكتب_حسب_الصف(المرحلة) if المرحلة else []
    
    keyboard = []
    
    if كتب:
        for i in range(0, len(كتب), 2):
            صف_ازرار = [كتب[i]['اسم_عرض']]
            if i + 1 < len(كتب):
                صف_ازرار.append(كتب[i + 1]['اسم_عرض'])
            keyboard.append(صف_ازرار)
        context.user_data['الكتب'] = {كتاب['اسم_عرض']: كتاب for كتاب in كتب}
    
    keyboard.append([KeyboardButton("🔍 بحث عام")])
    keyboard.append([KeyboardButton("📊 إحصائياتي"), KeyboardButton("🔑 معرف التفعيل"), KeyboardButton("🔄 تحديث القائمة")])
    keyboard.append([KeyboardButton("ℹ️ المساعدة"), KeyboardButton("🗃️ الأوامر")]) 
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # جلب الإعدادات الديناميكية 
    current_price = GLOBAL_CONFIG.get('premium_price', '10 ريال سعودي')
    contact_email = GLOBAL_CONFIG.get('contact_email', 'mosapadn@gmail.com')
    contact_instagram = GLOBAL_CONFIG.get('contact_instagram', 'mos_adn')
    show_email = GLOBAL_CONFIG.get('show_email', True)
    show_instagram = GLOBAL_CONFIG.get('show_instagram', True)

    رسالة = f"📚 **القائمة الرئيسية - {المرحلة} ({الدولة})**\n\n"
    
    if كتب:
        رسالة += f"✅ **الكتب المتاحة ({len(كتب)} كتاب)**\n"
    else:
        رسالة += "💡 يمكنك الآن استخدام **البحث العام** للإجابة على أسئلتك المنهجية."
        
    رسالة += f"\n{'🧠 الذكاء الاصطناعي: جاهز' if AI_جاهز else '⚠️ الوضع المحدود'}"
    
    is_premium = context.user_data.get('is_premium', 0)
    رسالة += f"\n✨ **Premium:** {'✅ مفعل' if is_premium else '❌ غير مفعل'}"
    
    if is_premium == 0:
        # 💡 رسالة Premium المحسّنة
        رسالة += (f"\n\n💎 **تفعيل Premium (إزالة الإعلانات):**\n"
                   f"💰 السعر: **{current_price}**\n"
                   f"(يرجى ملاحظة: **لن يتم دفع أي مبلغ إلا بعد تفعيل اشتراكك من قِبل المطور!**)\n"
                   )
        if show_email:
             رسالة += f"✉️ للتواصل مع المطور: {contact_email}\n"
        if show_instagram:
             # التأكد من عدم وجود @ مكررة
             display_instagram = contact_instagram.lstrip('@')
             رسالة += f"📸 أو عبر إنستجرام: @{display_instagram}\n"
        
    await update.message.reply_text(رسالة, reply_markup=reply_markup)

async def handle_main_menu(update: Update, context):
    user_input = update.message.text
    user_id = update.message.from_user.id
    
    # 0. التحقق من المنع بالإعلان
    is_blocked = await pre_check_ad_block(update, context, user_id)
    if is_blocked:
        return MAIN_MENU 

    # 1. أوامر المدير
    input_lower = user_input.lower().strip()
    if input_lower in ['/admin', '\admin', 'admin']: 
        return await admin_command(update, context) 

    # 2. معالجة الأزرار
    if user_input == "🔍 بحث عام":
        context.user_data['نوع_البحث'] = 'عام'
        context.user_data['الكتاب_المحدد'] = None
        await update.message.reply_text("🔍 **وضع البحث العام**\n\nاكتب سؤالك وسأجيبك بإجابة تعليمية شاملة:")
        
    elif user_input == "🔑 معرف التفعيل":
        معرف_فريد = context.user_data.get('معرف_التحقق_الفريد', 'غير متوفر')
        is_premium = context.user_data.get('is_premium', 0)
        رسالة = f"🔑 **معرف التفعيل الخاص بك:**\n\n`{معرف_فريد}`\n\n"
        رسالة += f"✨ **حالة Premium:** {'✅ مفعل' if is_premium else '❌ غير مفعل'}\n\n"
        await update.message.reply_text(رسالة)
        
    elif user_input == "📊 إحصائياتي":
        احصائيات = جلب_احصائيات_الطالب(user_id)
        if احصائيات:
            الاسم, المرحلة_الدراسية, عدد_الاسئلة, تاريخ_التسجيل, آخر_نشاط, معرف_فريد, is_premium = احصائيات
            await update.message.reply_text(
                f"📊 **إحصائياتك الدراسية**\n\n"
                f"👤 **الطالب:** {الاسم}\n"
                f"🏫 **المرحلة:** {المرحلة_الدراسية}\n"
                f"❓ **عدد الأسئلة:** {عدد_الاسئلة}\n"
                f"🕒 **آخر نشاط:** {آخر_نشاط[:16] if آخر_نشاط else 'غير متوفر'}"
            )
        else:
            await update.message.reply_text("❌ لا توجد بيانات لإحصائياتك")
            
    elif user_input == "🔄 تحديث القائمة":
        await update.message.reply_text("🔄 جاري تحديث القائمة...")
        معلومات_الطالب = جلب_طالب(user_id)
        if معلومات_الطالب:
             context.user_data['الاسم'], context.user_data['المرحلة_الدراسية'], context.user_data['الدولة'], context.user_data['معرف_التحقق_الفريد'], context.user_data['is_premium'] = معلومات_الطالب
        await عرض_القائمة_الرئيسية(update, context)
        
    elif user_input == "ℹ️ المساعدة":
        await update.message.reply_text("💡 **دليل الاستخدام:**...\n(شرح البحث والكتاب)")
    
    elif user_input == "🗃️ الأوامر": 
        await update.message.reply_text("🗃️ **أوامر البوت المتاحة:**\n\n• `/start`: للبدء، أو إعادة تسجيل الطالب.")
        
    elif user_input in context.user_data.get('الكتب', {}):
        كتاب = context.user_data['الكتب'][user_input]
        context.user_data['الكتاب_المحدد'] = كتاب
        context.user_data['نوع_البحث'] = 'كتاب'
        await update.message.reply_text(f"✅ **تم اختيار الكتاب:** {user_input}\n\n📝 اكتب سؤالك الآن وسأبحث في هذا الكتاب:")
        
    else:
        await معالجة_سؤال(update, context, user_input)
    
    return MAIN_MENU

async def معالجة_سؤال(update, context, سؤال):
    user_id = update.message.from_user.id
    نوع_البحث = context.user_data.get('نوع_البحث', 'عام')
    كتاب = context.user_data.get('الكتاب_المحدد')
    اسم_الطالب = context.user_data.get('الاسم', 'يا طالب') 
    مرحلة_الطالب = context.user_data.get('المرحلة_الدراسية', 'الثانوية العامة') 
    دولة_الطالب = context.user_data.get('الدولة', 'السعودية') 
    
    # 1. المعالجة الخاصة لسؤال من برمجك/من سواك 
    question_lower = سؤال.lower().strip()
    if any(phrase in question_lower for phrase in ["من سواك", "من برمجك", "من طورك", "مصممك"]):
         await update.message.reply_text(
             f"👋🏼 أنا بوت جاوِب صَح، تم تطويري وبرمجتي بواسطة **مصعب فهد**."
         )
         return MAIN_MENU # إنهاء المعالجة هنا

    # 2. تسجيل السؤال والبدء في المعالجة العادية
    تسجيل_سؤال(user_id, سؤال, كتاب['اسم_ملف'] if كتاب else None, نوع_البحث)
    await update.message.reply_text("🧠 **جاري البحث والمعالجة...**")
    
    try:
        if not AI_جاهز: raise Exception("الذكاء الاصطناعي غير متاح حالياً")
        
        # برومبت مُحسن وشامل (تم إضافة سياق البوت التعليمي)
        base_prompt = (
            f"أنت معلم خبير في المنهج {دولة_الطالب} للمرحلة {مرحلة_الطالب}. "
            f"اسم الطالب هو {اسم_الطالب}. "
            f"أنت تعمل ضمن بوت تعليمي على تطبيق تيليجرام (Telegram Educational Bot) ومهامك الرئيسية هي مساعدة الطلاب تعليمياً. "
            f"مهمتك هي الإجابة على استفسارات الطلاب التعليمية بأعلى درجة من الدقة والموثوقية المنهجية، "
            f"مع التركيز على المنهج الدراسي لدولة {دولة_الطالب} والمرحلة {مرحلة_الطالب}. "
        )

        if نوع_البحث == 'كتاب' and كتاب:
            محتوى_ذكي = استخراج_اجزاء_ذكية(كتاب['مسار'], سؤال)
            prompt = (
                f"{base_prompt} استخدم فقط النص التالي للإجابة. إذا لم تجد الإجابة، "
                f"أجب بـ 'عفواً يا {اسم_الطالب}، لم أجد إجابة هذا السؤال في الأجزاء الأكثر صلة من الكتاب المتاح لي.'\n\n"
                f"النص المستخرج: {محتوى_ذكي}\n\n"
                f"السؤال: {سؤال}"
            )
            response = model.generate_content(prompt)
            إجابة = response.text
            await update.message.reply_text(f"📖 **الإجابة من {كتاب['اسم_عرض']}:**\n\n{إجابة}")
            
        else:
            prompt = f"{base_prompt} السؤال: {سؤال}"
            response = model.generate_content(prompt)
            إجابة = response.text
            await update.message.reply_text(f"🎯 **الإجابة التعليمية يا {اسم_الطالب}:**\n\n{إجابة}")
        
        await update.message.reply_text("💡 هل لديك سؤال آخر؟ يمكنك كتابته مباشرة، أو اختر **'🔄 تحديث القائمة'** للعودة للقائمة الرئيسية.")
            
    except Exception as e:
        logger.error(f"❌ خطأ فادح في Gemini: {e}")
        await update.message.reply_text(f"❌ **حدث خطأ في المعالجة**. الحلول المقترحة: جرب سؤالاً آخر، أو تأكد من مفتاح Gemini.")
    
    return MAIN_MENU 

async def cancel(update: Update, context):
    await update.message.reply_text('تم إلغاء المحادثة.\nيمكنك البدء مرة أخرى بـ /start')
    return ConversationHandler.END
# app.py (القسم الثالث: معالجات المدير والتشغيل النهائي)

# ------------------------------------
# دوال لوحة المدير (المحدثة)
# ------------------------------------

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔐 **لوحة المدير:**\nالرجاء إدخال كلمة المرور:")
    return ADMIN_PASSWORD_ENTRY

async def get_admin_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text
    if password == ADMIN_PASSWORD:
        context.user_data['is_admin'] = True
        await update.message.reply_text("✅ **تم تسجيل الدخول كمدير!**")
        return await admin_menu(update, context)
    else:
        await update.message.reply_text("❌ كلمة مرور خاطئة. الرجاء البدء بـ admin مرة أخرى.")
        if context.user_data.get('الاسم'):
             return MAIN_MENU
        return ConversationHandler.END 

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة المدير المحدثة"""
    keyboard = [
        [KeyboardButton("🔑 تفعيل بريميم لرمز"), KeyboardButton("🚫 إلغاء بريميم لرمز")],
        [KeyboardButton("👥 عرض كل المستخدمين"), KeyboardButton("✨ عرض مشتركي بريميم")],
        [KeyboardButton("📣 مسابقات (إرسال إشعار للكل)"), KeyboardButton("💵 تغيير سعر البوت")],
        [KeyboardButton("📞 إعدادات التواصل"), KeyboardButton("🔙 العودة للقائمة الرئيسية")] # 💡 زر إعدادات التواصل
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🛠️ **قائمة المدير**\n\nاختر الإجراء المطلوب:", 
        reply_markup=reply_markup
    )
    return ADMIN_MENU

async def handle_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة اختيارات قائمة المدير"""
    user_input = update.message.text
    
    if user_input == "🔑 تفعيل بريميم لرمز":
        await update.message.reply_text("الرجاء إدخال **معرف التفعيل (Premium ID)** للطالب المطلوب تفعيله:")
        return PREMIUM_ID_ENTRY
        
    elif user_input == "🚫 إلغاء بريميم لرمز":
        await update.message.reply_text("الرجاء إدخال **معرف التفعيل (Premium ID)** للطالب المطلوب **إلغاء** تفعيله:")
        return PREMIUM_DEACTIVATE_ID_ENTRY
        
    elif user_input == "💵 تغيير سعر البوت": 
        current_price = GLOBAL_CONFIG.get('premium_price', '10 ريال سعودي')
        await update.message.reply_text(
            f"💵 **تغيير سعر البوت**\n\n"
            f"السعر الحالي هو: **{current_price}**\n"
            f"الرجاء إدخال السعر الجديد كاملاً (مثال: 50 دولار أمريكي، 100 جنيه مصري):"
        )
        return CHANGE_PRICE_ENTRY

    elif user_input == "📞 إعدادات التواصل": 
        return await contact_settings_menu(update, context)
        
    elif user_input == "👥 عرض كل المستخدمين":
        return await display_all_users_info(update, context)
        
    elif user_input == "✨ عرض مشتركي بريميم":
        return await display_premium_users_info(update, context)
        
    elif user_input == "📣 مسابقات (إرسال إشعار للكل)":
        await update.message.reply_text("📣 **وضع الإشعار الجماعي**\n\nالرجاء كتابة **الرسالة الكاملة** التي تريد إرسالها لجميع المستخدمين:")
        return BROADCAST_MESSAGE_ENTRY
        
    elif user_input == "🔙 العودة للقائمة الرئيسية":
        معلومات_الطالب = جلب_طالب(update.message.from_user.id)
        if معلومات_الطالب:
             context.user_data['الاسم'], context.user_data['المرحلة_الدراسية'], context.user_data['الدولة'], context.user_data['معرف_التحقق_الفريد'], context.user_data['is_premium'] = معلومات_الطالب

        context.user_data['is_admin'] = False
        await update.message.reply_text("↩️ تم تسجيل الخروج من وضع المدير.")
        await عرض_القائمة_الرئيسية(update, context) 
        return MAIN_MENU 
    
    else:
        await update.message.reply_text("اختيار غير صالح. الرجاء الاختيار من الأزرار.")
        return ADMIN_MENU

# 💡 دالة جديدة: قائمة إعدادات التواصل
async def contact_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email_status = "مفعل" if GLOBAL_CONFIG.get('show_email') else "مخفي"
    insta_status = "مفعل" if GLOBAL_CONFIG.get('show_instagram') else "مخفي"
    
    keyboard = [
        [KeyboardButton(f"✉️ تغيير البريد الإلكتروني ({GLOBAL_CONFIG.get('contact_email', 'غير محدد')})")],
        [KeyboardButton(f"📸 تغيير يوزر إنستجرام (@{GLOBAL_CONFIG.get('contact_instagram', 'غير محدد')})")],
        [KeyboardButton(f"👁️‍🗨️ عرض/إخفاء البريد (الحالة: {email_status})")],
        [KeyboardButton(f"👁️‍🗨️ عرض/إخفاء الإنستجرام (الحالة: {insta_status})")],
        [KeyboardButton("🔙 العودة لقائمة المدير")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text("📞 **إعدادات التواصل**\n\nاختر ما تريد تعديله:", reply_markup=reply_markup)
    return CONTACT_SETTINGS_MENU 

# 💡 دالة جديدة: معالجة قائمة إعدادات التواصل
async def handle_contact_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text

    if "تغيير البريد الإلكتروني" in user_input:
        await update.message.reply_text("✉️ الرجاء إدخال **البريد الإلكتروني** الجديد:")
        return CHANGE_EMAIL_ENTRY

    elif "تغيير يوزر إنستجرام" in user_input:
        await update.message.reply_text("📸 الرجاء إدخال **يوزر إنستجرام** الجديد (بدون @):")
        return CHANGE_INSTAGRAM_ENTRY

    elif "عرض/إخفاء البريد" in user_input:
        GLOBAL_CONFIG['show_email'] = not GLOBAL_CONFIG.get('show_email', True)
        save_config(GLOBAL_CONFIG)
        status = "✅ تم تفعيل العرض" if GLOBAL_CONFIG['show_email'] else "❌ تم تفعيل الإخفاء"
        await update.message.reply_text(f"✅ تم تحديث حالة البريد الإلكتروني. {status}")
        return await contact_settings_menu(update, context)

    elif "عرض/إخفاء الإنستجرام" in user_input:
        GLOBAL_CONFIG['show_instagram'] = not GLOBAL_CONFIG.get('show_instagram', True)
        save_config(GLOBAL_CONFIG)
        status = "✅ تم تفعيل العرض" if GLOBAL_CONFIG['show_instagram'] else "❌ تم تفعيل الإخفاء"
        await update.message.reply_text(f"✅ تم تحديث حالة يوزر إنستجرام. {status}")
        return await contact_settings_menu(update, context)

    elif user_input == "🔙 العودة لقائمة المدير":
        return await admin_menu(update, context)

    else:
        await update.message.reply_text("اختيار غير صالح.")
        return CONTACT_SETTINGS_MENU
    
# 💡 دوال جديدة: حفظ البريد والإنستجرام
async def set_new_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_email = update.message.text.strip()
    
    global GLOBAL_CONFIG
    GLOBAL_CONFIG['contact_email'] = new_email
    save_config(GLOBAL_CONFIG)
    
    await update.message.reply_text(f"✅ تم تحديث البريد الإلكتروني بنجاح: {new_email}")
    return await contact_settings_menu(update, context)

async def set_new_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_instagram = update.message.text.strip().lstrip('@')
    
    global GLOBAL_CONFIG
    GLOBAL_CONFIG['contact_instagram'] = new_instagram
    save_config(GLOBAL_CONFIG)
    
    await update.message.reply_text(f"✅ تم تحديث يوزر إنستجرام بنجاح: @{new_instagram}")
    return await contact_settings_menu(update, context)

async def set_new_price_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """حفظ السعر الجديد وتحديث الإعدادات العالمية"""
    new_price = update.message.text.strip()
    
    global PREMIUM_PRICE
    global GLOBAL_CONFIG
    
    GLOBAL_CONFIG['premium_price'] = new_price
    save_config(GLOBAL_CONFIG) # حفظ السعر بشكل دائم
    PREMIUM_PRICE = new_price # تحديث المتغير العام
    
    await update.message.reply_text(f"✅ **تم تحديث سعر البوت بنجاح!**\n\nالسعر الجديد هو: **{new_price}**")
    
    return await admin_menu(update, context)


async def activate_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    premium_id = update.message.text.strip()
    
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE الطلاب 
            SET is_premium = 1, ردود_منذ_الإعلان = 0
            WHERE معرف_التحقق_الفريد = ?
        ''', (premium_id,))
        
        conn.commit()
        
        if cursor.rowcount > 0:
            await update.message.reply_text(f"✅ **تم التفعيل بنجاح!**\n\nتم تفعيل حالة Premium للرمز: `{premium_id}`")
        else:
            await update.message.reply_text(f"❌ **فشل التفعيل!**\n\nلم يتم العثور على طالب يملك الرمز: `{premium_id}`")
            
        conn.close()
        
    except Exception as e:
        logger.error(f"خطأ في تفعيل البريميم: {e}")
        await update.message.reply_text(f"❌ حدث خطأ في قاعدة البيانات أثناء التفعيل.")

    return await admin_menu(update, context)
    
async def deactivate_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    premium_id = update.message.text.strip()
    
    if إلغاء_اشتراك_بريميم(premium_id):
        await update.message.reply_text(f"✅ **تم إلغاء التفعيل بنجاح!**\n\nتم إلغاء حالة Premium للرمز: `{premium_id}`.")
    else:
        await update.message.reply_text(f"❌ **فشل إلغاء التفعيل!**\n\nلم يتم العثور على طالب مفعل بريميم يملك الرمز: `{premium_id}`.")
        
    return await admin_menu(update, context)

async def display_all_users_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض أسماء ورموز تفعيل كل مستخدمي البوت"""
    الطلاب = جلب_جميع_الطلاب()
    
    إذا_لم_يوجد = "❌ لا يوجد طلاب مسجلين."
    
    if الطلاب:
        رسالة = "👥 **قائمة جميع المستخدمين:**\n\n"
        رسالة += "الاسم | الرمز الفريد | المرحلة | معرف المستخدم\n"
        رسالة += "------|-------------|---------|--------------\n"
        
        for الاسم, الرمز, المرحلة, معرف_المستخدم in الطلاب:
            رسالة += f"{الاسم} | {الرمز} | {المرحلة} | `{معرف_المستخدم}`\n"
            
        await update.message.reply_text(رسالة)
    else:
        await update.message.reply_text(إذا_لم_يوجد)
        
    return ADMIN_MENU

async def display_premium_users_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض أسماء ورموز تفعيل المشتركين البريميم فقط"""
    المشتركون = جلب_المشتركين_البريميم()
    
    إذا_لم_يوجد = "❌ لا يوجد مشتركون حالياً في Premium."
    
    if المشتركون:
        رسالة = "✨ **قائمة مشتركي Premium:**\n\n"
        رسالة += "الاسم | الرمز الفريد | معرف المستخدم\n"
        رسالة += "------|-------------|--------------\n"
        
        for الاسم, الرمز, معرف_المستخدم in المشتركون:
            رسالة += f"{الاسم} | {الرمز} | `{معرف_المستخدم}`\n"
            
        await update.message.reply_text(رسالة)
    else:
        await update.message.reply_text(إذا_لم_يوجد)
        
    return ADMIN_MENU
    
async def send_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إرسال الإشعار لجميع المستخدمين"""
    message = update.message.text
    
    الطلاب = جلب_جميع_الطلاب() 
    معرفات_المستخدمين = [row[3] for row in الطلاب] 
    
    رسائل_مرسلة = 0
    رسائل_فاشلة = 0
    
    await update.message.reply_text("🚀 جاري إرسال الإشعار الجماعي...")
    
    for user_id in معرفات_المستخدمين:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📣 **إشعار المسابقات/الفعاليات**\n\n"
                     f"{message}",
                parse_mode='Markdown'
            )
            رسائل_مرسلة += 1
            await asyncio.sleep(0.05) 
        except Exception as e:
            رسائل_فاشلة += 1
            logger.warning(f"❌ فشل إرسال إشعار للمستخدم {user_id}: {e}")
            
    await update.message.reply_text(
        f"✅ **تم الانتهاء من الإرسال!**\n\n"
        f"✅ الرسائل المرسلة بنجاح: {رسائل_مرسلة}\n"
        f"❌ الرسائل الفاشلة (قد يكون المستخدم حظر البوت): {رسائل_فاشلة}"
    )
    
    return await admin_menu(update, context)

def main():
    print("🔍 جاري فحص النظام...")
    
    كل_الكتب = []
    # فحص الكتب المتاحة (لإظهار الإحصائيات عند التشغيل)
    for صف in ["📚 الأول الثانوي", "📚 الثاني الثانوي", "📚 الثالث الثانوي (علمي)", "📚 الثالث الثانوي (أدبي)"]:
        كتب = احصل_على_الكتب_حسب_الصف(صف)
        كل_الكتب.extend(كتب)
    
    print(f"📊 إجمالي الكتب: {len(كل_الكتب)} كتاب (منهاج ثانوي سعودي حالياً)")
    
    try:
        app = Application.builder().token(BOT_TOKEN).build()
        
        # إعداد محادثة التسجيل
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)], 
            states={
                NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
                STAGE_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_stage)],
                COUNTRY_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_country)],
                MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu)],
                
                # Admin States
                ADMIN_PASSWORD_ENTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_admin_password)],
                ADMIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_menu)],
                PREMIUM_ID_ENTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, activate_premium)],
                PREMIUM_DEACTIVATE_ID_ENTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, deactivate_premium)],
                BROADCAST_MESSAGE_ENTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, send_broadcast_message)],
                CHANGE_PRICE_ENTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_new_price_value)],
                CONTACT_SETTINGS_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_contact_settings_menu)], 
                CHANGE_EMAIL_ENTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_new_email)], 
                CHANGE_INSTAGRAM_ENTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_new_instagram)], 
            },
            fallbacks=[
                CommandHandler('cancel', cancel),
                CommandHandler('start', start) 
            ]
        )
        
        app.add_handler(conv_handler)
        
        # إضافة معالجات أزرار الإعلان المدمجة (Callbacks)
        app.add_handler(CallbackQueryHandler(handle_ad_start_callback, pattern='^' + AD_START_CALLBACK_DATA + '$'))
        app.add_handler(CallbackQueryHandler(handle_ad_check_callback, pattern='^' + AD_CHECK_CALLBACK_DATA + '$'))


        print("🎓 البوت التعليمي المتكامل يعمل الآن!")
        
        app.run_polling()
        
    except Exception as e:
        print(f"❌ خطأ فادح في تشغيل البوت: {e}")

if __name__ == "__main__":
    main()