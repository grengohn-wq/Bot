# app.py - بوت منهج Ai (الإصدار النهائي الكامل بدون أخطاء)

import os
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '2'

import warnings
warnings.filterwarnings("ignore")
import logging
logging.getLogger('google').setLevel(logging.ERROR)

import sqlite3
import json
import uuid 
import asyncio 
import time 
import re
import csv
from datetime import datetime
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

print("🚀 بدء تشغيل بوت منهج Ai...")

# الأساسيات
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOT_TOKEN = "8522705485:AAHeqccrQ5GpXi4HiQzwyEJwQo4yt6P82Uc"
CONFIG_FILE = f'{BASE_DIR}/البيانات/config.json' 

# إعدادات المدير والإعلانات والبريميوم
ADMIN_PASSWORD = "mosap@123123"
AD_LINK = "https://otieu.com/4/10160934"
AD_RESPONSE_LIMIT = 2 

# قائمة الدول والمراحل
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
# حالات المحادثة - كاملة ومحدثة 100% (حل نهائي)
(
    NAME, STAGE_SELECTION, COUNTRY_SELECTION, REFERRAL_CODE, MAIN_MENU,
    CONVERT_POINTS, TRANSFER_MONEY, SUPPORT_MESSAGE, TASKS_MENU,
    ADMIN_PASSWORD_ENTRY, ADMIN_MENU, PREMIUM_ID_ENTRY, PREMIUM_DEACTIVATE_ID_ENTRY,
    BROADCAST_MESSAGE_ENTRY, CHANGE_PRICE_ENTRY, GIFT_PREMIUM_ENTRY,
    ADMIN_SUPPORT_MENU, ADMIN_REPLY_SUPPORT, ADMIN_MANAGE_TASKS,
    ADD_TASK, ADD_MANAGER, ADMIN_GIVE_POINTS, ADMIN_GIVE_MONEY
) = range(23)
# إعدادات الإعلان
AD_START_CALLBACK_DATA = "start_ad_timer"      
AD_CHECK_CALLBACK_DATA = "check_ad_timer"      
AD_CONFIRM_VIEW = "confirm_ad_view"

# إعدادات التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# دوال تحميل وحفظ الإعدادات
def load_config():
    """تحميل الإعدادات من ملف JSON"""
    os.makedirs(f'{BASE_DIR}/البيانات', exist_ok=True) 
    default_config = {
        "premium_price": "10 ريال سعودي",
        "contact_email": "mosapadn@gmail.com",
        "contact_instagram": "mos_adn",
        "show_email": True,
        "show_instagram": True,
        "main_gemini_token": "AIzaSyDTqXo6j5Pz5Ki5Y1fjFFGi3Uo6fp5R7b0",
        "premium_points_price": 1000
    }
    if not os.path.exists(CONFIG_FILE):
        save_config(default_config)
        return default_config
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            for key, default_value in default_config.items():
                config.setdefault(key, default_value)
            return config
    except Exception as e:
        logger.error(f"خطأ في تحميل ملف الإعدادات: {e}")
        return default_config

