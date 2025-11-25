# api/bot.py - بوت منهج AI محول لـ webhook (Vercel Compatible)

import os
import json
import uuid
import asyncio
import time
import re
import warnings
from datetime import datetime
from typing import Optional
import logging

# قمع التحذيرات
warnings.filterwarnings("ignore")
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '2'
logging.getLogger('google').setLevel(logging.ERROR)

# Vercel Handler
from http.server import BaseHTTPRequestHandler
import urllib.parse

# Telegram & AI
import google.generativeai as genai
from telegram import Update, Bot, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, ContextTypes

# Supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠️ Supabase client not available. Install with: pip install supabase")

# Configuration
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8522705485:AAHeqccrQ5GpXi4HiQzwyEJwQo4yt6P82Uc')
SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyDTqXo6j5Pz5Ki5Y1fjFFGi3Uo6fp5R7b0')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'mosap@123123')

# Static Configuration
AD_LINK = "https://otieu.com/4/10160934"
AD_RESPONSE_LIMIT = 2
PREMIUM_PRICE = "10 ريال سعودي"

# Arab Countries & Education Stages
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

# Initialize Supabase
supabase: Optional[Client] = None
if SUPABASE_AVAILABLE and SUPABASE_URL and SUPABASE_SERVICE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        print("✅ Supabase initialized successfully")
    except Exception as e:
        print(f"❌ Supabase initialization failed: {e}")

# Initialize Gemini AI
AI_READY = False
model = None

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')
        AI_READY = True
        print("✅ Gemini AI initialized successfully")
    except Exception as e:
        AI_READY = False
        print(f"❌ Gemini AI initialization failed: {e}")

