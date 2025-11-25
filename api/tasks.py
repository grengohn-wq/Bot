# api/tasks.py - Tasks API for Mini App

import os
import json
import asyncio
from supabase import create_client, Client
from http.server import BaseHTTPRequestHandler
from datetime import datetime, timedelta

# Supabase Configuration
SUPABASE_URL = os.environ.get('NEXT_PUBLIC_SUPABASE_URL', '')
SUPABASE_ANON_KEY = os.environ.get('NEXT_PUBLIC_SUPABASE_ANON_KEY', '')

# Initialize Supabase
supabase: Client = None

if SUPABASE_URL and SUPABASE_ANON_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        print("✅ Tasks API: Supabase initialized")
    except Exception as e:
        print(f"❌ Tasks API: Supabase initialization failed: {e}")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Get available tasks for user"""
        try:
            # Parse query parameters
            path_parts = self.path.split('?')
            if len(path_parts) > 1:
                params = self.parse_query_params(path_parts[1])
            else:
                params = {}
            
            user_id = params.get('user_id')
            if not user_id:
                self.send_error_response(400, 'Missing user_id parameter')
                return
            
            # Check Supabase availability
            if not supabase:
                self.send_error_response(503, 'Database service not available')
                return
            
            # Get user data
            user_response = supabase.table('students').select('*').eq('telegram_id', user_id).execute()
            if not user_response.data:
                self.send_error_response(404, 'User not found')
                return
            
            user = user_response.data[0]
            
            # Get available tasks
            tasks = self.get_available_tasks(user)
            
            # Get user's completed tasks
            completed_response = supabase.table('completed_tasks').select('task_name').eq('user_id', user['id']).execute()
            completed_tasks = [task['task_name'] for task in completed_response.data] if completed_response.data else []
            
            # Filter out completed tasks
            available_tasks = [task for task in tasks if task['name'] not in completed_tasks]
            
            self.send_json_response({
                'success': True,
                'tasks': available_tasks,
                'completed_count': len(completed_tasks),
                'available_count': len(available_tasks)
            })
            
        except Exception as e:
            print(f"Tasks API GET Error: {e}")
            self.send_error_response(500, f'Server error: {str(e)}')
    
    def do_POST(self):
        """Complete a task"""
        try:
            # Parse request body
            content_length = int(self.headers.get('content-length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)
            
            # Validate required fields
            required_fields = ['user_id', 'task_name']
            for field in required_fields:
                if field not in data:
                    self.send_error_response(400, f'Missing required field: {field}')
                    return
            
            user_id = data['user_id']
            task_name = data['task_name']
            
            # Check Supabase availability
            if not supabase:
                self.send_error_response(503, 'Database service not available')
                return
            
            # Get user data
            user_response = supabase.table('students').select('*').eq('telegram_id', user_id).execute()
            if not user_response.data:
                self.send_error_response(404, 'User not found')
                return
            
            user = user_response.data[0]
            
            # Check if task already completed
            completed_check = supabase.table('completed_tasks').select('id').eq('user_id', user['id']).eq('task_name', task_name).execute()
            if completed_check.data:
                self.send_error_response(400, 'Task already completed')
                return
            
            # Get task details
            tasks = self.get_available_tasks(user)
            task = next((t for t in tasks if t['name'] == task_name), None)
            if not task:
                self.send_error_response(404, 'Task not found')
                return
            
            # Complete the task
            result = self.complete_task(user, task)
            
            if result['success']:
                self.send_json_response({
                    'success': True,
                    'message': f'تم إنجاز المهمة بنجاح! حصلت على {task["points"]} نقطة',
                    'points_earned': task['points'],
                    'new_total_points': result['new_points']
                })
            else:
                self.send_error_response(500, result['error'])
                
        except json.JSONDecodeError:
            self.send_error_response(400, 'Invalid JSON in request body')
        except Exception as e:
            print(f"Tasks API POST Error: {e}")
            self.send_error_response(500, f'Server error: {str(e)}')
    
    def get_available_tasks(self, user: dict) -> list:
        """Get tasks based on user level and activity"""
        tasks = [
            {
                "name": "first_question",
                "title": "أول سؤال",
                "description": "اطرح أول سؤال تعليمي في البوت",
                "points": 10,
                "type": "chat",
                "icon": "💬"
            },
            {
                "name": "daily_active",
                "title": "نشاط يومي",
                "description": "استخدم التطبيق لمدة 5 دقائق اليوم",
                "points": 5,
                "type": "activity",
                "icon": "📱"
            },
            {
                "name": "five_questions",
                "title": "خمسة أسئلة",
                "description": "اطرح 5 أسئلة تعليمية مختلفة",
                "points": 25,
                "type": "chat",
                "icon": "🎯"
            },
            {
                "name": "referral_friend",
                "title": "دعوة صديق",
                "description": "ادع صديق للانضمام للتطبيق",
                "points": 50,
                "type": "referral",
                "icon": "👥"
            },
            {
                "name": "complete_profile",
                "title": "إكمال الملف الشخصي",
                "description": "أكمل بياناتك الشخصية في التطبيق",
                "points": 20,
                "type": "profile",
                "icon": "📝"
            },
            {
                "name": "weekly_champion",
                "title": "بطل الأسبوع",
                "description": "استخدم التطبيق كل يوم هذا الأسبوع",
                "points": 100,
                "type": "achievement",
                "icon": "🏆"
            },
            {
                "name": "study_streak",
                "title": "سلسلة الدراسة",
                "description": "ادرس لمدة 3 أيام متتالية",
                "points": 75,
                "type": "streak",
                "icon": "🔥"
            },
            {
                "name": "premium_trial",
                "title": "تجربة البريميوم",
                "description": "فعل تجربة البريميوم المجانية",
                "points": 30,
                "type": "premium",
                "icon": "⭐"
            },
            {
                "name": "feedback_master",
                "title": "خبير التقييم",
                "description": "قيم التطبيق في متجر التطبيقات",
                "points": 40,
                "type": "feedback",
                "icon": "⭐"
            },
            {
                "name": "math_specialist",
                "title": "متخصص الرياضيات",
                "description": "اطرح 10 أسئلة في الرياضيات",
                "points": 60,
                "type": "subject",
                "icon": "🔢"
            }
        ]
        
        # Filter tasks based on user level
        user_level = self.get_user_level(user)
        
        # Beginner tasks (first week)
        if user_level <= 1:
            return [task for task in tasks if task['type'] in ['chat', 'activity', 'profile']]
        
        # Intermediate tasks 
        elif user_level <= 3:
            return [task for task in tasks if task['type'] not in ['achievement']]
        
        # Advanced tasks (all tasks available)
        else:
            return tasks
    
    def get_user_level(self, user: dict) -> int:
        """Calculate user level based on points and activity"""
        points = user.get('points', 0)
        
        if points < 50:
            return 1
        elif points < 150:
            return 2
        elif points < 300:
            return 3
        elif points < 500:
            return 4
        else:
            return 5
    
    def complete_task(self, user: dict, task: dict) -> dict:
        """Complete a task and award points"""
        try:
            # Insert completed task record
            supabase.table('completed_tasks').insert({
                'user_id': user['id'],
                'task_name': task['name'],
                'points_earned': task['points'],
                'completed_at': datetime.now().isoformat()
            }).execute()
            
            # Update user points
            new_points = user['points'] + task['points']
            supabase.table('students').update({
                'points': new_points,
                'updated_at': datetime.now().isoformat()
            }).eq('id', user['id']).execute()
            
            return {
                'success': True,
                'new_points': new_points
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def parse_query_params(self, query_string: str) -> dict:
        """Parse URL query parameters"""
        params = {}
        for param in query_string.split('&'):
            if '=' in param:
                key, value = param.split('=', 1)
                params[key] = value
        return params
    
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
def tasks_handler(request):
    """Vercel Function Handler"""
    return handler