def save_config(config):
    """حفظ الإعدادات إلى ملف JSON"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"خطأ في حفظ ملف الإعدادات: {e}")

# تحميل الإعدادات عند بدء التشغيل
GLOBAL_CONFIG = load_config()
PREMIUM_PRICE = GLOBAL_CONFIG.get('premium_price', '10 ريال سعودي')
MAIN_GEMINI_TOKEN = GLOBAL_CONFIG.get('main_gemini_token', 'AIzaSyBr5cddPtXXQawQqE8-CbYf7POYtHCsPDM')

# تهيئة الذكاء الاصطناعي
AI_جاهز = False
model = None

if MAIN_GEMINI_TOKEN:
    try:
        genai.configure(api_key=MAIN_GEMINI_TOKEN)
        model = genai.GenerativeModel('gemini-2.0-flash')
        AI_جاهز = True
        print("✅ تم تهيئة الذكاء الاصطناعي بنجاح!")
    except Exception as e:
        AI_جاهز = False
        print(f"❌ خطأ في الذكاء الاصطناعي: {e}")
else:
    print("⚠️ لم يتم إضافة توكن جيميني رئيسي بعد.")

# إنشاء هيكل المجلدات وقاعدة البيانات
def انشاء_الهيكل():
    مجلدات = [f"{BASE_DIR}/البيانات"]
    for مجلد in مجلدات:
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
                is_premium INTEGER DEFAULT 0,
                الدولة TEXT DEFAULT 'المملكة العربية السعودية',
                is_gift_premium INTEGER DEFAULT 0,
                رصيد_النقاط INTEGER DEFAULT 0,
                رصيد_الريال INTEGER DEFAULT 0,
                is_manager INTEGER DEFAULT 0,
                احالات_ناجحة INTEGER DEFAULT 0,
                رمز_احالة_مستخدم TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS الاسئلة (
                معرف_سؤال INTEGER PRIMARY KEY AUTOINCREMENT,
                معرف_المستخدم INTEGER,
                السؤال TEXT NOT NULL,
                نوع_البحث TEXT DEFAULT 'عام',
                تاريخ_السؤال TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS المهام (
                مهمة_id INTEGER PRIMARY KEY AUTOINCREMENT,
                رابط TEXT NOT NULL,
                وصف TEXT NOT NULL,
                نقاط INTEGER DEFAULT 10,
                is_active INTEGER DEFAULT 1,
                تاريخ_الإضافة TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS المهام_المكتملة (
                إكمال_id INTEGER PRIMARY KEY AUTOINCREMENT,
                معرف_المستخدم INTEGER,
                مهمة_id INTEGER,
                تاريخ_الإكمال TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS التحويلات (
                تحويل_id INTEGER PRIMARY KEY AUTOINCREMENT,
                مرسل_id INTEGER,
                مستلم_id INTEGER,
                مبلغ INTEGER NOT NULL,
                نوع TEXT NOT NULL,
                تاريخ_التحويل TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS الدعم (
                دعم_id INTEGER PRIMARY KEY AUTOINCREMENT,
                معرف_المستخدم INTEGER,
                الرسالة TEXT NOT NULL,
                الرد TEXT,
                is_answered INTEGER DEFAULT 0,
                تاريخ_الرسالة TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                تاريخ_الرد TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ تم تهيئة قاعدة البيانات بنجاح!")
    except Exception as e:
        print(f"❌ خطأ في قاعدة البيانات: {e}")

تهيئة_قاعدة_البيانات()

# دوال إدارة البيانات 
def جلب_طالب(معرف_المستخدم):
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT الاسم, الصف, الدولة, معرف_التحقق_الفريد, is_premium, is_gift_premium,
                   رصيد_النقاط, رصيد_الريال, is_manager, احالات_ناجحة, رمز_احالة_مستخدم 
            FROM الطلاب WHERE معرف_المستخدم = ?
        ''', (معرف_المستخدم,))
        result = cursor.fetchone()
        conn.close()
        return result
    except Exception as e:
        logger.error(f"خطأ في جلب الطالب: {e}")
        return None

def حفظ_طالب(معرف_المستخدم, الاسم, المرحلة_الدراسية, الدولة, معرف_التحقق_الفريد=None, رمز_احالة_مستخدم=None):
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO الطلاب 
            (معرف_المستخدم, الاسم, الصف, الدولة, معرف_التحقق_الفريد, آخر_نشاط, رمز_احالة_مستخدم)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
        ''', (معرف_المستخدم, الاسم, المرحلة_الدراسية, الدولة, معرف_التحقق_الفريد, رمز_احالة_مستخدم))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ خطأ في حفظ الطالب: {e}")
        return False

def التحقق_من_رمز_الاحالة(رمز_الاحالة):
    """التحقق من وجود رمز الإحالة في قاعدة البيانات"""
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('SELECT معرف_المستخدم, الاسم FROM الطلاب WHERE معرف_التحقق_الفريد = ?', (رمز_الاحالة,))
        result = cursor.fetchone()
        conn.close()
        return result
    except Exception as e:
        logger.error(f"خطأ في التحقق من رمز الإحالة: {e}")
        return None

def منح_نقاط_الاحالة(معرف_المحيل, معرف_المستخدم_الجديد, اسم_المستخدم_الجديد):
    """منح 100 نقطة للمحيل وإرسال إشعار"""
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        
        # إضافة النقاط للمحيل
        cursor.execute('UPDATE الطلاب SET رصيد_النقاط = رصيد_النقاط + 100, احالات_ناجحة = احالات_ناجحة + 1 WHERE معرف_المستخدم = ?', (معرف_المحيل,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"خطأ في منح نقاط الإحالة: {e}")
        return False

def تسجيل_سؤال(معرف_المستخدم, السؤال, نوع_البحث="عام"):
    """تسجيل السؤال وزيادة عداد الإعلانات"""
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO الاسئلة (معرف_المستخدم, السؤال, نوع_البحث)
            VALUES (?, ?, ?)
        ''', (معرف_المستخدم, السؤال, نوع_البحث))
        
        cursor.execute('''
            UPDATE الطلاب 
            SET عدد_الاسئلة = عدد_الاسئلة + 1, 
                آخر_نشاط = CURRENT_TIMESTAMP,
                ردود_منذ_الإعلان = ردود_منذ_الإعلان + 1 
            WHERE معرف_المستخدم = ?
        ''', (معرف_المستخدم,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ خطأ في تسجيل السؤال: {e}")
        return False

# نظام النقاط والتحويلات
def إضافة_نقاط(معرف_المستخدم, نقاط, سبب=""):
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('UPDATE الطلاب SET رصيد_النقاط = رصيد_النقاط + ? WHERE معرف_المستخدم = ?', (نقاط, معرف_المستخدم))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"خطأ في إضافة نقاط: {e}")
        return False

def تحويل_نقاط_لريال(معرف_المستخدم, نقاط):
    try:
        if نقاط < 100:
            return False, "الحد الأدنى للتحويل 100 نقطة"
        
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        
        # التحقق من الرصيد
        cursor.execute('SELECT رصيد_النقاط FROM الطلاب WHERE معرف_المستخدم = ?', (معرف_المستخدم,))
        رصيد = cursor.fetchone()[0]
        
        if رصيد < نقاط:
            conn.close()
            return False, "رصيد النقاط غير كافي"
        
        ريال = نقاط // 100
        
        # تنفيذ التحويل
        cursor.execute('''
            UPDATE الطلاب 
            SET رصيد_النقاط = رصيد_النقاط - ?,
                رصيد_الريال = رصيد_الريال + ?
            WHERE معرف_المستخدم = ?
        ''', (نقاط, ريال, معرف_المستخدم))
        
        conn.commit()
        conn.close()
        return True, f"تم تحويل {نقاط} نقطة إلى {ريال} ريال"
    except Exception as e:
        logger.error(f"خطأ في تحويل النقاط: {e}")
        return False, "حدث خطأ في التحويل"

def تحويل_ريال(مرسل_id, رمز_المستلم, مبلغ):
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        
        # التحقق من رصيد المرسل
        cursor.execute('SELECT رصيد_الريال FROM الطلاب WHERE معرف_المستخدم = ?', (مرسل_id,))
        رصيد_مرسل = cursor.fetchone()[0]
        
        if رصيد_مرسل < مبلغ:
            conn.close()
            return False, "رصيد الريال غير كافي"
        
        # البحث عن المستلم
        cursor.execute('SELECT معرف_المستخدم, الاسم FROM الطلاب WHERE معرف_التحقق_الفريد = ?', (رمز_المستلم,))
        مستلم = cursor.fetchone()
        
        if not مستلم:
            conn.close()
            return False, "لم يتم العثور على المستلم"
        
        مستلم_id, اسم_المستلم = مستلم
        
        # تنفيذ التحويل
        cursor.execute('UPDATE الطلاب SET رصيد_الريال = رصيد_الريال - ? WHERE معرف_المستخدم = ?', (مبلغ, مرسل_id))
        cursor.execute('UPDATE الطلاب SET رصيد_الريال = رصيد_الريال + ? WHERE معرف_المستخدم = ?', (مبلغ, مستلم_id))
        
        conn.commit()
        conn.close()
        return True, (مستلم_id, اسم_المستلم)
    except Exception as e:
        logger.error(f"خطأ في تحويل الريال: {e}")
        return False, "حدث خطأ في التحويل"

def شراء_بريميم(معرف_المستخدم):
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute('SELECT رصيد_الريال FROM الطلاب WHERE معرف_المستخدم = ?', (معرف_المستخدم,))
        رصيد = cursor.fetchone()[0]
        
        if رصيد < 10:
            conn.close()
            return False, "رصيد الريال غير كافي"
        
        cursor.execute('''
            UPDATE الطلاب 
            SET رصيد_الريال = رصيد_الريال - 10,
                is_premium = 1,
                ردود_منذ_الإعلان = 0
            WHERE معرف_المستخدم = ?
        ''', (معرف_المستخدم,))
        
        conn.commit()
        conn.close()
        return True, "تم شراء البريميم بنجاح"
    except Exception as e:
        logger.error(f"خطأ في شراء البريميم: {e}")
        return False, "حدث خطأ في الشراء"

# نظام المهام
def جلب_المهام_المتاحة(معرف_المستخدم):
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT م.مهمة_id, م.رابط, م.وصف, م.نقاط 
            FROM المهام م
            WHERE م.is_active = 1 
            AND م.مهمة_id NOT IN (
                SELECT مهمة_id FROM المهام_المكتملة WHERE معرف_المستخدم = ?
            )
        ''', (معرف_المستخدم,))
        
        مهام = cursor.fetchall()
        conn.close()
        return مهام
    except Exception as e:
        logger.error(f"خطأ في جلب المهام: {e}")
        return []

def إضافة_مهمة(رابط, وصف, نقاط):
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO المهام (رابط, وصف, نقاط) VALUES (?, ?, ?)', (رابط, وصف, نقاط))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"خطأ في إضافة مهمة: {e}")
        return False

def إكمال_مهمة(معرف_المستخدم, مهمة_id):
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        
        # الحصول على نقاط المهمة
        cursor.execute('SELECT نقاط FROM المهام WHERE مهمة_id = ?', (مهمة_id,))
        نقاط = cursor.fetchone()[0]
        
        # تسجيل إكمال المهمة
        cursor.execute('INSERT INTO المهام_المكتملة (معرف_المستخدم, مهمة_id) VALUES (?, ?)', (معرف_المستخدم, مهمة_id))
        
        # إضافة النقاط
        cursor.execute('UPDATE الطلاب SET رصيد_النقاط = رصيد_النقاط + ? WHERE معرف_المستخدم = ?', (نقاط, معرف_المستخدم))
        
        conn.commit()
        conn.close()
        return True, نقاط
    except Exception as e:
        logger.error(f"خطأ في إكمال المهمة: {e}")
        return False, 0

# نظام الدعم
def إرسال_رسالة_دعم(معرف_المستخدم, الرسالة):
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO الدعم (معرف_المستخدم, الرسالة) VALUES (?, ?)', (معرف_المستخدم, الرسالة))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"خطأ في إرسال رسالة دعم: {e}")
        return False

def جلب_رسائل_الدعم():
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT د.دعم_id, د.معرف_المستخدم, س.الاسم, د.الرسالة, د.تاريخ_الرسالة
            FROM الدعم د
            JOIN الطلاب س ON د.معرف_المستخدم = س.معرف_المستخدم
            WHERE د.is_answered = 0
            ORDER BY د.تاريخ_الرسالة
        ''')
        رسائل = cursor.fetchall()
        conn.close()
        return رسائل
    except Exception as e:
        logger.error(f"خطأ في جلب رسائل الدعم: {e}")
        return []

def الرد_على_دعم(دعم_id, الرد):
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute('SELECT معرف_المستخدم FROM الدعم WHERE دعم_id = ?', (دعم_id,))
        معرف_المستخدم = cursor.fetchone()[0]
        
        cursor.execute('''
            UPDATE الدعم 
            SET الرد = ?, is_answered = 1, تاريخ_الرد = CURRENT_TIMESTAMP
            WHERE دعم_id = ?
        ''', (الرد, دعم_id))
        
        conn.commit()
        conn.close()
        return True, معرف_المستخدم
    except Exception as e:
        logger.error(f"خطأ في الرد على الدعم: {e}")
        return False, None

# نظام الإعلانات و Premium
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

        is_premium, ad_count = result
        
        conn.close()
        
        if is_premium == 0 and ad_count >= AD_RESPONSE_LIMIT:
            keyboard = [
                [InlineKeyboardButton("🔗 انقر هنا لتفعيل زر المتابعة", callback_data=AD_START_CALLBACK_DATA)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"🛑 **نحتاج دعمك (إعلان):**\n\n"
                f"أنت بحاجة لدعم البوت لتمويل استمرار الخدمة.\n\n"
                f"أو **الضغط على الزر أدناه**، ثم اتبع التعليمات في الرسالة التالية لتمكين سؤالك.",
                reply_markup=reply_markup
            )
            context.user_data['last_question_text'] = update.message.text 
            return True 
        
        return False 
        
    except Exception as e:
        logger.error(f"خطأ في فحص الإعلان: {e}")
        return False 

async def handle_ad_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة ضغط زر بدء الإعلان"""
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
                 f"2. اضغط على زر **'المتابعة بعد 5 ثواني'**.\n\n"
                 f"🎁 **ستحصل على 5 نقاط مكافأة!**",
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
        REQUIRED_TIME = 5
        
        if elapsed_time >= REQUIRED_TIME:
            try:
                conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
                cursor = conn.cursor()
                
                cursor.execute('UPDATE الطلاب SET ردود_منذ_الإعلان = 0 WHERE معرف_المستخدم = ?', (user_id,))
                # إضافة 5 نقاط مكافأة
                cursor.execute('UPDATE الطلاب SET رصيد_النقاط = رصيد_النقاط + 5 WHERE معرف_المستخدم = ?', (user_id,))
                
                conn.commit()
                conn.close()
                
                context.user_data.pop('ad_start_time', None)
                last_q = context.user_data.pop('last_question_text', "سؤالك الأخير")

                await query.edit_message_text(
                    text=f"✅ **شكراً لدعمك!**\n\n"
                         f"تم تصفير العداد وإضافة 5 نقاط مكافأة!\n\n"
                         f"يمكنك الآن إعادة طرح سؤالك السابق: `{last_q}`",
                    reply_markup=None 
                )
                
            except Exception as e:
                logger.error(f"خطأ في تصفير عداد الإعلان: {e}")
                await query.edit_message_text(f"❌ حدث خطأ في تصفير العداد. حاول /start.")
        else:
            remaining_time = int(REQUIRED_TIME - elapsed_time) + 1
            await query.answer(f"⏳ يجب الانتظار {remaining_time} ثانية أخرى قبل المتابعة.", show_alert=True)

async def handle_ad_confirm_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة تأكيد مشاهدة الإعلان"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if query.data == AD_CONFIRM_VIEW:
        # إضافة 5 نقاط مكافأة
        إضافة_نقاط(user_id, 5, "مشاهدة إعلان")
        
        # تحديث البيانات
        معلومات_الطالب = جلب_طالب(user_id)
        if معلومات_الطالب:
            context.user_data['رصيد_النقاط'] = معلومات_الطالب[6]
        
        await query.edit_message_text(
            f"✅ **تم تأكيد المشاهدة!**\n\n"
            f"🎁 **المكافأة:** 5 نقاط\n"
            f"💎 **رصيد النقاط الجديد:** {context.user_data['رصيد_النقاط']} نقطة\n\n"
            f"شكراً لدعمك! 🙏"
        )