# Database Functions (Supabase)
def get_user_by_id(user_id: int):
    """جلب بيانات المستخدم"""
    if not supabase:
        return None
    try:
        response = supabase.table('students').select('*').eq('telegram_id', user_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Database error: {e}")
        return None

def create_user(user_id: int, name: str, stage: str, country: str, verification_code: str = None, referral_code: str = None):
    """إنشاء مستخدم جديد"""
    if not supabase:
        return False
    try:
        verification_code = verification_code or str(uuid.uuid4()).split('-')[0].upper()
        user_data = {
            'telegram_id': user_id,
            'name': name,
            'education_stage': stage,
            'country': country,
            'verification_code': verification_code,
            'points': 50,  # Welcome bonus
            'riyal': 0,
            'is_premium': False,
            'is_gift_premium': False,
            'is_manager': False,
            'successful_referrals': 0,
            'referral_code': referral_code,
            'questions_count': 0,
            'ads_response_count': 0
        }
        response = supabase.table('students').insert(user_data).execute()
        return response.data[0] if response.data else False
    except Exception as e:
        print(f"Database create error: {e}")
        return False

def update_user_points(user_id: int, points: int, reason: str = ""):
    """تحديث نقاط المستخدم"""
    if not supabase:
        return False
    try:
        current_user = get_user_by_id(user_id)
        if current_user:
            new_points = current_user['points'] + points
            supabase.table('students').update({'points': new_points}).eq('telegram_id', user_id).execute()
            return True
        return False
    except Exception as e:
        print(f"Update points error: {e}")
        return False

def convert_points_to_riyal(user_id: int, points: int):
    """تحويل النقاط لريال"""
    if not supabase or points < 100:
        return False, "الحد الأدنى للتحويل 100 نقطة"
    
    try:
        user = get_user_by_id(user_id)
        if not user or user['points'] < points:
            return False, "رصيد النقاط غير كافي"
        
        riyal = points // 100
        new_points = user['points'] - points
        new_riyal = user['riyal'] + riyal
        
        supabase.table('students').update({
            'points': new_points,
            'riyal': new_riyal
        }).eq('telegram_id', user_id).execute()
        
        return True, f"تم تحويل {points} نقطة إلى {riyal} ريال"
    except Exception as e:
        return False, "حدث خطأ في التحويل"

def buy_premium(user_id: int):
    """شراء البريميم"""
    if not supabase:
        return False, "خدمة غير متوفرة"
    
    try:
        user = get_user_by_id(user_id)
        if not user or user['riyal'] < 10:
            return False, "رصيد الريال غير كافي"
        
        new_riyal = user['riyal'] - 10
        supabase.table('students').update({
            'riyal': new_riyal,
            'is_premium': True,
            'ads_response_count': 0
        }).eq('telegram_id', user_id).execute()
        
        return True, "تم شراء البريميم بنجاح"
    except Exception as e:
        return False, "حدث خطأ في الشراء"

def record_question(user_id: int, question: str):
    """تسجيل السؤال"""
    if not supabase:
        return False
    try:
        # Update question count and ad response count
        user = get_user_by_id(user_id)
        if user:
            supabase.table('students').update({
                'questions_count': user['questions_count'] + 1,
                'ads_response_count': user['ads_response_count'] + 1
            }).eq('telegram_id', user_id).execute()
        
        # Record question
        supabase.table('questions').insert({
            'user_id': user_id,
            'question': question,
            'question_type': 'general'
        }).execute()
        
        return True
    except Exception as e:
        print(f"Record question error: {e}")
        return False

# Helper Functions
def validate_full_name(name: str):
    """التحقق من صحة الاسم"""
    if not name or len(name.strip()) == 0:
        return False, "❌ الاسم لا يمكن أن يكون فارغاً"
    
    parts = name.strip().split()
    
    if len(parts) != 3:
        return False, "❌ يجب إدخال الاسم الثلاثي (الاسم الأول + الأب + الجد)\nمثال: محمد عبدالله الفهد"
    
    for part in parts:
        if re.search(r'[0-9!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?]', part):
            return False, f"❌ الجزء '{part}' يحتوي على أرقام أو رموز\nيجب أن يحتوي الاسم على أحرف عربية أو إنجليزية فقط"
        
        if not re.search(r'[a-zA-Zأ-ي]', part):
            return False, f"❌ الجزء '{part}' غير صالح\nيجب أن يحتوي على أحرف عربية أو إنجليزية"
    
    return True, "✅ الاسم صالح"

def check_ad_block(user_id: int):
    """التحقق من حظر الإعلان"""
    if not supabase:
        return False
    try:
        user = get_user_by_id(user_id)
        if user and not user['is_premium'] and user['ads_response_count'] >= AD_RESPONSE_LIMIT:
            return True
        return False
    except Exception:
        return False

# Bot Handlers
class TelegramBot:
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.app = Application.builder().token(BOT_TOKEN).build()
    
    async def handle_start(self, user_id: int, first_name: str) -> dict:
        """معالجة أمر /start"""
        user = get_user_by_id(user_id)
        
        if user:
            return {
                'text': f"🎓 أهلاً بعودتك {user['name']}!\n\n"
                        f"💎 **رصيد النقاط:** {user['points']} نقطة\n"
                        f"💵 **رصيد الريال:** {user['riyal']} ريال\n"
                        f"✨ **حالة البريميم:** {'✅ مفعل' if user['is_premium'] else '❌ غير مفعل'}\n\n"
                        f"🧠 **اكتب سؤالك مباشرة وسأجيبك بإجابة منهجية شاملة**",
                'reply_markup': self.get_main_menu_keyboard(user)
            }
        else:
            return {
                'text': f"🎓 أهلاً بك {first_name}!\n\n"
                        f"أنـا بـوت **منهج AI** 🧠 للإجابات المنهجية الشاملة.\n\n"
                        f"**الرجاء إدخال اسمك الثلاثي كاملاً:**\n"
                        f"👉 الاسم الأول + اسم الأب + اسم الجد\n\n"
                        f"**مثال:** محمد عبدالله الفهد"
            }
    
    async def handle_question(self, user_id: int, question: str, user_name: str = "طالب") -> dict:
        """معالجة الأسئلة"""
        # تسجيل السؤال
        record_question(user_id, question)
        
        # التحقق من الإعلان
        if check_ad_block(user_id):
            keyboard = [[{
                'text': "🔗 انقر هنا لتفعيل زر المتابعة",
                'callback_data': "start_ad_timer"
            }]]
            return {
                'text': f"🛑 **نحتاج دعمك (إعلان):**\n\n"
                       f"أنت بحاجة لدعم البوت لتمويل استمرار الخدمة.\n\n"
                       f"اضغط على الزر أدناه واتبع التعليمات.",
                'reply_markup': {'inline_keyboard': keyboard}
            }
        
        if not AI_READY:
            return {'text': "❌ الذكاء الاصطناعي غير متاح حالياً"}
        
        try:
            user = get_user_by_id(user_id)
            stage = user['education_stage'] if user else "الثانوية العامة"
            country = user['country'] if user else "السعودية"
            
            prompt = (
                f"أنت معلم خبير في المنهج {country} للمرحلة {stage}. "
                f"اسم الطالب هو {user_name}. "
                f"أنت تعمل ضمن بوت تعليمي على تطبيق تيليجرام ومهامك الرئيسية هي مساعدة الطلاب تعليمياً. "
                f"مهمتك هي الإجابة على استفسارات الطلاب التعليمية بأعلى درجة من الدقة والموثوقية المنهجية، "
                f"مع التركيز على المنهج الدراسي لدولة {country} والمرحلة {stage}. "
                f"أجب على السؤال التالي بإجابة تعليمية منهجية دقيقة:\n\n"
                f"السؤال: {question}"
            )

            response = model.generate_content(prompt)
            answer = response.text
            
            return {
                'text': f"🎯 **الإجابة التعليمية يا {user_name}:**\n\n{answer}\n\n"
                       f"💡 هل لديك سؤال آخر؟ يمكنك كتابته مباشرة."
            }
            
        except Exception as e:
            print(f"AI Error: {e}")
            return {'text': "❌ حدث خطأ في المعالجة. جرب سؤالاً آخر."}
    
    def get_main_menu_keyboard(self, user=None):
        """إنشاء لوحة المفاتيح الرئيسية"""
        keyboard = [
            [{'text': "🔍 بحث عام"}],
            [{'text': "📊 إحصائياتي"}, {'text': "🔑 معرف التفعيل"}],
            [{'text': "💎 نقاطي"}, {'text': "📤 تحويل نقاط"}],
            [{'text': "🔀 تحويل ريال"}, {'text': "🛒 شراء بريميم"}],
            [{'text': "👥 نظام الإحالة"}, {'text': "📋 المهام"}],
            [{'text': "🎬 مشاهدة إعلان"}, {'text': "📞 اتصل بالدعم"}],
            [{'text': "🔄 تحديث القائمة"}]
        ]
        
        if user and user.get('is_manager'):
            keyboard.append([{'text': "🛠️ الدخول لوضع المدير"}])
        
        return {'keyboard': keyboard, 'resize_keyboard': True}

# Webhook Handler
bot_instance = TelegramBot()

class handler(BaseHTTPRequestHandler):
    async def process_update(self, update_data: dict):
        """معالجة التحديثات"""
        try:
            update = Update.de_json(update_data, bot_instance.bot)
            
            if update.message:
                user_id = update.message.from_user.id
                first_name = update.message.from_user.first_name
                text = update.message.text
                
                if text == '/start':
                    response = await bot_instance.handle_start(user_id, first_name)
                elif text and text.startswith('/'):
                    # Handle other commands
                    response = {'text': 'أمر غير معروف. استخدم /start للبدء.'}
                else:
                    # Handle regular messages/questions
                    user = get_user_by_id(user_id)
                    user_name = user['name'] if user else first_name
                    response = await bot_instance.handle_question(user_id, text, user_name)
                
                # Send response
                if response:
                    await bot_instance.bot.send_message(
                        chat_id=user_id,
                        text=response['text'],
                        reply_markup=response.get('reply_markup')
                    )
            
            elif update.callback_query:
                # Handle inline keyboard callbacks
                query = update.callback_query
                user_id = query.from_user.id
                data = query.data
                
                if data == "start_ad_timer":
                    keyboard = [[
                        {'text': "🌐 رابط الإعلان (اضغط هنا)", 'url': AD_LINK},
                        {'text': "✅ المتابعة بعد 5 ثواني", 'callback_data': "check_ad_timer"}
                    ]]
                    
                    await query.edit_message_text(
                        text="⚠️ **الخطوات المطلوبة:**\n"
                             "1. **اضغط على الرابط أعلاه** وانتظر 5 ثوانٍ.\n"
                             "2. اضغط على زر **'المتابعة بعد 5 ثواني'**.\n\n"
                             "🎁 **ستحصل على 5 نقاط مكافأة!**",
                        reply_markup={'inline_keyboard': keyboard}
                    )
                
                elif data == "check_ad_timer":
                    # Reset ad counter and give bonus
                    if supabase:
                        supabase.table('students').update({
                            'ads_response_count': 0,
                            'points': lambda x: x + 5  # Add 5 points bonus
                        }).eq('telegram_id', user_id).execute()
                    
                    await query.edit_message_text(
                        text="✅ **شكراً لدعمك!**\n\n"
                             "تم تصفير العداد وإضافة 5 نقاط مكافأة!\n\n"
                             "يمكنك الآن إعادة طرح سؤالك السابق."
                    )
        
        except Exception as e:
            print(f"Update processing error: {e}")
    
    def do_POST(self):
        """معالجة طلبات POST"""
        try:
            content_length = int(self.headers.get('content-length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            update_data = json.loads(body)
            
            # Run async function
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.process_update(update_data))
            loop.close()
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok'}).encode())
            
        except Exception as e:
            print(f"Webhook error: {e}")
            self.send_response(500)
            self.end_headers()
    
    def do_GET(self):
        """معالجة طلبات GET"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = {
            'status': 'ok',
            'message': 'منهج AI Bot Webhook',
            'version': '2.0',
            'ai_ready': AI_READY,
            'supabase_ready': supabase is not None
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

# Export for Vercel
def webhook(request):
    """Vercel Function Handler"""
    return handler