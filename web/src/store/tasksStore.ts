import { create } from 'zustand';
import { TasksStore } from '@/types';
import { dbFunctions } from '@/lib/supabase';
import { useUserStore } from './userStore';

export const useTasksStore = create<TasksStore>((set, get) => ({
  tasks: [],
  completedTaskIds: [],
  isLoading: false,

  setTasks: (tasks) => {
    set({ tasks });
  },

  setCompletedTasks: (taskIds) => {
    set({ completedTaskIds: taskIds });
  },

  setLoading: (loading) => {
    set({ isLoading: loading });
  },

  completeTask: async (taskId) => {
    const { user } = useUserStore.getState();
    if (!user) {
      throw new Error('المستخدم غير مسجل الدخول');
    }

    set({ isLoading: true });

    try {
      const result = await dbFunctions.completeTask(user.telegram_id, taskId);
      
      if (result.success) {
        // Update completed tasks list
        const { completedTaskIds } = get();
        set({ completedTaskIds: [...completedTaskIds, taskId] });
        
        // Update user points in user store
        useUserStore.getState().updateUser({ 
          points: result.user?.points || user.points + result.points 
        });
        
        // Telegram WebApp haptic feedback
        if (window.Telegram?.WebApp?.HapticFeedback) {
          window.Telegram.WebApp.HapticFeedback.notificationOccurred('success');
        }
        
        // Play cash sound effect (if available)
        try {
          const audio = new Audio('/sounds/cash.mp3');
          audio.volume = 0.3;
          audio.play().catch(() => {}); // Ignore audio errors
        } catch {}
        
        set({ isLoading: false });
        return true;
      }
      
      set({ isLoading: false });
      return false;
      
    } catch (error) {
      console.error('Error completing task:', error);
      
      // Telegram WebApp haptic feedback for error
      if (window.Telegram?.WebApp?.HapticFeedback) {
        window.Telegram.WebApp.HapticFeedback.notificationOccurred('error');
      }
      
      set({ isLoading: false });
      throw error;
    }
  }
}));

// Load user's tasks
export const loadUserTasks = async () => {
  const { user } = useUserStore.getState();
  if (!user) return;

  const { setTasks, setCompletedTasks, setLoading } = useTasksStore.getState();
  
  setLoading(true);
  
  try {
    // Get available tasks
    const tasks = await dbFunctions.getAvailableTasks(user.telegram_id);
    setTasks(tasks);
    
    // Get completed task IDs from the tasks that are NOT available
    const allTasks = await dbFunctions.getAvailableTasks(0); // Get all tasks
    const availableTaskIds = tasks.map(t => t.id);
    const completedTaskIds = allTasks
      .filter(t => !availableTaskIds.includes(t.id))
      .map(t => t.id);
    
    setCompletedTasks(completedTaskIds);
    
  } catch (error) {
    console.error('Error loading tasks:', error);
  } finally {
    setLoading(false);
  }
};