# دوال إدارة المدير
def جلب_جميع_الطلاب():
    """جلب معلومات جميع الطلاب"""
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('SELECT الاسم, معرف_التحقق_الفريد, الصف, معرف_المستخدم, is_premium, is_gift_premium FROM الطلاب') 
        result = cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        logger.error(f"خطأ في جلب جميع الطلاب: {e}")
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

def تفعيل_بريميم_هدية(معرف_فريد):
    """تفعيل البريميم كهدية"""
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE الطلاب 
            SET is_premium = 1, is_gift_premium = 1, ردود_منذ_الإعلان = 0
            WHERE معرف_التحقق_الفريد = ?
        ''', (معرف_فريد,))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        return rows_affected > 0
    except Exception as e:
        logger.error(f"خطأ في تفعيل البريميم هدية: {e}")
        return False

# دوال مساعدة
def جلب_احصائيات_الطالب(معرف_المستخدم):
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT الاسم, الصف, عدد_الاسئلة, تاريخ_التسجيل, آخر_نشاط, معرف_التحقق_الفريد, is_premium, is_gift_premium,
                   رصيد_النقاط, رصيد_الريال, is_manager, احالات_ناجحة, رمز_احالة_مستخدم
            FROM الطلاب WHERE معرف_المستخدم = ?
        ''', (معرف_المستخدم,))
        result = cursor.fetchone()
        conn.close()
        return result
    except Exception as e:
        return None

# التحقق من صحة الاسم المحدث
def التحقق_من_الاسم_الكامل(الاسم_الكامل):
    """التحقق من أن الاسم الكامل يحتوي على 3 أسماء وأحرف عربية/إنجليزية فقط"""
    if not الاسم_الكامل or len(الاسم_الكامل.strip()) == 0:
        return False, "❌ الاسم لا يمكن أن يكون فارغاً"
    
    # تقسيم الاسم إلى أجزاء
    أجزاء_الاسم = الاسم_الكامل.strip().split()
    
    # التحقق من أن الاسم مكون من 3 أجزاء
    if len(أجزاء_الاسم) != 3:
        return False, "❌ يجب إدخال الاسم الثلاثي (الاسم الأول + الأب + الجد)\nمثال: محمد عبدالله الفهد"
    
    # التحقق من كل جزء من الاسم
    for جزء in أجزاء_الاسم:
        # التحقق من وجود أرقام أو رموز
        if re.search(r'[0-9!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?]', جزء):
            return False, f"❌ الجزء '{جزء}' يحتوي على أرقام أو رموز\nيجب أن يحتوي الاسم على أحرف عربية أو إنجليزية فقط"
        
        # التحقق من أن الاسم يحتوي على أحرف صالحة فقط
        if not re.search(r'[a-zA-Zأ-ي]', جزء):
            return False, f"❌ الجزء '{جزء}' غير صالح\nيجب أن يحتوي على أحرف عربية أو إنجليزية"
    
    return True, "✅ الاسم صالح"

# Handlers - التسجيل المحدث
async def start(update: Update, context):
    user = update.message.from_user
    معلومات_الطالب = جلب_طالب(user.id) 

    if معلومات_الطالب:
        # تحديث كل بيانات المستخدم من قاعدة البيانات
        context.user_data.update({
            'الاسم': معلومات_الطالب[0],
            'المرحلة_الدراسية': معلومات_الطالب[1],
            'الدولة': معلومات_الطالب[2],
            'معرف_التحقق_الفريد': معلومات_الطالب[3],
            'is_premium': معلومات_الطالب[4],
            'is_gift_premium': معلومات_الطالب[5],
            'رصيد_النقاط': معلومات_الطالب[6],
            'رصيد_الريال': معلومات_الطالب[7],
            'is_manager': معلومات_الطالب[8],
            'احالات_ناجحة': معلومات_الطالب[9],
            'رمز_احالة_مستخدم': معلومات_الطالب[10]
        })
            
        await update.message.reply_text(f"🎓 أهلاً بعودتك {context.user_data['الاسم']}!\n\n")
        await عرض_القائمة_الرئيسية(update, context)
        return MAIN_MENU
    else:
        await update.message.reply_text(
            f"🎓 أهلاً بك {user.first_name}!\n\n"
            f"أنـا بـوت **منهج Ai** 🧠 للإجابات المنهجية الشاملة.\n\n"
            f"**الرجاء إدخال اسمك الثلاثي كاملاً:**\n"
            f"👉 الاسم الأول + اسم الأب + اسم الجد\n\n"
            f"**مثال:** محمد عبدالله الفهد"
        )
        return NAME

async def get_name(update: Update, context):
    الاسم_الكامل = update.message.text.strip()
    
    صالح, رسالة = التحقق_من_الاسم_الكامل(الاسم_الكامل)
    if not صالح:
        await update.message.reply_text(رسالة + "\n\nالرجاء إدخال الاسم الثلاثي مرة أخرى:")
        return NAME
    
    context.user_data['الاسم'] = الاسم_الكامل
    
    # قائمة الأزرار للمراحل الدراسية
    keyboard = []
    for stage in EDUCATION_STAGES:
        keyboard.append([KeyboardButton(stage)])

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(f"👤 تم التسجيل: {الاسم_الكامل}\n\n🏫 الآن اختر **مرحلتك الدراسية**:", reply_markup=reply_markup)
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
    
    await update.message.reply_text(
        f"✅ **أخيراً:**\n\n"
        f"👤 الطالب: {context.user_data['الاسم']}\n"
        f"🏫 المرحلة: {context.user_data['المرحلة_الدراسية']}\n"
        f"🌍 الدولة: {context.user_data['الدولة']}\n\n"
        f"💡 **هل لديك رمز إحالة من صديق؟**\n"
        f"(إذا لم يكن لديك، اضغط /skip)"
    )
    return REFERRAL_CODE

async def get_referral_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    رمز_الاحالة = update.message.text.strip().upper()
    
    # التحقق من رمز الإحالة
    محيل = التحقق_من_رمز_الاحالة(رمز_الاحالة)
    
    if not محيل:
        await update.message.reply_text("❌ رمز الإحالة غير صحيح. الرجاء التحقق والمحاولة مرة أخرى:")
        return REFERRAL_CODE
    
    معرف_المحيل, اسم_المحيل = محيل
    context.user_data['رمز_احالة_مستخدم'] = رمز_الاحالة
    
    # حفظ البيانات في قاعدة البيانات
    معرف_فريد = str(uuid.uuid4()).split('-')[0].upper()
    context.user_data['معرف_التحقق_الفريد'] = معرف_فريد
    context.user_data['is_premium'] = 0 
    context.user_data['is_gift_premium'] = 0
    context.user_data['رصيد_النقاط'] = 50  # مكافأة ترحيب
    context.user_data['رصيد_الريال'] = 0
    context.user_data['is_manager'] = 0
    
    حفظ_طالب(user_id, context.user_data['الاسم'], context.user_data['المرحلة_الدراسية'], 
              context.user_data['الدولة'], معرف_فريد, رمز_الاحالة)
    
    # منح نقاط الإحالة للمحيل
    منح_نقاط_الاحالة(معرف_المحيل, user_id, context.user_data['الاسم'])
    
    # إرسال إشعار للمحيل
    try:
        await context.bot.send_message(
            chat_id=معرف_المحيل,
            text=f"🎉 **إحالة ناجحة!**\n\n"
                 f"تم تسجيل مستخدم جديد برمز إحالتك!\n"
                 f"👤 المستخدم: {context.user_data['الاسم']}\n"
                 f"🎁 **المكافأة:** 100 نقطة\n"
                 f"💎 تم إضافتها لرصيدك تلقائياً"
        )
    except Exception as e:
        logger.error(f"خطأ في إرسال إشعار للمحيل: {e}")
    
    await update.message.reply_text(
        f"✅ **تم التسجيل بنجاح!**\n\n"
        f"👤 الطالب: {context.user_data['الاسم']}\n"
        f"🏫 المرحلة: {context.user_data['المرحلة_الدراسية']}\n"
        f"🌍 الدولة: {context.user_data['الدولة']}\n"
        f"🔑 **الرمز الفريد:** `{معرف_فريد}`\n\n"
        f"🎁 **مكافأة ترحيب:** 50 نقطة!\n"
        f"💎 رصيد النقاط: 50 نقطة\n\n"
        f"✅ **تم تفعيل رمز الإحالة بنجاح!**\n"
        f"👥 المحيل: {اسم_المحيل}\n\n"
        f"**يمكنك الآن:**\n"
        f"• كسب النقاط عبر الإحالات والمهام\n"
        f"• تحويل النقاط لريال سعودي\n"
        f"• شراء البريميم من رصيدك"
    )
    
    await عرض_القائمة_الرئيسية(update, context)
    return MAIN_MENU

async def skip_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    # حفظ البيانات في قاعدة البيانات بدون رمز إحالة
    معرف_فريد = str(uuid.uuid4()).split('-')[0].upper()
    context.user_data['معرف_التحقق_الفريد'] = معرف_فريد
    context.user_data['is_premium'] = 0 
    context.user_data['is_gift_premium'] = 0
    context.user_data['رصيد_النقاط'] = 50  # مكافأة ترحيب
    context.user_data['رصيد_الريال'] = 0
    context.user_data['is_manager'] = 0
    context.user_data['رمز_احالة_مستخدم'] = None
    
    حفظ_طالب(user_id, context.user_data['الاسم'], context.user_data['المرحلة_الدراسية'], 
              context.user_data['الدولة'], معرف_فريد)
    
    await update.message.reply_text(
        f"✅ **تم التسجيل بنجاح!**\n\n"
        f"👤 الطالب: {context.user_data['الاسم']}\n"
        f"🏫 المرحلة: {context.user_data['المرحلة_الدراسية']}\n"
        f"🌍 الدولة: {context.user_data['الدولة']}\n"
        f"🔑 **الرمز الفريد:** `{معرف_فريد}`\n\n"
        f"🎁 **مكافأة ترحيب:** 50 نقطة!\n"
        f"💎 رصيد النقاط: 50 نقطة\n\n"
        f"**يمكنك الآن:**\n"
        f"• كسب النقاط عبر الإحالات والمهام\n"
        f"• تحويل النقاط لريال سعودي\n"
        f"• شراء البريميم من رصيدك"
    )
    
    await عرض_القائمة_الرئيسية(update, context)
    return MAIN_MENU

