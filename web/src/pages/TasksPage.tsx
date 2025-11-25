// src/pages/TasksPage.tsx - Tasks page for the Mini App

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { useTelegram } from '@/hooks/useTelegram';
import { useSound } from '@/hooks/useSound';
import { useUserStore } from '@/store/userStore';

interface Task {
  name: string;
  title: string;
  description: string;
  points: number;
  type: string;
  icon: string;
}

interface TasksState {
  tasks: Task[];
  completedCount: number;
  availableCount: number;
  loading: boolean;
  error: string | null;
}

const TasksPage: React.FC = () => {
  const { hapticFeedback } = useTelegram();
  const { playSound } = useSound();
  const { user } = useUserStore();
  
  const [tasksState, setTasksState] = useState<TasksState>({
    tasks: [],
    completedCount: 0,
    availableCount: 0,
    loading: true,
    error: null
  });
  
  const [filter, setFilter] = useState<'all' | 'activity' | 'chat' | 'achievement'>('all');
  const [completingTask, setCompletingTask] = useState<string | null>(null);

  useEffect(() => {
    if (user?.telegram_id) {
      fetchTasks();
    }
  }, [user?.telegram_id]);

  const fetchTasks = async () => {
    if (!user?.telegram_id) return;
    
    try {
      setTasksState(prev => ({ ...prev, loading: true, error: null }));
      
      const response = await fetch(`/api/tasks?user_id=${user.telegram_id}`);
      const data = await response.json();
      
      if (data.success) {
        setTasksState(prev => ({
          ...prev,
          tasks: data.tasks || [],
          completedCount: data.completed_count || 0,
          availableCount: data.available_count || 0,
          loading: false,
          error: null
        }));
      } else {
        setTasksState(prev => ({
          ...prev,
          loading: false,
          error: data.error || 'حدث خطأ في تحميل المهام'
        }));
      }
    } catch (err) {
      setTasksState(prev => ({
        ...prev,
        loading: false,
        error: 'فشل في الاتصال بالخادم'
      }));
      console.error('Tasks fetch error:', err);
    }
  };

  const handleCompleteTask = async (task: Task) => {
    if (!user?.telegram_id || completingTask) return;
    
    setCompletingTask(task.name);
    playSound && playSound('click');
    
    try {
      const response = await fetch('/api/tasks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: user.telegram_id,
          task_name: task.name
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        hapticFeedback?.success();
        playSound && playSound('success');
        
        // Refresh tasks list
        setTimeout(() => {
          fetchTasks();
        }, 1000);
        
      } else {
        hapticFeedback?.error();
        playSound && playSound('error');
        alert(data.error || 'فشل في إنجاز المهمة');
      }
    } catch (err) {
      hapticFeedback?.error();
      playSound && playSound('error');
      alert('حدث خطأ أثناء إنجاز المهمة');
      console.error('Task completion error:', err);
    } finally {
      setCompletingTask(null);
    }
  };

  const filteredTasks = tasksState.tasks.filter(task => {
    if (filter === 'all') return true;
    return task.type === filter;
  });

  const getTaskTypeColor = (type: string): string => {
    const colors: Record<string, string> = {
      'chat': 'text-blue-400',
      'activity': 'text-green-400',
      'referral': 'text-purple-400',
      'profile': 'text-orange-400',
      'achievement': 'text-yellow-400',
      'streak': 'text-red-400',
      'premium': 'text-indigo-400',
      'feedback': 'text-pink-400',
      'subject': 'text-teal-400'
    };
    return colors[type] || 'text-gray-400';
  };

  const getTaskTypeLabel = (type: string): string => {
    const labels: Record<string, string> = {
      'chat': '💬 دردشة',
      'activity': '📱 نشاط',
      'referral': '👥 إحالة',
      'profile': '📝 ملف شخصي',
      'achievement': '🏆 إنجاز',
      'streak': '🔥 سلسلة',
      'premium': '⭐ بريميوم',
      'feedback': '⭐ تقييم',
      'subject': '📚 مادة'
    };
    return labels[type] || type;
  };

  if (tasksState.loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-blue-900 flex items-center justify-center">
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
              <h1 className="text-2xl font-bold text-white">🎯 المهام</h1>
              <p className="text-gray-300 mt-1">أكمل المهام واحصل على النقاط!</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-primary-400">{user?.points || 0}</div>
              <div className="text-sm text-gray-400">نقطة</div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="bg-gray-800 mx-4 mt-4 rounded-xl shadow-md overflow-hidden">
        <div className="grid grid-cols-3 divide-x divide-gray-600">
          <div className="text-center py-4">
            <div className="text-2xl font-bold text-green-400">{tasksState.completedCount}</div>
            <div className="text-sm text-gray-400">مهمة مكتملة</div>
          </div>
          <div className="text-center py-4">
            <div className="text-2xl font-bold text-primary-400">{tasksState.availableCount}</div>
            <div className="text-sm text-gray-400">مهمة متاحة</div>
          </div>
          <div className="text-center py-4">
            <div className="text-2xl font-bold text-purple-400">{tasksState.completedCount + tasksState.availableCount}</div>
            <div className="text-sm text-gray-400">إجمالي المهام</div>
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="px-4 mt-4">
        <div className="bg-gray-800 rounded-xl shadow-md p-2">
          <div className="flex gap-2 overflow-x-auto">
            {[
              { key: 'all', label: 'الكل', icon: '📋' },
              { key: 'activity', label: 'نشاط', icon: '📱' },
              { key: 'chat', label: 'دردشة', icon: '💬' },
              { key: 'achievement', label: 'إنجازات', icon: '🏆' }
            ].map(({ key, label, icon }) => (
              <button
                key={key}
                onClick={() => {
                  setFilter(key as any);
                  hapticFeedback?.selection();
                  playSound && playSound('click');
                }}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${
                  filter === key
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

      {/* Tasks List */}
      <div className="px-4 py-4 space-y-3 pb-24">
        <AnimatePresence mode="wait">
          {tasksState.error ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="text-center py-8"
            >
              <div className="text-red-400 text-lg mb-2">❌ حدث خطأ</div>
              <p className="text-gray-300">{tasksState.error}</p>
              <Button
                onClick={fetchTasks}
                className="mt-4"
                variant="outline"
              >
                إعادة المحاولة
              </Button>
            </motion.div>
          ) : filteredTasks.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="text-center py-8"
            >
              <div className="text-6xl mb-4">🎉</div>
              <h3 className="text-xl font-semibold text-gray-200 mb-2">
                ممتاز! لا توجد مهام متاحة
              </h3>
              <p className="text-gray-400">
                لقد أكملت جميع المهام المتاحة في هذا التصنيف
              </p>
            </motion.div>
          ) : (
            filteredTasks.map((task, index) => (
              <motion.div
                key={task.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className="bg-gray-800 hover:bg-gray-750 border-gray-600 hover:border-primary-500 transition-all duration-300 border-r-4 border-primary-400">
                  <div className="flex items-center gap-4">
                    {/* Task Icon */}
                    <div className="text-4xl">
                      {task.icon}
                    </div>
                    
                    {/* Task Details */}
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-100 mb-1">
                        {task.title}
                      </h3>
                      <p className="text-gray-400 text-sm mb-2">
                        {task.description}
                      </p>
                      <div className="flex items-center gap-2">
                        <span className={`text-xs px-2 py-1 rounded-full bg-gray-700 ${getTaskTypeColor(task.type)}`}>
                          {getTaskTypeLabel(task.type)}
                        </span>
                        <span className="text-green-400 font-semibold text-sm">
                          +{task.points} نقطة
                        </span>
                      </div>
                    </div>
                    
                    {/* Complete Button */}
                    <div>
                      <Button
                        onClick={() => handleCompleteTask(task)}
                        disabled={completingTask === task.name}
                        className="bg-gradient-to-l from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white border-0 shadow-lg"
                        size="sm"
                      >
                        {completingTask === task.name ? (
                          <div className="flex items-center gap-2">
                            <LoadingSpinner size="sm" />
                            <span>جاري الإنجاز...</span>
                          </div>
                        ) : (
                          '✅ إنجاز'
                        )}
                      </Button>
                    </div>
                  </div>
                </Card>
              </motion.div>
            ))
          )}
        </AnimatePresence>

        {/* Progress Section */}
        {tasksState.completedCount > 0 && (
          <Card className="bg-gradient-to-r from-primary-500 to-primary-600 text-white border-0">
            <div className="text-center">
              <h3 className="font-semibold mb-2">🎉 إحصائياتك الرائعة!</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-2xl font-bold">{user?.points || 0}</div>
                  <div className="text-sm opacity-90">إجمالي النقاط</div>
                </div>
                <div>
                  <div className="text-2xl font-bold">{tasksState.completedCount}</div>
                  <div className="text-sm opacity-90">المهام المكتملة</div>
                </div>
              </div>
              <p className="text-sm mt-4 opacity-90">
                واصل التميز واحصل على المزيد من النقاط! 🚀
              </p>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};

export default TasksPage;