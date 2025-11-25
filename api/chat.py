# api/chat.py - Chat API for Mini App

import os
import json
import google.generativeai as genai
from http.server import BaseHTTPRequestHandler
from datetime import datetime

# Configuration
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyDTqXo6j5Pz5Ki5Y1fjFFGi3Uo6fp5R7b0')

# Initialize Gemini AI
AI_READY = False
model = None

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')
        AI_READY = True
        print("✅ Chat API: Gemini AI initialized")
    except Exception as e:
        AI_READY = False
        print(f"❌ Chat API: Gemini AI initialization failed: {e}")

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle chat requests"""
        try:
            # Parse request
            content_length = int(self.headers.get('content-length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)
            
            # Validate required fields
            if 'question' not in data:
                self.send_error_response(400, 'Missing required field: question')
                return
            
            question = data['question']
            user_id = data.get('user_id', 0)
            user_name = data.get('user_name', 'طالب')
            education_stage = data.get('education_stage', 'الثانوية العامة')
            country = data.get('country', 'المملكة العربية السعودية')
            
            # Check AI availability
            if not AI_READY:
                self.send_error_response(503, 'Gemini AI service is not available')
                return
            
            # Generate response
            try:
                prompt = self.build_prompt(question, user_name, education_stage, country)
                response = model.generate_content(prompt)
                answer = response.text
                
                # Send successful response
                self.send_json_response({
                    'success': True,
                    'answer': answer,
                    'timestamp': datetime.now().isoformat(),
                    'model': 'gemini-2.0-flash'
                })
                
            except Exception as e:
                print(f"Gemini AI Error: {e}")
                self.send_error_response(500, f'AI processing error: {str(e)}')
                
        except json.JSONDecodeError:
            self.send_error_response(400, 'Invalid JSON in request body')
        except Exception as e:
            print(f"Chat API Error: {e}")
            self.send_error_response(500, f'Server error: {str(e)}')
    
    def do_GET(self):
        """Handle health check"""
        self.send_json_response({
            'status': 'ok',
            'service': 'منهج AI Chat API',
            'version': '2.0',
            'ai_ready': AI_READY,
            'timestamp': datetime.now().isoformat()
        })
    
    def build_prompt(self, question: str, user_name: str, education_stage: str, country: str) -> str:
        """Build optimized prompt for Gemini"""
        return f"""أنت معلم خبير في المنهج {country} للمرحلة {education_stage}.
اسم الطالب هو {user_name}.

أنت تعمل ضمن تطبيق منهج AI الذكي - وهو تطبيق تعليمي متقدم على تيليجرام مخصص للطلاب العرب.

مهامك الرئيسية:
• تقديم إجابات تعليمية دقيقة وموثوقة
• التركيز على المنهج الدراسي لدولة {country} والمرحلة {education_stage}
• استخدام أسلوب تعليمي واضح ومناسب لعمر الطالب
• تقديم أمثلة عملية ونصائح دراسية مفيدة
• التشجيع والتحفيز الإيجابي

قواعد الإجابة:
1. ابدأ بترحيب شخصي باستخدام اسم الطالب
2. قدم إجابة شاملة ومنظمة
3. استخدم نقاط ترقيم وتنسيق واضح
4. أضف نصائح دراسية إضافية عند الإمكان
5. اختتم بتشجيع للطالب

السؤال: {question}

تذكر: أجب بالعربية الفصحى مع لمسة ودية، واجعل إجابتك تعليمية ومفيدة ومحفزة للطالب."""
    
    def send_json_response(self, data: dict, status_code: int = 200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def send_error_response(self, status_code: int, message: str):
        """Send error response"""
        self.send_json_response({
            'success': False,
            'error': message,
            'timestamp': datetime.now().isoformat()
        }, status_code)
    
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

# Export for Vercel
def chat_handler(request):
    """Vercel Function Handler"""
    return handler