async def عرض_القائمة_الرئيسية(update, context):
    المرحلة = context.user_data.get('المرحلة_الدراسية')
    الدولة = context.user_data.get('الدولة', 'السعودية')
    is_manager = context.user_data.get('is_manager', 0)
    
    keyboard = []
    
    # السطر 1: البحث
    keyboard.append([KeyboardButton("🔍 بحث عام")])
    
    # السطر 2: المعلومات
    keyboard.append([KeyboardButton("📊 إحصائياتي"), KeyboardButton("🔑 معرف التفعيل")])
    
    # السطر 3: النظام المالي
    keyboard.append([KeyboardButton("💎 نقاطي"), KeyboardButton("📤 تحويل نقاط")])
    keyboard.append([KeyboardButton("🔀 تحويل ريال"), KeyboardButton("🛒 شراء بريميم")])
    
    # السطر 4: المكافآت
    keyboard.append([KeyboardButton("👥 نظام الإحالة"), KeyboardButton("📋 المهام")])
    keyboard.append([KeyboardButton("🎬 مشاهدة إعلان"), KeyboardButton("📞 اتصل بالدعم")])
    
    # السطر 5: التحديث
    keyboard.append([KeyboardButton("🔄 تحديث القائمة")])
    
    # السطر 6: للمديرين فقط
    if is_manager:
        keyboard.append([KeyboardButton("🛠️ الدخول لوضع المدير")])
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # جلب الإعدادات الديناميكية 
    current_price = GLOBAL_CONFIG.get('premium_price', '10 ريال سعودي')

    رسالة = f"📚 **بوت منهج Ai - {المرحلة} ({الدولة})**\n\n"
    
    # معلومات الرصيد
    نقاط = context.user_data.get('رصيد_النقاط', 0)
    ريال = context.user_data.get('رصيد_الريال', 0)
    
    رسالة += f"💎 **رصيد النقاط:** {نقاط} نقطة\n"
    رسالة += f"💵 **رصيد الريال:** {ريال} ريال\n\n"
        
    رسالة += f"🧠 **البحث العام الجاهز**\n"
    رسالة += f"💡 اكتب سؤالك مباشرة وسأجيبك بإجابة منهجية شاملة\n\n"
    
    رسالة += f"{'🧠 الذكاء الاصطناعي: جاهز' if AI_جاهز else '⚠️ الوضع المحدود'}"
    
    is_premium = context.user_data.get('is_premium', 0)
    رسالة += f"\n✨ **Premium:** {'✅ مفعل' if is_premium else '❌ غير مفعل'}"
    
    if is_premium == 0:
        رسالة += (f"\n\n💎 **تفعيل Premium (إزالة الإعلانات):**\n"
                   f"💰 السعر: **{current_price}**\n"
                   f"💳 أو ادفع من رصيدك: 10 ريال")
        
    await update.message.reply_text(رسالة, reply_markup=reply_markup)

async def handle_main_menu(update: Update, context):
    user_input = update.message.text
    user_id = update.message.from_user.id
    
    # 0. التحقق من المنع بالإعلان (للبحث العام فقط)
    if user_input == "🔍 بحث عام":
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
        await update.message.reply_text("🔍 **وضع البحث العام**\n\nاكتب سؤالك وسأجيبك بإجابة تعليمية شاملة:")
        
    elif user_input == "🔑 معرف التفعيل":
        معرف_فريد = context.user_data.get('معرف_التحقق_الفريد', 'غير متوفر')
        is_premium = context.user_data.get('is_premium', 0)
        is_gift = context.user_data.get('is_gift_premium', 0)
        
        رسالة = f"🔑 **الرمز الفريد الخاص بك:**\n\n`{معرف_فريد}`\n\n"
        رسالة += f"✨ **حالة Premium:** {'✅ مفعل' if is_premium else '❌ غير مفعل'}"
        if is_gift:
            رسالة += f" (🎁 هدية)"
        await update.message.reply_text(رسالة)
        
    elif user_input == "📊 إحصائياتي":
        احصائيات = جلب_احصائيات_الطالب(user_id)
        if احصائيات:
            الاسم, المرحلة_الدراسية, عدد_الاسئلة, تاريخ_التسجيل, آخر_نشاط, معرف_فريد, is_premium, is_gift, نقاط, ريال, is_manager, احالات, رمز_احالة_مستخدم = احصائيات
            await update.message.reply_text(
                f"📊 **إحصائياتك الدراسية**\n\n"
                f"👤 **الطالب:** {الاسم}\n"
                f"🏫 **المرحلة:** {المرحلة_الدراسية}\n"
                f"❓ **عدد الأسئلة:** {عدد_الاسئلة}\n"
                f"💎 **النقاط:** {نقاط} نقطة\n"
                f"💵 **الريال:** {ريال} ريال\n"
                f"👥 **الإحالات الناجحة:** {احالات}\n"
                f"🕒 **آخر نشاط:** {آخر_نشاط[:16] if آخر_نشاط else 'غير متوفر'}"
            )
        else:
            await update.message.reply_text("❌ لا توجد بيانات لإحصائياتك")
            
    elif user_input == "🔄 تحديث القائمة":
        await update.message.reply_text("🔄 جاري تحديث القائمة...")
        معلومات_الطالب = جلب_طالب(user_id)
        if معلومات_الطالب:
             context.user_data.update({
                 'الاسم': معلومات_الطالب[0],
                 'المرحلة_الدراسية': معلومات_الطالب[1],
                 'الدولة': معلومات_الطالب[2],
                 'معرف_التحقق_الفريد': معلومات_الطالب[3],
                 'is_premium': معلومات_الطالب[4],
                 'is_gift_premium': معلومات_الطالب[5],
                 'رصيد_النقاط': معلومات_الطالب[6],
                 'رصيد_الريال': معلومات_الطالب[7],
                 'is_manager': معلومات_الطالب[8],
                 'احالات_ناجحة': معلومات_الطالب[9],
                 'رمز_احالة_مستخدم': معلومات_الطالب[10]
             })
        await عرض_القائمة_الرئيسية(update, context)
        
    elif user_input == "💎 نقاطي":
        نقاط = context.user_data.get('رصيد_النقاط', 0)
        ريال = context.user_data.get('رصيد_الريال', 0)
        await update.message.reply_text(
            f"💎 **رصيدك الحالي:**\n\n"
            f"🎁 **النقاط:** {نقاط} نقطة\n"
            f"💵 **الريال:** {ريال} ريال\n\n"
            f"💡 **طريقة الاستخدام:**\n"
            f"• 100 نقطة = 1 ريال سعودي\n"
            f"• يمكنك تحويل النقاط لريال\n"
            f"• يمكنك تحويل الريال لمستخدمين آخرين\n"
            f"• يمكنك شراء البريميم من رصيدك"
        )
        
    elif user_input == "📤 تحويل نقاط":
        await update.message.reply_text(
            "📤 **تحويل النقاط لريال سعودي**\n\n"
            "الحد الأدنى للتحويل: 100 نقطة\n"
            "المعادلة: 100 نقطة = 1 ريال\n\n"
            "الرجاء إدخال عدد النقاط التي تريد تحويلها:"
        )
        return CONVERT_POINTS
        
    elif user_input == "🔀 تحويل ريال":
        await update.message.reply_text(
            "🔀 **تحويل ريال لمستخدم آخر**\n\n"
            "الرجاء إدخال **الرمز الفريد** للمستلم:"
        )
        return TRANSFER_MONEY
        
    elif user_input == "🛒 شراء بريميم":
        return await شراء_بريميم_Handler(update, context)
        
    elif user_input == "👥 نظام الإحالة":
        رمز_احالة = context.user_data.get('معرف_التحقق_الفريد', 'غير متوفر')  # نفس الرمز الفريد
        احالات = context.user_data.get('احالات_ناجحة', 0)
        await update.message.reply_text(
            f"👥 **نظام الإحالة**\n\n"
            f"🔑 **رمز الإحالة الخاص بك:** `{رمز_احالة}`\n\n"
            f"🎁 **مكافأة الإحالة:** 100 نقطة لكل مستخدم جديد\n"
            f"📊 **إحالاتك الناجحة:** {احالات} إحالة\n\n"
            f"**طريقة الاستخدام:**\n"
            f"1. شارك الرمز أعلاه مع أصدقائك\n"
            f"2. عند تسجيلهم، يستخدمون الرمز في التسجيل\n"
            f"3. تحصل على 100 نقطة لكل إحالة ناجحة"
        )
        
    elif user_input == "📋 المهام":
        return await عرض_المهام(update, context)
        
    elif user_input == "🎬 مشاهدة إعلان":
        return await مشاهدة_إعلان(update, context)
        
    elif user_input == "📞 اتصل بالدعم":
        await update.message.reply_text(
            "📞 **مركز الدعم**\n\n"
            "الرجاء كتابة رسالتك للدعم وسيتم الرد عليك في أقرب وقت:"
        )
        return SUPPORT_MESSAGE
        
    elif user_input == "🛠️ الدخول لوضع المدير":
        if context.user_data.get('is_manager'):
            return await admin_menu(update, context)
        else:
            await update.message.reply_text("❌ ليس لديك صلاحيات المدير")
            
    else:
        await معالجة_سؤال(update, context, user_input)
    
    return MAIN_MENU 

