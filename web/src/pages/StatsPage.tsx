// src/pages/StatsPage.tsx - Statistics page for the Mini App

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { useUserStore } from '@/store/userStore';
import { useTelegram } from '@/hooks/useTelegram';
import { useSound } from '@/hooks/useSound';

interface UserStats {
  user_info: {
    name: string;
    points: number;
    riyal: number;
    is_premium: boolean;
    education_stage: string;
    country: string;
    joined_date: string;
  };
  activity_stats: {
    total_tasks_completed: number;
    study_streak: number;
    weekly_activity: number;
    rank: number;
  };
  achievements: {
    points_milestone: {
      current: number;
      next_milestone: number | null;
      progress: number;
    };
    tasks_milestone: {
      current: number;
      next_milestone: number | null;
      progress: number;
    };
    streak_milestone: {
      current: number;
      next_milestone: number | null;
      progress: number;
    };
  };
}

interface LeaderboardEntry {
  rank: number;
  name: string;
  points: number;
  education_stage: string;
  country: string;
}

const StatsPage: React.FC = () => {
  const { hapticFeedback } = useTelegram();
  const { playSound } = useSound();
  const { user } = useUserStore();
  
  const [stats, setStats] = useState<UserStats | null>(null);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'stats' | 'leaderboard'>('stats');

  useEffect(() => {
    if (user?.telegram_id) {
      fetchStats();
      fetchLeaderboard();
    }
  }, [user?.telegram_id]);

  const fetchStats = async () => {
    if (!user?.telegram_id) return;
    
    try {
      setLoading(true);
      const response = await fetch(`/api/stats/user?user_id=${user.telegram_id}`);
      const data = await response.json();
      
      if (data.success) {
        setStats(data.data);
        setError(null);
      } else {
        setError(data.error || 'حدث خطأ في تحميل الإحصائيات');
      }
    } catch (err) {
      setError('فشل في الاتصال بالخادم');
      console.error('Stats fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchLeaderboard = async () => {
    try {
      const response = await fetch('/api/stats/leaderboard?limit=10');
      const data = await response.json();
      
      if (data.success) {
        setLeaderboard(data.data.leaderboard || []);
      }
    } catch (err) {
      console.error('Leaderboard fetch error:', err);
    }
  };

  const getRankEmoji = (rank: number): string => {
    if (rank <= 3) return '👑';
    if (rank <= 10) return '⭐';
    if (rank <= 50) return '🏅';
    return '📊';
  };

  const getProgressColor = (progress: number): string => {
    if (progress >= 80) return 'bg-green-500';
    if (progress >= 50) return 'bg-primary-500';
    if (progress >= 25) return 'bg-yellow-500';
    return 'bg-gray-500';
  };

  const formatJoinDate = (dateString: string): string => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('ar-SA', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    } catch {
      return 'غير محدد';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-gray-900 to-blue-900">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-blue-900 text-white" dir="rtl">
      {/* Header */}
      <div className="bg-gray-800 shadow-lg border-b-4 border-primary-500">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">📊 الإحصائيات</h1>
              <p className="text-gray-300 mt-1">تابع تقدمك ومستواك التعليمي</p>
            </div>
            <div className="text-center">
              <div className="text-3xl">{getRankEmoji(stats?.activity_stats.rank || 0)}</div>
              <div className="text-sm text-gray-400">المرتبة #{stats?.activity_stats.rank}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="px-4 mt-4">
        <div className="bg-gray-800 rounded-xl shadow-md p-2">
          <div className="flex gap-2">
            {[
              { key: 'stats', label: 'إحصائياتي', icon: '📈' },
              { key: 'leaderboard', label: 'المتصدرون', icon: '🏆' }
            ].map(({ key, label, icon }) => (
              <button
                key={key}
                onClick={() => {
                  setActiveTab(key as any);
                  hapticFeedback?.selection();
                  playSound && playSound('click');
                }}
                className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                  activeTab === key
                    ? 'bg-primary-500 text-white shadow-lg'
                    : 'text-gray-300 hover:bg-gray-700'
                }`}
              >
                <span>{icon}</span>
                <span>{label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="px-4 py-4 pb-24">
        <AnimatePresence mode="wait">
          {activeTab === 'stats' ? (
            <motion.div
              key="stats"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="space-y-4"
            >
              {error ? (
                <Card className="text-center py-8 bg-gray-800 border-gray-600">
                  <div className="text-red-400 text-lg mb-2">❌ حدث خطأ</div>
                  <p className="text-gray-300 mb-4">{error}</p>
                  <Button onClick={fetchStats} variant="outline">
                    إعادة المحاولة
                  </Button>
                </Card>
              ) : stats ? (
                <>
                  {/* User Info Card */}
                  <Card className="bg-gradient-to-r from-primary-500 to-primary-600 text-white border-0">
                    <div className="text-center">
                      <div className="text-4xl mb-2">👋</div>
                      <h2 className="text-xl font-bold mb-1">أهلاً {stats.user_info.name}!</h2>
                      <p className="opacity-90 text-sm">
                        {stats.user_info.education_stage} • {stats.user_info.country}
                      </p>
                      <p className="opacity-75 text-xs mt-2">
                        عضو منذ {formatJoinDate(stats.user_info.joined_date)}
                      </p>
                    </div>
                  </Card>

                  {/* Points & Riyal */}
                  <div className="grid grid-cols-2 gap-4">
                    <Card className="text-center bg-gray-800 border-green-500">
                      <div className="text-3xl mb-2">💰</div>
                      <div className="text-2xl font-bold text-green-400">{stats.user_info.points}</div>
                      <div className="text-sm text-gray-400">نقطة</div>
                    </Card>
                    <Card className="text-center bg-gray-800 border-purple-500">
                      <div className="text-3xl mb-2">💎</div>
                      <div className="text-2xl font-bold text-purple-400">{stats.user_info.riyal}</div>
                      <div className="text-sm text-gray-400">ريال</div>
                    </Card>
                  </div>

                  {/* Activity Stats */}
                  <Card className="bg-gray-800 border-gray-600">
                    <h3 className="font-semibold text-gray-100 mb-4 text-center">📈 إحصائيات النشاط</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-primary-400">{stats.activity_stats.total_tasks_completed}</div>
                        <div className="text-sm text-gray-400">مهمة مكتملة</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-red-400">{stats.activity_stats.study_streak}</div>
                        <div className="text-sm text-gray-400">أيام متتالية 🔥</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-400">{stats.activity_stats.weekly_activity}</div>
                        <div className="text-sm text-gray-400">نشاط الأسبوع</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-purple-400">#{stats.activity_stats.rank}</div>
                        <div className="text-sm text-gray-400">الترتيب العام</div>
                      </div>
                    </div>
                  </Card>

                  {/* Progress Milestones */}
                  <Card className="bg-gray-800 border-gray-600">
                    <h3 className="font-semibold text-gray-100 mb-4 text-center">🎯 التقدم نحو الأهداف</h3>
                    <div className="space-y-4">
                      {/* Points Progress */}
                      <div>
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm font-medium text-gray-300">النقاط</span>
                          <span className="text-sm text-gray-400">
                            {stats.achievements.points_milestone.current}
                            {stats.achievements.points_milestone.next_milestone && 
                              ` / ${stats.achievements.points_milestone.next_milestone}`
                            }
                          </span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full transition-all duration-500 ${
                              getProgressColor(stats.achievements.points_milestone.progress)
                            }`}
                            style={{ width: `${stats.achievements.points_milestone.progress}%` }}
                          />
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          {stats.achievements.points_milestone.progress.toFixed(1)}% مكتمل
                        </div>
                      </div>

                      {/* Tasks Progress */}
                      <div>
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm font-medium text-gray-300">المهام</span>
                          <span className="text-sm text-gray-400">
                            {stats.achievements.tasks_milestone.current}
                            {stats.achievements.tasks_milestone.next_milestone && 
                              ` / ${stats.achievements.tasks_milestone.next_milestone}`
                            }
                          </span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full transition-all duration-500 ${
                              getProgressColor(stats.achievements.tasks_milestone.progress)
                            }`}
                            style={{ width: `${stats.achievements.tasks_milestone.progress}%` }}
                          />
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          {stats.achievements.tasks_milestone.progress.toFixed(1)}% مكتمل
                        </div>
                      </div>

                      {/* Streak Progress */}
                      <div>
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm font-medium text-gray-300">السلسلة 🔥</span>
                          <span className="text-sm text-gray-400">
                            {stats.achievements.streak_milestone.current}
                            {stats.achievements.streak_milestone.next_milestone && 
                              ` / ${stats.achievements.streak_milestone.next_milestone}`
                            } يوم
                          </span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full transition-all duration-500 ${
                              getProgressColor(stats.achievements.streak_milestone.progress)
                            }`}
                            style={{ width: `${stats.achievements.streak_milestone.progress}%` }}
                          />
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          {stats.achievements.streak_milestone.progress.toFixed(1)}% مكتمل
                        </div>
                      </div>
                    </div>
                  </Card>

                  {/* Premium Status */}
                  <Card className={`${stats.user_info.is_premium ? 'bg-gradient-to-r from-yellow-600 to-orange-700 border-yellow-500' : 'bg-gray-800 border-gray-600'}`}>
                    <div className="text-center">
                      <div className="text-4xl mb-2">
                        {stats.user_info.is_premium ? '⭐' : '🆓'}
                      </div>
                      <h3 className="font-semibold text-white mb-1">
                        {stats.user_info.is_premium ? 'عضو بريميوم' : 'عضو مجاني'}
                      </h3>
                      <p className="text-gray-300 text-sm">
                        {stats.user_info.is_premium 
                          ? 'تتمتع بجميع الميزات المتقدمة!'
                          : 'ارتق إلى البريميوم للحصول على المزيد من الميزات'
                        }
                      </p>
                      {!stats.user_info.is_premium && (
                        <Button 
                          className="mt-3 bg-gradient-to-r from-yellow-500 to-orange-500 text-white border-0"
                          size="sm"
                          onClick={() => {
                            hapticFeedback?.notification('success');
                            playSound && playSound('click');
                          }}
                        >
                          ترقية إلى البريميوم ⭐
                        </Button>
                      )}
                    </div>
                  </Card>
                </>
              ) : (
                <LoadingSpinner />
              )}
            </motion.div>
          ) : (
            <motion.div
              key="leaderboard"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-3"
            >
              <Card className="bg-gray-800 border-gray-600">
                <h3 className="font-semibold text-gray-100 mb-4 text-center">🏆 أفضل 10 طلاب</h3>
                <div className="space-y-3">
                  {leaderboard.length > 0 ? (
                    leaderboard.map((entry, index) => (
                      <motion.div
                        key={entry.rank}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className={`flex items-center gap-3 p-3 rounded-lg ${
                          entry.name === user?.name 
                            ? 'bg-primary-500/20 border-2 border-primary-500' 
                            : 'bg-gray-700'
                        }`}
                      >
                        {/* Rank */}
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                          entry.rank === 1 ? 'bg-yellow-500 text-black' :
                          entry.rank === 2 ? 'bg-gray-400 text-white' :
                          entry.rank === 3 ? 'bg-amber-600 text-white' :
                          'bg-gray-600 text-white'
                        }`}>
                          {entry.rank}
                        </div>
                        
                        {/* User Info */}
                        <div className="flex-1">
                          <div className="font-medium text-gray-100">
                            {entry.name}
                            {entry.name === user?.name && <span className="text-primary-400 mr-1">(أنت)</span>}
                          </div>
                          <div className="text-xs text-gray-400">
                            {entry.education_stage} • {entry.country}
                          </div>
                        </div>
                        
                        {/* Points */}
                        <div className="text-left">
                          <div className="font-bold text-green-400">{entry.points}</div>
                          <div className="text-xs text-gray-500">نقطة</div>
                        </div>
                      </motion.div>
                    ))
                  ) : (
                    <div className="text-center py-8 text-gray-400">
                      <div className="text-4xl mb-2">📊</div>
                      <p>لا توجد بيانات متاحة حالياً</p>
                    </div>
                  )}
                </div>
              </Card>
              
              {/* Motivational Message */}
              <Card className="bg-gradient-to-r from-purple-600 to-pink-700 text-white text-center border-0">
                <div className="text-4xl mb-2">🚀</div>
                <h3 className="font-semibold mb-1">استمر في التميز!</h3>
                <p className="text-sm opacity-90">
                  كل سؤال تطرحه ومهمة تنجزها تقربك من القمة
                </p>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default StatsPage;