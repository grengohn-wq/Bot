# api/stats.py - Statistics API for Mini App

import os
import json
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
        print("✅ Stats API: Supabase initialized")
    except Exception as e:
        print(f"❌ Stats API: Supabase initialization failed: {e}")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Get statistics"""
        try:
            # Parse URL path
            path_parts = self.path.split('/')
            
            # Check Supabase availability
            if not supabase:
                self.send_error_response(503, 'Database service not available')
                return
            
            # Route based on path
            if 'user' in self.path:
                # Get user stats
                user_id = self.get_query_param('user_id')
                if not user_id:
                    self.send_error_response(400, 'Missing user_id parameter')
                    return
                
                stats = self.get_user_stats(user_id)
                self.send_json_response({
                    'success': True,
                    'data': stats
                })
                
            elif 'admin' in self.path:
                # Get admin stats (for admin panel)
                stats = self.get_admin_stats()
                self.send_json_response({
                    'success': True,
                    'data': stats
                })
                
            elif 'leaderboard' in self.path:
                # Get leaderboard
                limit = int(self.get_query_param('limit') or '10')
                leaderboard = self.get_leaderboard(limit)
                self.send_json_response({
                    'success': True,
                    'data': leaderboard
                })
                
            else:
                # General platform stats
                stats = self.get_platform_stats()
                self.send_json_response({
                    'success': True,
                    'data': stats
                })
                
        except Exception as e:
            print(f"Stats API Error: {e}")
            self.send_error_response(500, f'Server error: {str(e)}')
    
    def get_user_stats(self, user_id: str) -> dict:
        """Get detailed stats for a specific user"""
        # Get user data
        user_response = supabase.table('students').select('*').eq('telegram_id', user_id).execute()
        if not user_response.data:
            return {'error': 'User not found'}
        
        user = user_response.data[0]
        
        # Get completed tasks count
        completed_tasks_response = supabase.table('completed_tasks').select('*').eq('user_id', user['id']).execute()
        completed_tasks = completed_tasks_response.data or []
        
        # Calculate study streak
        study_streak = self.calculate_study_streak(user['id'])
        
        # Get user rank
        user_rank = self.get_user_rank(user['points'])
        
        # Calculate activity this week
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        weekly_activity = len([task for task in completed_tasks if task['completed_at'] > week_ago])
        
        return {
            'user_info': {
                'name': user['name'],
                'points': user['points'],
                'riyal': user['riyal'],
                'is_premium': user['is_premium'],
                'education_stage': user['education_stage'],
                'country': user['country'],
                'joined_date': user['created_at']
            },
            'activity_stats': {
                'total_tasks_completed': len(completed_tasks),
                'study_streak': study_streak,
                'weekly_activity': weekly_activity,
                'rank': user_rank
            },
            'achievements': {
                'points_milestone': self.get_points_milestone(user['points']),
                'tasks_milestone': self.get_tasks_milestone(len(completed_tasks)),
                'streak_milestone': self.get_streak_milestone(study_streak)
            }
        }
    
    def get_admin_stats(self) -> dict:
        """Get comprehensive admin statistics"""
        try:
            # Total users
            total_users_response = supabase.table('students').select('id').execute()
            total_users = len(total_users_response.data) if total_users_response.data else 0
            
            # Active users (last 7 days)
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            active_users_response = supabase.table('students').select('id').gte('last_activity', week_ago).execute()
            active_users = len(active_users_response.data) if active_users_response.data else 0
            
            # Premium users
            premium_users_response = supabase.table('students').select('id').eq('is_premium', True).execute()
            premium_users = len(premium_users_response.data) if premium_users_response.data else 0
            
            # Total tasks completed
            total_tasks_response = supabase.table('completed_tasks').select('id').execute()
            total_tasks_completed = len(total_tasks_response.data) if total_tasks_response.data else 0
            
            # Today's new users
            today = datetime.now().date().isoformat()
            today_users_response = supabase.table('students').select('id').gte('created_at', today).execute()
            today_new_users = len(today_users_response.data) if today_users_response.data else 0
            
            # Country distribution
            countries_response = supabase.table('students').select('country').execute()
            country_stats = {}
            if countries_response.data:
                for user in countries_response.data:
                    country = user['country'] or 'غير محدد'
                    country_stats[country] = country_stats.get(country, 0) + 1
            
            # Education stage distribution
            education_response = supabase.table('students').select('education_stage').execute()
            education_stats = {}
            if education_response.data:
                for user in education_response.data:
                    stage = user['education_stage'] or 'غير محدد'
                    education_stats[stage] = education_stats.get(stage, 0) + 1
            
            return {
                'overview': {
                    'total_users': total_users,
                    'active_users_week': active_users,
                    'premium_users': premium_users,
                    'today_new_users': today_new_users,
                    'total_tasks_completed': total_tasks_completed,
                    'activity_rate': round((active_users / total_users * 100), 1) if total_users > 0 else 0,
                    'premium_rate': round((premium_users / total_users * 100), 1) if total_users > 0 else 0
                },
                'distribution': {
                    'countries': country_stats,
                    'education_stages': education_stats
                },
                'growth': {
                    'daily_growth': today_new_users,
                    'weekly_growth': self.get_weekly_growth(),
                    'monthly_growth': self.get_monthly_growth()
                }
            }
            
        except Exception as e:
            print(f"Admin stats error: {e}")
            return {'error': str(e)}
    
    def get_platform_stats(self) -> dict:
        """Get general platform statistics"""
        try:
            # Basic stats
            users_response = supabase.table('students').select('id, points, created_at').execute()
            users_data = users_response.data or []
            
            total_users = len(users_data)
            total_points = sum(user['points'] for user in users_data)
            
            # Recent activity (last 24 hours)
            yesterday = (datetime.now() - timedelta(days=1)).isoformat()
            recent_tasks_response = supabase.table('completed_tasks').select('id').gte('completed_at', yesterday).execute()
            recent_activity = len(recent_tasks_response.data) if recent_tasks_response.data else 0
            
            return {
                'total_users': total_users,
                'total_points_distributed': total_points,
                'recent_activity': recent_activity,
                'platform_health': 'excellent' if recent_activity > 10 else 'good' if recent_activity > 5 else 'normal'
            }
            
        except Exception as e:
            print(f"Platform stats error: {e}")
            return {'error': str(e)}
    
    def get_leaderboard(self, limit: int = 10) -> dict:
        """Get top users leaderboard"""
        try:
            leaderboard_response = supabase.table('students').select('name, points, education_stage, country').order('points', desc=True).limit(limit).execute()
            
            leaderboard = []
            if leaderboard_response.data:
                for i, user in enumerate(leaderboard_response.data):
                    leaderboard.append({
                        'rank': i + 1,
                        'name': user['name'],
                        'points': user['points'],
                        'education_stage': user['education_stage'],
                        'country': user['country']
                    })
            
            return {
                'leaderboard': leaderboard,
                'total_entries': len(leaderboard)
            }
            
        except Exception as e:
            print(f"Leaderboard error: {e}")
            return {'error': str(e)}
    
    def calculate_study_streak(self, user_id: int) -> int:
        """Calculate user's current study streak"""
        try:
            # Get recent completed tasks
            tasks_response = supabase.table('completed_tasks').select('completed_at').eq('user_id', user_id).order('completed_at', desc=True).execute()
            
            if not tasks_response.data:
                return 0
            
            # Convert to dates and count consecutive days
            task_dates = set()
            for task in tasks_response.data:
                date = datetime.fromisoformat(task['completed_at']).date()
                task_dates.add(date)
            
            # Check for consecutive days starting from today
            current_date = datetime.now().date()
            streak = 0
            
            while current_date in task_dates:
                streak += 1
                current_date -= timedelta(days=1)
            
            return streak
            
        except Exception as e:
            print(f"Streak calculation error: {e}")
            return 0
    
    def get_user_rank(self, user_points: int) -> int:
        """Get user's rank based on points"""
        try:
            higher_users_response = supabase.table('students').select('id').gt('points', user_points).execute()
            return len(higher_users_response.data) + 1 if higher_users_response.data else 1
            
        except Exception as e:
            print(f"Rank calculation error: {e}")
            return 0
    
    def get_weekly_growth(self) -> int:
        """Get new users in the last week"""
        try:
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            growth_response = supabase.table('students').select('id').gte('created_at', week_ago).execute()
            return len(growth_response.data) if growth_response.data else 0
        except:
            return 0
    
    def get_monthly_growth(self) -> int:
        """Get new users in the last month"""
        try:
            month_ago = (datetime.now() - timedelta(days=30)).isoformat()
            growth_response = supabase.table('students').select('id').gte('created_at', month_ago).execute()
            return len(growth_response.data) if growth_response.data else 0
        except:
            return 0
    
    def get_points_milestone(self, points: int) -> dict:
        """Get points milestone info"""
        milestones = [50, 100, 250, 500, 1000, 2000, 5000]
        
        for milestone in milestones:
            if points < milestone:
                return {
                    'current': points,
                    'next_milestone': milestone,
                    'progress': round((points / milestone) * 100, 1)
                }
        
        return {
            'current': points,
            'next_milestone': None,
            'progress': 100
        }
    
    def get_tasks_milestone(self, tasks: int) -> dict:
        """Get tasks milestone info"""
        milestones = [5, 10, 25, 50, 100, 200, 500]
        
        for milestone in milestones:
            if tasks < milestone:
                return {
                    'current': tasks,
                    'next_milestone': milestone,
                    'progress': round((tasks / milestone) * 100, 1)
                }
        
        return {
            'current': tasks,
            'next_milestone': None,
            'progress': 100
        }
    
    def get_streak_milestone(self, streak: int) -> dict:
        """Get streak milestone info"""
        milestones = [3, 7, 14, 30, 60, 100]
        
        for milestone in milestones:
            if streak < milestone:
                return {
                    'current': streak,
                    'next_milestone': milestone,
                    'progress': round((streak / milestone) * 100, 1)
                }
        
        return {
            'current': streak,
            'next_milestone': None,
            'progress': 100
        }
    
    def get_query_param(self, param_name: str) -> str:
        """Extract query parameter from URL"""
        if '?' not in self.path:
            return None
        
        query_string = self.path.split('?')[1]
        for param in query_string.split('&'):
            if '=' in param:
                key, value = param.split('=', 1)
                if key == param_name:
                    return value
        return None
    
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
def stats_handler(request):
    """Vercel Function Handler"""
    return handler