async def معالجة_سؤال(update, context, سؤال):
    user_id = update.message.from_user.id
    اسم_الطالب = context.user_data.get('الاسم', 'يا طالب') 
    مرحلة_الطالب = context.user_data.get('المرحلة_الدراسية', 'الثانوية العامة') 
    دولة_الطالب = context.user_data.get('الدولة', 'السعودية') 
    
    # 1. المعالجة الخاصة لسؤال من برمجك/من سواك 
    question_lower = سؤال.lower().strip()
    if any(phrase in question_lower for phrase in ["من سواك", "من برمجك", "من طورك", "مصممك"]):
         await update.message.reply_text(
             f"👋🏼 أنا بوت منهج Ai، تم تطويري وبرمجتي بواسطة **مصعب فهد**."
         )
         return MAIN_MENU

    # 2. تسجيل السؤال والبدء في المعالجة العادية
    تسجيل_سؤال(user_id, سؤال, "عام")
    await update.message.reply_text("🧠 **جاري البحث والمعالجة...**")
    
    try:
        if not AI_جاهز: 
            await update.message.reply_text("❌ الذكاء الاصطناعي غير متاح حالياً")
            return MAIN_MENU
        
        # برومبت مُحسن وشامل
        prompt = (
            f"أنت معلم خبير في المنهج {دولة_الطالب} للمرحلة {مرحلة_الطالب}. "
            f"اسم الطالب هو {اسم_الطالب}. "
            f"أنت تعمل ضمن بوت تعليمي على تطبيق تيليجرام (Telegram Educational Bot) ومهامك الرئيسية هي مساعدة الطلاب تعليمياً. "
            f"مهمتك هي الإجابة على استفسارات الطلاب التعليمية بأعلى درجة من الدقة والموثوقية المنهجية، "
            f"مع التركيز على المنهج الدراسي لدولة {دولة_الطالب} والمرحلة {مرحلة_الطالب}. "
            f"أجب على السؤال التالي بإجابة تعليمية منهجية دقيقة:\n\n"
            f"السؤال: {سؤال}"
        )

        response = model.generate_content(prompt)
        إجابة = response.text
        await update.message.reply_text(f"🎯 **الإجابة التعليمية يا {اسم_الطالب}:**\n\n{إجابة}")
        
        await update.message.reply_text("💡 هل لديك سؤال آخر؟ يمكنك كتابته مباشرة، أو اختر **'🔄 تحديث القائمة'** للعودة للقائمة الرئيسية.")
            
    except Exception as e:
        logger.error(f"❌ خطأ فادح في Gemini: {e}")
        await update.message.reply_text(f"❌ **حدث خطأ في المعالجة**. جرب سؤالاً آخر.")
    
    return MAIN_MENU 

# Handlers للنقاط والتحويلات
async def convert_points_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        نقاط = int(update.message.text)
        user_id = update.message.from_user.id
        
        ناجح, رسالة = تحويل_نقاط_لريال(user_id, نقاط)
        
        if ناجح:
            # تحديث البيانات
            معلومات_الطالب = جلب_طالب(user_id)
            if معلومات_الطالب:
                context.user_data['رصيد_النقاط'] = معلومات_الطالب[6]
                context.user_data['رصيد_الريال'] = معلومات_الطالب[7]
            
            await update.message.reply_text(f"✅ {رسالة}\n\n💎 رصيد النقاط الجديد: {context.user_data['رصيد_النقاط']}\n💵 رصيد الريال الجديد: {context.user_data['رصيد_الريال']}")
        else:
            await update.message.reply_text(f"❌ {رسالة}")
            
    except ValueError:
        await update.message.reply_text("❌ الرجاء إدخال رقم صحيح")
        return CONVERT_POINTS
    
    await عرض_القائمة_الرئيسية(update, context)
    return MAIN_MENU

async def transfer_money_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    رمز_المستلم = update.message.text.strip()
    context.user_data['رمز_المستلم'] = رمز_المستلم
    
    await update.message.reply_text("💸 الرجاء إدخال المبلغ بالريال الذي تريد تحويله:")
    return TRANSFER_MONEY + 1

async def transfer_money_amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        مبلغ = int(update.message.text)
        user_id = update.message.from_user.id
        رمز_المستلم = context.user_data.get('رمز_المستلم')
        
        if مبلغ <= 0:
            await update.message.reply_text("❌ المبلغ يجب أن يكون أكبر من الصفر")
            return TRANSFER_MONEY
            
        ناجح, رسالة = تحويل_ريال(user_id, رمز_المستلم, مبلغ)
        
        if ناجح:
            مستلم_id, اسم_المستلم = رسالة
            
            # تحديث بيانات المرسل
            معلومات_الطالب = جلب_طالب(user_id)
            if معلومات_الطالب:
                context.user_data['رصيد_الريال'] = معلومات_الطالب[7]
            
            # إرسال إشعار للمستلم
            try:
                await context.bot.send_message(
                    chat_id=مستلم_id,
                    text=f"🎉 **تحويل وارد**\n\n"
                         f"استلمت {مبلغ} ريال من {context.user_data['الاسم']}\n"
                         f"💳 رصيدك الجديد: {معلومات_الطالب[7] + مبلغ if معلومات_الطالب else مبلغ} ريال"
                )
            except Exception as e:
                logger.error(f"خطأ في إرسال إشعار للمستلم: {e}")
            
            await update.message.reply_text(
                f"✅ **تم التحويل بنجاح!**\n\n"
                f"💸 **المبلغ:** {مبلغ} ريال\n"
                f"👤 **المستلم:** {اسم_المستلم}\n"
                f"💳 **رصيدك الجديد:** {context.user_data['رصيد_الريال']} ريال"
            )
        else:
            await update.message.reply_text(f"❌ {رسالة}")
            
    except ValueError:
        await update.message.reply_text("❌ الرجاء إدخال رقم صحيح")
        return TRANSFER_MONEY + 1
    
    context.user_data.pop('رمز_المستلم', None)
    await عرض_القائمة_الرئيسية(update, context)
    return MAIN_MENU

async def شراء_بريميم_Handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    if context.user_data.get('is_premium'):
        await update.message.reply_text("✅ أنت مشترك بالفعل في البريميم!")
        return MAIN_MENU
        
    ناجح, رسالة = شراء_بريميم(user_id)
    
    if ناجح:
        # تحديث البيانات
        معلومات_الطالب = جلب_طالب(user_id)
        if معلومات_الطالب:
            context.user_data['is_premium'] = 1
            context.user_data['رصيد_الريال'] = معلومات_الطالب[7]
        
        await update.message.reply_text(
            f"🎉 **تم شراء البريميم بنجاح!**\n\n"
            f"✨ **مميزات البريميم:**\n"
            f"• إزالة الإعلانات تماماً\n"
            f"• إجابات أسرع\n"
            f"• دعم مميز\n\n"
            f"💳 **رصيدك الجديد:** {context.user_data['رصيد_الريال']} ريال"
        )
    else:
        await update.message.reply_text(f"❌ {رسالة}")
    
    await عرض_القائمة_الرئيسية(update, context)
    return MAIN_MENU

# Handlers للمهام
async def عرض_المهام(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    مهام = جلب_المهام_المتاحة(user_id)
    
    if not مهام:
        await update.message.reply_text("📭 لا توجد مهام متاحة حالياً.")
        return MAIN_MENU
    
    keyboard = []
    for مهمة in مهام:
        مهمة_id, رابط, وصف, نقاط = مهمة
        keyboard.append([KeyboardButton(f"📋 {وصف} - {نقاط} نقطة")])
        context.user_data[f'مهمة_{مهمة_id}'] = مهمة
    
    keyboard.append([KeyboardButton("🔙 العودة للقائمة الرئيسية")])
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "📋 **المهام المتاحة:**\n\n"
        "اختر المهمة التي تريد إكمالها:",
        reply_markup=reply_markup
    )
    return TASKS_MENU

async def handle_tasks_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    
    if user_input == "🔙 العودة للقائمة الرئيسية":
        await عرض_القائمة_الرئيسية(update, context)
        return MAIN_MENU
    
    # البحث عن المهمة المختارة
    for key, value in context.user_data.items():
        if key.startswith('مهمة_') and user_input.startswith(f"📋 {value[2]}"):
            مهمة_id = key.split('_')[1]
            await إكمال_مهمة_Handler(update, context, int(مهمة_id))
            return MAIN_MENU
    
    await update.message.reply_text("❌ لم يتم التعرف على المهمة")
    return TASKS_MENU

async def إكمال_مهمة_Handler(update: Update, context: ContextTypes.DEFAULT_TYPE, مهمة_id):
    user_id = update.message.from_user.id
    ناجح, نقاط = إكمال_مهمة(user_id, مهمة_id)
    
    if ناجح:
        # تحديث البيانات
        معلومات_الطالب = جلب_طالب(user_id)
        if معلومات_الطالب:
            context.user_data['رصيد_النقاط'] = معلومات_الطالب[6]
        
        await update.message.reply_text(
            f"✅ **تم إكمال المهمة بنجاح!**\n\n"
            f"🎁 **المكافأة:** {نقاط} نقطة\n"
            f"💎 **رصيد النقاط الجديد:** {context.user_data['رصيد_النقاط']} نقطة"
        )
    else:
        await update.message.reply_text("❌ حدث خطأ في إكمال المهمة")
    
    await عرض_القائمة_الرئيسية(update, context)
    return MAIN_MENU

async def مشاهدة_إعلان(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    keyboard = [
        [InlineKeyboardButton("🌐 رابط الإعلان (اضغط هنا)", url=AD_LINK)],
        [InlineKeyboardButton("✅ تأكيد المشاهدة", callback_data=AD_CONFIRM_VIEW)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🎬 **مشاهدة إعلان**\n\n"
        "شاهد الإعلان لمدة 5 ثوانٍ واحصل على 5 نقاط!\n\n"
        "**الخطوات:**\n"
        "1. اضغط على الرابط وانتظر 5 ثوانٍ\n"
        "2. اضغط على زر التأكيد\n"
        "3. احصل على 5 نقاط مكافأة",
        reply_markup=reply_markup
    )

# Handlers للدعم
async def support_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    رسالة = update.message.text
    user_id = update.message.from_user.id
    
    if إرسال_رسالة_دعم(user_id, رسالة):
        await update.message.reply_text(
            "✅ **تم إرسال رسالتك للدعم**\n\n"
            "سيتم الرد عليك في أقرب وقت ممكن.\n"
            "شكراً لاتصالك بنا! 📞"
        )
    else:
        await update.message.reply_text("❌ حدث خطأ في إرسال الرسالة")
    
    await عرض_القائمة_الرئيسية(update, context)
    return MAIN_MENU

# دوال لوحة المدير المحدثة
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
        return MAIN_MENU

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة المدير المحدثة"""
    keyboard = [
        [KeyboardButton("👥 عرض كل المستخدمين"), KeyboardButton("✨ عرض مشتركي بريميم")],
        [KeyboardButton("🚫 عرض غير المشتركين"), KeyboardButton("💎 إحصائيات النقاط")],
        [KeyboardButton("📋 إدارة المهام"), KeyboardButton("🛒 طلبات البريميم")],
        [KeyboardButton("🔑 تفعيل بريميم لرمز"), KeyboardButton("🚫 إلغاء بريميم لرمز")],
        [KeyboardButton("🎁 تفعيل بريميم هدية"), KeyboardButton("🛠️ تعيين مدير جديد")],
        [KeyboardButton("📣 مسابقات (إرسال إشعار للكل)"), KeyboardButton("💵 تغيير سعر البوت")],
        [KeyboardButton("📞 إدارة الدعم"), KeyboardButton("💰 الرصيد المفتوح")],
        [KeyboardButton("🔙 العودة للقائمة الرئيسية")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        f"🛠️ **قائمة المدير - منهج Ai**\n\n"
        f"🧠 **حالة الذكاء الاصطناعي:** {'✅ جاهز' if AI_جاهز else '❌ غير جاهز'}\n\n"
        f"اختر الإجراء المطلوب:", 
        reply_markup=reply_markup
    )
    return ADMIN_MENU

async def handle_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة اختيارات قائمة المدير"""
    user_input = update.message.text
    
    if user_input == "👥 عرض كل المستخدمين":
        return await display_all_users_info(update, context)
        
    elif user_input == "✨ عرض مشتركي بريميم":
        return await display_premium_users_info(update, context)
        
    elif user_input == "🚫 عرض غير المشتركين":
        return await display_non_premium_users_info(update, context)
        
    elif user_input == "💎 إحصائيات النقاط":
        return await عرض_إحصائيات_النقاط(update, context)
    
    elif user_input == "📋 إدارة المهام":
        return await إدارة_المهام(update, context)
    
    elif user_input == "🛒 طلبات البريميم":
        return await طلبات_البريميم(update, context)
    
    elif user_input == "🔑 تفعيل بريميم لرمز":
        await update.message.reply_text("الرجاء إدخال **الرمز الفريد** للطالب المطلوب تفعيله:")
        return PREMIUM_ID_ENTRY
        
    elif user_input == "🚫 إلغاء بريميم لرمز":
        await update.message.reply_text("الرجاء إدخال **الرمز الفريد** للطالب المطلوب **إلغاء** تفعيله:")
        return PREMIUM_DEACTIVATE_ID_ENTRY
        
    elif user_input == "🎁 تفعيل بريميم هدية":
        await update.message.reply_text("🎁 **تفعيل بريميم هدية**\n\nالرجاء إدخال **الرمز الفريد** للطالب المطلوب منحه الهدية:")
        return GIFT_PREMIUM_ENTRY
        
    elif user_input == "🛠️ تعيين مدير جديد":
        await update.message.reply_text("🛠️ **تعيين مدير جديد**\n\nالرجاء إدخال الرمز الفريد للمستخدم:")
        return ADD_MANAGER
    
    elif user_input == "📣 مسابقات (إرسال إشعار للكل)":
        await update.message.reply_text("📣 **وضع الإشعار الجماعي**\n\nالرجاء كتابة **الرسالة الكاملة** التي تريد إرسالها لجميع المستخدمين:")
        return BROADCAST_MESSAGE_ENTRY
        
    elif user_input == "💵 تغيير سعر البوت": 
        current_price = GLOBAL_CONFIG.get('premium_price', '10 ريال سعودي')
        await update.message.reply_text(
            f"💵 **تغيير سعر البوت**\n\n"
            f"السعر الحالي هو: **{current_price}**\n"
            f"الرجاء إدخال السعر الجديد كاملاً (مثال: 50 دولار أمريكي، 100 جنيه مصري):"
        )
        return CHANGE_PRICE_ENTRY

    elif user_input == "📞 إدارة الدعم":
        return await إدارة_الدعم(update, context)
    
    elif user_input == "💰 الرصيد المفتوح":
        return await الرصيد_المفتوح(update, context)
        
    elif user_input == "🔙 العودة للقائمة الرئيسية":
        معلومات_الطالب = جلب_طالب(update.message.from_user.id)
        if معلومات_الطالب:
             context.user_data.update({
                 'الاسم': معلومات_الطالب[0],
                 'المرحلة_الدراسية': معلومات_الطالب[1],
                 'الدولة': معلومات_الطالب[2],
                 'معرف_التحقق_الفريد': معلومات_الطالب[3],
                 'is_premium': معلومات_الطالب[4],
                 'is_gift_premium': معلومات_الطالب[5],
                 'رصيد_النقاط': معلومات_الطالب[6],
                 'رصيد_الريال': معلومات_الطالب[7],
                 'is_manager': معلومات_الطالب[8],
                 'احالات_ناجحة': معلومات_الطالب[9],
                 'رمز_احالة_مستخدم': معلومات_الطالب[10]
             })

        context.user_data['is_admin'] = False
        await update.message.reply_text("↩️ تم تسجيل الخروج من وضع المدير.")
        await عرض_القائمة_الرئيسية(update, context) 
        return MAIN_MENU 
    
    else:
        await update.message.reply_text("اختيار غير صالح. الرجاء الاختيار من الأزرار.")
        return ADMIN_MENU

# دوال المدير الجديدة
async def display_all_users_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض أسماء ورموز تفعيل كل مستخدمي البوت"""
    الطلاب = جلب_جميع_الطلاب()
    
    إذا_لم_يوجد = "❌ لا يوجد طلاب مسجلين."
    
    if الطلاب:
        رسالة = f"👥 **قائمة جميع المستخدمين:** (إجمالي: {len(الطلاب)} مستخدم)\n\n"
        
        for الاسم, الرمز, المرحلة, معرف_المستخدم, is_premium, is_gift in الطلاب:
            حالة = "🎁" if is_gift else "✅" if is_premium else "❌"
            رسالة += f"👤 {الاسم} | {الرمز} | {المرحلة} | {حالة}\n"
            
        await update.message.reply_text(رسالة)
    else:
        await update.message.reply_text(إذا_لم_يوجد)
        
    return ADMIN_MENU

async def display_premium_users_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض أسماء ورموز تفعيل المشتركين البريميم فقط"""
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('SELECT الاسم, معرف_التحقق_الفريد, معرف_المستخدم, is_gift_premium FROM الطلاب WHERE is_premium = 1')
        المشتركون = cursor.fetchall()
        conn.close()
        
        إذا_لم_يوجد = "❌ لا يوجد مشتركون حالياً في Premium."
        
        if المشتركون:
            رسالة = f"✨ **قائمة مشتركي Premium:** (إجمالي: {len(المشتركون)} مشترك)\n\n"
            
            for الاسم, الرمز, معرف_المستخدم, is_gift in المشتركون:
                نوع = "🎁 هدية" if is_gift else "💳 مدفوع"
                رسالة += f"👤 {الاسم} | {الرمز} | {نوع}\n"
                
            await update.message.reply_text(رسالة)
        else:
            await update.message.reply_text(إذا_لم_يوجد)
            
    except Exception as e:
        logger.error(f"خطأ في جلب المشتركين البريميم: {e}")
        await update.message.reply_text("❌ حدث خطأ في جلب البيانات")
        
    return ADMIN_MENU

async def display_non_premium_users_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض المستخدمين غير المشتركين في البريميم"""
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('SELECT الاسم, معرف_التحقق_الفريد, معرف_المستخدم FROM الطلاب WHERE is_premium = 0')
        غير_المشتركين = cursor.fetchall()
        conn.close()
        
        إذا_لم_يوجد = "✅ جميع المستخدمين مشتركون في Premium."
        
        if غير_المشتركين:
            رسالة = f"🚫 **قائمة غير المشتركين في Premium:** (إجمالي: {len(غير_المشتركين)} مستخدم)\n\n"
            
            for الاسم, الرمز, معرف_المستخدم in غير_المشتركين:
                رسالة += f"👤 {الاسم} | {الرمز}\n"
                
            await update.message.reply_text(رسالة)
        else:
            await update.message.reply_text(إذا_لم_يوجد)
            
    except Exception as e:
        logger.error(f"خطأ في جلب غير المشتركين: {e}")
        await update.message.reply_text("❌ حدث خطأ في جلب البيانات")
        
    return ADMIN_MENU

async def عرض_إحصائيات_النقاط(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        
        # إجمالي النقاط في النظام
        cursor.execute('SELECT SUM(رصيد_النقاط), SUM(رصيد_الريال) FROM الطلاب')
        إجمالي_النقاط, إجمالي_الريال = cursor.fetchone()
        
        # أعلى 5 مستخدمين
        cursor.execute('''
            SELECT الاسم, رصيد_النقاط, رصيد_الريال 
            FROM الطلاب 
            ORDER BY رصيد_النقاط DESC 
            LIMIT 5
        ''')
        أعلى_المستخدمين = cursor.fetchall()
        
        conn.close()
        
        رسالة = f"📊 **إحصائيات النقاط**\n\n"
        رسالة += f"💰 **إجمالي النقاط في النظام:** {إجمالي_النقاط or 0} نقطة\n"
        رسالة += f"💵 **إجمالي الريال في النظام:** {إجمالي_الريال or 0} ريال\n\n"
        رسالة += f"🏆 **أعلى 5 مستخدمين:**\n"
        
        for i, (اسم, نقاط, ريال) in enumerate(أعلى_المستخدمين, 1):
            رسالة += f"{i}. {اسم} - {نقاط} نقطة - {ريال} ريال\n"
        
        await update.message.reply_text(رسالة)
        
    except Exception as e:
        logger.error(f"خطأ في عرض إحصائيات النقاط: {e}")
        await update.message.reply_text("❌ حدث خطأ في جلب الإحصائيات")
    
    return ADMIN_MENU

async def إدارة_المهام(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("➕ إضافة مهمة جديدة")],
        [KeyboardButton("📋 عرض المهام الحالية")],
        [KeyboardButton("🔙 العودة لقائمة المدير")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text("📋 **إدارة المهام**\n\nاختر الإجراء المطلوب:", reply_markup=reply_markup)
    return ADMIN_MANAGE_TASKS

async def handle_manage_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    
    if user_input == "➕ إضافة مهمة جديدة":
        await update.message.reply_text("➕ **إضافة مهمة جديدة**\n\nالرجاء إدخال رابط المهمة:")
        return ADD_TASK
        
    elif user_input == "📋 عرض المهام الحالية":
        return await عرض_المهام_الحالية(update, context)
        
    elif user_input == "🔙 العودة لقائمة المدير":
        return await admin_menu(update, context)
    
    else:
        await update.message.reply_text("❌ اختيار غير صالح")
        return ADMIN_MANAGE_TASKS

async def add_task_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    رابط = update.message.text
    context.user_data['رابط_المهمة'] = رابط
    
    await update.message.reply_text("📝 الرجاء إدخال وصف المهمة:")
    return ADD_TASK + 1

async def add_task_description_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    وصف = update.message.text
    context.user_data['وصف_المهمة'] = وصف
    
    await update.message.reply_text("💎 الرجاء إدخال عدد النقاط للمهمة:")
    return ADD_TASK + 2

async def add_task_points_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        نقاط = int(update.message.text)
        رابط = context.user_data['رابط_المهمة']
        وصف = context.user_data['وصف_المهمة']
        
        if إضافة_مهمة(رابط, وصف, نقاط):
            await update.message.reply_text(f"✅ **تم إضافة المهمة بنجاح!**\n\n📋 {وصف}\n💎 {نقاط} نقطة")
        else:
            await update.message.reply_text("❌ فشل في إضافة المهمة")
            
    except ValueError:
        await update.message.reply_text("❌ الرجاء إدخال رقم صحيح للنقاط")
        return ADD_TASK + 2
    
    context.user_data.pop('رابط_المهمة', None)
    context.user_data.pop('وصف_المهمة', None)
    return await إدارة_المهام(update, context)

async def عرض_المهام_الحالية(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('SELECT مهمة_id, رابط, وصف, نقاط FROM المهام WHERE is_active = 1')
        مهام = cursor.fetchall()
        conn.close()
        
        if not مهام:
            await update.message.reply_text("📭 لا توجد مهام حالياً.")
            return ADMIN_MANAGE_TASKS
        
        رسالة = "📋 **المهام الحالية:**\n\n"
        for مهمة_id, رابط, وصف, نقاط in مهام:
            رسالة += f"🔹 **{وصف}**\n"
            رسالة += f"🔗 الرابط: {رابط}\n"
            رسالة += f"💎 النقاط: {نقاط}\n"
            رسالة += f"🆔 الرقم: {مهمة_id}\n\n"
        
        await update.message.reply_text(رسالة)
        
    except Exception as e:
        logger.error(f"خطأ في عرض المهام الحالية: {e}")
        await update.message.reply_text("❌ حدث خطأ في جلب المهام")
    
    return ADMIN_MANAGE_TASKS

async def طلبات_البريميم(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛒 **طلبات البريميم**\n\n"
        "حالياً لا توجد طلبات بريميم معلقة.\n"
        "سيظهر هنا أي مستخدم يحاول شراء البريميم ولكن رصيده غير كافي."
    )
    return ADMIN_MENU

async def add_manager_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    رمز_فريد = update.message.text.strip().upper()
    
    # التحقق من وجود المستخدم
    مستخدم = التحقق_من_رمز_الاحالة(رمز_فريد)
    
    if not مستخدم:
        await update.message.reply_text("❌ لم يتم العثور على مستخدم بهذا الرمز الفريد. الرجاء المحاولة مرة أخرى:")
        return ADD_MANAGER
    
    معرف_المستخدم, اسم_المستخدم = مستخدم
    
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('UPDATE الطلاب SET is_manager = 1 WHERE معرف_المستخدم = ?', (معرف_المستخدم,))
        conn.commit()
        conn.close()
        
        # إرسال إشعار للمستخدم المعين
        try:
            await context.bot.send_message(
                chat_id=معرف_المستخدم,
                text=f"🎉 **تهانينا!**\n\n"
                     f"تم تعيينك كمدير في بوت منهج Ai!\n"
                     f"الآن يمكنك الدخول لوضع المدير من القائمة الرئيسية."
            )
        except Exception as e:
            logger.error(f"خطأ في إرسال إشعار للمدير الجديد: {e}")
        
        await update.message.reply_text(f"✅ **تم تعيين {اسم_المستخدم} كمدير بنجاح!**")
        
    except Exception as e:
        logger.error(f"خطأ في تعيين المدير: {e}")
        await update.message.reply_text("❌ حدث خطأ في تعيين المدير")
    
    return await admin_menu(update, context)

async def إدارة_الدعم(update: Update, context: ContextTypes.DEFAULT_TYPE):
    رسائل = جلب_رسائل_الدعم()
    
    if not رسائل:
        await update.message.reply_text("📭 لا توجد رسائل دعم جديدة.")
        return ADMIN_MENU
    
    keyboard = []
    for دعم_id, معرف_المستخدم, اسم, رسالة, تاريخ in رسائل:
        keyboard.append([KeyboardButton(f"📩 {اسم} - {رسالة[:30]}...")])
        context.user_data[f'دعم_{دعم_id}'] = (دعم_id, معرف_المستخدم, اسم, رسالة)
    
    keyboard.append([KeyboardButton("🔙 العودة لقائمة المدير")])
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        f"📞 **رسائل الدعم الجديدة** ({len(رسائل)} رسالة)\n\n"
        f"اختر الرسالة للرد عليها:",
        reply_markup=reply_markup
    )
    return ADMIN_SUPPORT_MENU

async def handle_support_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    
    if user_input == "🔙 العودة لقائمة المدير":
        return await admin_menu(update, context)
    
    # البحث عن الرسالة المختارة
    for key, value in context.user_data.items():
        if key.startswith('دعم_') and user_input.startswith(f"📩 {value[2]}"):
            دعم_id, معرف_المستخدم, اسم, رسالة = value
            context.user_data['دعم_محدد'] = (دعم_id, معرف_المستخدم, اسم)
            
            await update.message.reply_text(
                f"📩 **رسالة من {اسم}:**\n\n"
                f"{رسالة}\n\n"
                f"الرجاء كتابة الرد:"
            )
            return ADMIN_REPLY_SUPPORT
    
    await update.message.reply_text("❌ لم يتم التعرف على الرسالة")
    return ADMIN_SUPPORT_MENU

async def reply_support_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    الرد = update.message.text
    دعم_محدد = context.user_data.get('دعم_محدد')
    
    if not دعم_محدد:
        await update.message.reply_text("❌ لم يتم تحديد رسالة دعم")
        return ADMIN_SUPPORT_MENU
    
    دعم_id, معرف_المستخدم, اسم = دعم_محدد
    
    ناجح, معرف_المستخدم = الرد_على_دعم(دعم_id, الرد)
    
    if ناجح:
        # إرسال الرد للمستخدم
        try:
            await context.bot.send_message(
                chat_id=معرف_المستخدم,
                text=f"📞 **رد الدعم:**\n\n"
                     f"{الرد}\n\n"
                     f"شكراً لاتصالك بنا! 🙏"
            )
        except Exception as e:
            logger.error(f"خطأ في إرسال الرد للمستخدم: {e}")
        
        await update.message.reply_text("✅ **تم إرسال الرد بنجاح!**")
    else:
        await update.message.reply_text("❌ فشل في إرسال الرد")
    
    context.user_data.pop('دعم_محدد', None)
    return await admin_menu(update, context)

async def الرصيد_المفتوح(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("🎁 منح نقاط لمستخدم")],
        [KeyboardButton("💸 منح ريال لمستخدم")],
        [KeyboardButton("🔙 العودة لقائمة المدير")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text("💰 **الرصيد المفتوح**\n\nاختر الإجراء المطلوب:", reply_markup=reply_markup)
    return ADMIN_GIVE_POINTS

async def handle_give_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    
    if user_input == "🎁 منح نقاط لمستخدم":
        await update.message.reply_text("🎁 **منح نقاط لمستخدم**\n\nالرجاء إدخال الرمز الفريد للمستخدم:")
        return ADMIN_GIVE_POINTS + 1
        
    elif user_input == "💸 منح ريال لمستخدم":
        await update.message.reply_text("💸 **منح ريال لمستخدم**\n\nالرجاء إدخال الرمز الفريد للمستخدم:")
        return ADMIN_GIVE_MONEY
        
    elif user_input == "🔙 العودة لقائمة المدير":
        return await admin_menu(update, context)
    
    else:
        await update.message.reply_text("❌ اختيار غير صالح")
        return ADMIN_GIVE_POINTS

async def give_points_user_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    رمز_فريد = update.message.text.strip().upper()
    
    # التحقق من وجود المستخدم
    مستخدم = التحقق_من_رمز_الاحالة(رمز_فريد)
    
    if not مستخدم:
        await update.message.reply_text("❌ لم يتم العثور على مستخدم بهذا الرمز الفريد. الرجاء المحاولة مرة أخرى:")
        return ADMIN_GIVE_POINTS + 1
    
    context.user_data['مستخدم_لمنح_النقاط'] = مستخدم
    await update.message.reply_text("💎 الرجاء إدخال عدد النقاط التي تريد منحها:")
    return ADMIN_GIVE_POINTS + 2

async def give_points_amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        نقاط = int(update.message.text)
        مستخدم = context.user_data.get('مستخدم_لمنح_النقاط')
        
        if not مستخدم:
            await update.message.reply_text("❌ لم يتم تحديد مستخدم")
            return ADMIN_GIVE_POINTS
            
        معرف_المستخدم, اسم_المستخدم = مستخدم
        
        if إضافة_نقاط(معرف_المستخدم, نقاط, "هدية من الإدارة"):
            # إرسال إشعار للمستخدم
            try:
                await context.bot.send_message(
                    chat_id=معرف_المستخدم,
                    text=f"🎉 **هدية من الإدارة!**\n\n"
                         f"لقد حصلت على {نقاط} نقطة هدية من الإدارة!\n"
                         f"💎 تم إضافتها لرصيدك تلقائياً"
                )
            except Exception as e:
                logger.error(f"خطأ في إرسال إشعار للمستخدم: {e}")
            
            await update.message.reply_text(f"✅ **تم منح {نقاط} نقطة لـ {اسم_المستخدم} بنجاح!**")
        else:
            await update.message.reply_text("❌ فشل في منح النقاط")
            
    except ValueError:
        await update.message.reply_text("❌ الرجاء إدخال رقم صحيح")
        return ADMIN_GIVE_POINTS + 2
    
    context.user_data.pop('مستخدم_لمنح_النقاط', None)
    return await admin_menu(update, context)

async def give_money_user_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    رمز_فريد = update.message.text.strip().upper()
    
    # التحقق من وجود المستخدم
    مستخدم = التحقق_من_رمز_الاحالة(رمز_فريد)
    
    if not مستخدم:
        await update.message.reply_text("❌ لم يتم العثور على مستخدم بهذا الرمز الفريد. الرجاء المحاولة مرة أخرى:")
        return ADMIN_GIVE_MONEY
    
    context.user_data['مستخدم_لمنح_الريال'] = مستخدم
    await update.message.reply_text("💸 الرجاء إدخال المبلغ بالريال الذي تريد منحه:")
    return ADMIN_GIVE_MONEY + 1

async def give_money_amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        مبلغ = int(update.message.text)
        مستخدم = context.user_data.get('مستخدم_لمنح_الريال')
        
        if not مستخدم:
            await update.message.reply_text("❌ لم يتم تحديد مستخدم")
            return ADMIN_GIVE_MONEY
            
        معرف_المستخدم, اسم_المستخدم = مستخدم
        
        # تنفيذ منح الريال
        try:
            conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute('UPDATE الطلاب SET رصيد_الريال = رصيد_الريال + ? WHERE معرف_المستخدم = ?', (مبلغ, معرف_المستخدم))
            conn.commit()
            conn.close()
            
            # إرسال إشعار للمستخدم
            try:
                await context.bot.send_message(
                    chat_id=معرف_المستخدم,
                    text=f"🎉 **هدية من الإدارة!**\n\n"
                         f"لقد حصلت على {مبلغ} ريال هدية من الإدارة!\n"
                         f"💳 تم إضافتها لرصيدك تلقائياً"
                )
            except Exception as e:
                logger.error(f"خطأ في إرسال إشعار للمستخدم: {e}")
            
            await update.message.reply_text(f"✅ **تم منح {مبلغ} ريال لـ {اسم_المستخدم} بنجاح!**")
        except Exception as e:
            logger.error(f"خطأ في منح الريال: {e}")
            await update.message.reply_text("❌ فشل في منح الريال")
            
    except ValueError:
        await update.message.reply_text("❌ الرجاء إدخال رقم صحيح")
        return ADMIN_GIVE_MONEY + 1
    
    context.user_data.pop('مستخدم_لمنح_الريال', None)
    return await admin_menu(update, context)

# Handlers للمدير الأساسية
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

async def activate_gift_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تفعيل بريميم هدية"""
    premium_id = update.message.text.strip()
    
    if تفعيل_بريميم_هدية(premium_id):
        await update.message.reply_text(f"✅ **تم منح الهدية بنجاح!**\n\nتم تفعيل حالة Premium كهدية للرمز: `{premium_id}`")
    else:
        await update.message.reply_text(f"❌ **فشل منح الهدية!**\n\nلم يتم العثور على طالب يملك الرمز: `{premium_id}`")
        
    return await admin_menu(update, context)

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

async def set_new_price_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """حفظ السعر الجديد وتحديث الإعدادات العالمية"""
    new_price = update.message.text.strip()
    
    global GLOBAL_CONFIG
    
    GLOBAL_CONFIG['premium_price'] = new_price
    save_config(GLOBAL_CONFIG)
    
    await update.message.reply_text(f"✅ **تم تحديث سعر البوت بنجاح!**\n\nالسعر الجديد هو: **{new_price}**")
    return await admin_menu(update, context)

async def cancel(update: Update, context):
    await update.message.reply_text('تم إلغاء المحادثة.\nيمكنك البدء مرة أخرى بـ /start')
    return ConversationHandler.END

def main():
    print("🔍 جاري فحص النظام...")
    
    # إظهار حالة التوكن عند التشغيل
    if MAIN_GEMINI_TOKEN:
        print(f"✅ تم تحميل التوكن الرئيسي ({len(MAIN_GEMINI_TOKEN)} حرف)")
    else:
        print("⚠️ لم يتم إضافة توكن رئيسي. الرجاء إضافته من لوحة المدير.")
    
    print(f"🚀 بوت منهج Ai جاهز للتشغيل!")
    
    try:
        app = Application.builder().token(BOT_TOKEN).build()
        
        # إعداد محادثة التسجيل
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)], 
            states={
                NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
                STAGE_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_stage)],
                COUNTRY_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_country)],
                REFERRAL_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_referral_code)],
                MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu)],
                
                # حالات جديدة للنقاط والدعم
                CONVERT_POINTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, convert_points_handler)],
                TRANSFER_MONEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, transfer_money_handler)],
                TRANSFER_MONEY + 1: [MessageHandler(filters.TEXT & ~filters.COMMAND, transfer_money_amount_handler)],
                SUPPORT_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, support_message_handler)],
                TASKS_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tasks_menu)],
                
                # Admin States
                ADMIN_PASSWORD_ENTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_admin_password)],
                ADMIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_menu)],
                PREMIUM_ID_ENTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, activate_premium)],
                PREMIUM_DEACTIVATE_ID_ENTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, deactivate_premium)],
                GIFT_PREMIUM_ENTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, activate_gift_premium)],
                BROADCAST_MESSAGE_ENTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, send_broadcast_message)],
                CHANGE_PRICE_ENTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_new_price_value)],
                ADMIN_SUPPORT_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_support_messages)],
                ADMIN_REPLY_SUPPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, reply_support_handler)],
                ADMIN_MANAGE_TASKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_manage_tasks)],
                ADD_TASK: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_task_handler)],
                ADD_TASK + 1: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_task_description_handler)],
                ADD_TASK + 2: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_task_points_handler)],
                ADD_MANAGER: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_manager_handler)],
                ADMIN_GIVE_POINTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_give_points)],
                ADMIN_GIVE_POINTS + 1: [MessageHandler(filters.TEXT & ~filters.COMMAND, give_points_user_handler)],
                ADMIN_GIVE_POINTS + 2: [MessageHandler(filters.TEXT & ~filters.COMMAND, give_points_amount_handler)],
                ADMIN_GIVE_MONEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, give_money_user_handler)],
                ADMIN_GIVE_MONEY + 1: [MessageHandler(filters.TEXT & ~filters.COMMAND, give_money_amount_handler)],
            },
            fallbacks=[
                CommandHandler('cancel', cancel),
                CommandHandler('start', start),
                CommandHandler('skip', skip_referral)
            ]
        )
        
        app.add_handler(conv_handler)
        
        # إضافة معالجات أزرار الإعلان
        app.add_handler(CallbackQueryHandler(handle_ad_start_callback, pattern='^' + AD_START_CALLBACK_DATA + '$'))
        app.add_handler(CallbackQueryHandler(handle_ad_check_callback, pattern='^' + AD_CHECK_CALLBACK_DATA + '$'))
        app.add_handler(CallbackQueryHandler(handle_ad_confirm_view, pattern='^' + AD_CONFIRM_VIEW + '$'))

        print("🎓 بوت منهج Ai يعمل الآن!")
        
        app.run_polling()
        
    except Exception as e:
        print(f"❌ خطأ فادح في تشغيل البوت: {e}")

if __name__ == "__main__":
    main()
