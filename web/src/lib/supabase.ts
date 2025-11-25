import { createClient } from '@supabase/supabase-js';

// Supabase configuration
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://your-project.supabase.co';
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'your-anon-key';

// Create Supabase client
export const supabase = createClient(supabaseUrl, supabaseKey);

// Database table names
export const TABLES = {
  STUDENTS: 'students',
  QUESTIONS: 'questions',
  TASKS: 'tasks',
  COMPLETED_TASKS: 'completed_tasks',
  TRANSFERS: 'transfers',
  SUPPORT_MESSAGES: 'support_messages',
  ADMINS: 'admins',
  APP_SETTINGS: 'app_settings'
} as const;

// Database functions
export const dbFunctions = {
  // Get user by telegram ID
  async getUserByTelegramId(telegramId: number) {
    const { data, error } = await supabase
      .from(TABLES.STUDENTS)
      .select('*')
      .eq('telegram_id', telegramId)
      .single();
    
    if (error && error.code !== 'PGRST116') {
      console.error('Error fetching user:', error);
      return null;
    }
    
    return data;
  },

  // Create new user
  async createUser(userData: {
    telegram_id: number;
    name: string;
    education_stage: string;
    country: string;
    verification_code: string;
    referral_code?: string;
  }) {
    const { data, error } = await supabase
      .from(TABLES.STUDENTS)
      .insert([userData])
      .select()
      .single();
    
    if (error) {
      console.error('Error creating user:', error);
      return null;
    }
    
    return data;
  },

  // Update user points
  async updateUserPoints(telegramId: number, pointsToAdd: number) {
    // First get current points
    const { data: current } = await supabase
      .from(TABLES.STUDENTS)
      .select('points')
      .eq('telegram_id', telegramId)
      .single();
    
    if (!current) return null;
    
    const { data, error } = await supabase
      .from(TABLES.STUDENTS)
      .update({ 
        points: current.points + pointsToAdd,
        updated_at: new Date().toISOString()
      })
      .eq('telegram_id', telegramId)
      .select()
      .single();
    
    if (error) {
      console.error('Error updating points:', error);
      return null;
    }
    
    return data;
  },

  // Convert points to riyal
  async convertPointsToRiyal(telegramId: number, points: number) {
    if (points < 100) {
      throw new Error('الحد الأدنى للتحويل 100 نقطة');
    }

    const riyal = Math.floor(points / 100);
    
    // Get current values first
    const { data: current } = await supabase
      .from(TABLES.STUDENTS)
      .select('points, riyal')
      .eq('telegram_id', telegramId)
      .single();

    if (!current || current.points < points) {
      throw new Error('رصيد النقاط غير كافي');
    }

    const { data, error } = await supabase
      .from(TABLES.STUDENTS)
      .update({
        points: current.points - points,
        riyal: current.riyal + riyal,
        updated_at: new Date().toISOString()
      })
      .eq('telegram_id', telegramId)
      .select()
      .single();

    if (error) {
      console.error('Error converting points:', error);
      throw new Error('فشل في تحويل النقاط');
    }

    if (!data) {
      throw new Error('رصيد النقاط غير كافي');
    }

    return { success: true, riyal, data };
  },

  // Transfer riyal
  async transferRiyal(senderTelegramId: number, receiverCode: string, amount: number) {
    // First, find the receiver
    const { data: receiver, error: receiverError } = await supabase
      .from(TABLES.STUDENTS)
      .select('telegram_id, name')
      .eq('verification_code', receiverCode)
      .single();

    if (receiverError || !receiver) {
      throw new Error('لم يتم العثور على المستلم');
    }

    // Perform the transfer in a transaction-like manner
    // Get sender's current balance first
    const { data: senderInfo, error: senderInfoError } = await supabase
      .from(TABLES.STUDENTS)
      .select('riyal')
      .eq('telegram_id', senderTelegramId)
      .single();

    if (senderInfoError || !senderInfo || senderInfo.riyal < amount) {
      throw new Error('رصيد الريال غير كافي');
    }

    const { data: sender, error: senderError } = await supabase
      .from(TABLES.STUDENTS)
      .update({
        riyal: senderInfo.riyal - amount,
        updated_at: new Date().toISOString()
      })
      .eq('telegram_id', senderTelegramId)
      .select()
      .single();

    if (senderError || !sender) {
      throw new Error('رصيد الريال غير كافي');
    }

    // Update receiver
    const { data: receiverInfo, error: receiverInfoError } = await supabase
      .from(TABLES.STUDENTS)
      .select('riyal')
      .eq('telegram_id', receiver.telegram_id)
      .single();

    if (receiverInfoError || !receiverInfo) {
      // Rollback sender update
      await supabase
        .from(TABLES.STUDENTS)
        .update({
          riyal: senderInfo.riyal,
          updated_at: new Date().toISOString()
        })
        .eq('telegram_id', senderTelegramId);
      
      throw new Error('فشل في العثور على المستلم');
    }

    const { error: receiverUpdateError } = await supabase
      .from(TABLES.STUDENTS)
      .update({
        riyal: receiverInfo.riyal + amount,
        updated_at: new Date().toISOString()
      })
      .eq('telegram_id', receiver.telegram_id);

    if (receiverUpdateError) {
      // Rollback sender update
      await supabase
        .from(TABLES.STUDENTS)
        .update({
          riyal: senderInfo.riyal,
          updated_at: new Date().toISOString()
        })
        .eq('telegram_id', senderTelegramId);
      
      throw new Error('فشل في إتمام التحويل');
    }

    // Record the transfer
    await supabase
      .from(TABLES.TRANSFERS)
      .insert([{
        sender_id: senderTelegramId,
        receiver_id: receiver.telegram_id,
        amount,
        transfer_type: 'riyal'
      }]);

    return { success: true, receiverName: receiver.name, data: sender };
  },

  // Buy premium
  async buyPremium(telegramId: number) {
    // Get current riyal first
    const { data: current } = await supabase
      .from(TABLES.STUDENTS)
      .select('riyal')
      .eq('telegram_id', telegramId)
      .single();

    if (!current || current.riyal < 10) {
      throw new Error('رصيد الريال غير كافي');
    }

    const { data, error } = await supabase
      .from(TABLES.STUDENTS)
      .update({
        riyal: current.riyal - 10,
        is_premium: true,
        ads_response_count: 0,
        updated_at: new Date().toISOString()
      })
      .eq('telegram_id', telegramId)
      .select()
      .single();

    if (error || !data) {
      throw new Error('رصيد الريال غير كافي');
    }

    return data;
  },

  // Get available tasks for user
  async getAvailableTasks(telegramId: number) {
    const { data, error } = await supabase
      .from(TABLES.TASKS)
      .select(`
        *,
        completion_count:completed_tasks(count)
      `)
      .eq('is_active', true)
      .not('id', 'in', 
        supabase
          .from(TABLES.COMPLETED_TASKS)
          .select('task_id')
          .eq('user_id', telegramId)
      );

    if (error) {
      console.error('Error fetching tasks:', error);
      return [];
    }

    return data || [];
  },

  // Complete task
  async completeTask(telegramId: number, taskId: number) {
    // First check if task is already completed
    const { data: existingCompletion } = await supabase
      .from(TABLES.COMPLETED_TASKS)
      .select('id')
      .eq('user_id', telegramId)
      .eq('task_id', taskId)
      .single();

    if (existingCompletion) {
      throw new Error('تم إنجاز هذه المهمة مسبقاً');
    }

    // Get task points
    const { data: task, error: taskError } = await supabase
      .from(TABLES.TASKS)
      .select('points')
      .eq('id', taskId)
      .eq('is_active', true)
      .single();

    if (taskError || !task) {
      throw new Error('مهمة غير صالحة');
    }

    // Mark task as completed
    const { error: completionError } = await supabase
      .from(TABLES.COMPLETED_TASKS)
      .insert([{
        user_id: telegramId,
        task_id: taskId
      }]);

    if (completionError) {
      throw new Error('فشل في تسجيل إنجاز المهمة');
    }

    // Add points to user
    const updatedUser = await this.updateUserPoints(telegramId, task.points);

    return { success: true, points: task.points, user: updatedUser };
  },

  // Record question
  async recordQuestion(telegramId: number, question: string) {
    // Get current counts first
    const { data: current } = await supabase
      .from(TABLES.STUDENTS)
      .select('questions_count, ads_response_count')
      .eq('telegram_id', telegramId)
      .single();

    if (current) {
      // Update user stats
      await supabase
        .from(TABLES.STUDENTS)
        .update({
          questions_count: current.questions_count + 1,
          ads_response_count: current.ads_response_count + 1,
          last_activity: new Date().toISOString(),
          updated_at: new Date().toISOString()
        })
        .eq('telegram_id', telegramId);
    }

    // Record question
    const { error } = await supabase
      .from(TABLES.QUESTIONS)
      .insert([{
        user_id: telegramId,
        question,
        question_type: 'general'
      }]);

    if (error) {
      console.error('Error recording question:', error);
    }
  },

  // Get leaderboard
  async getLeaderboard(limit: number = 100) {
    const { data, error } = await supabase
      .from(TABLES.STUDENTS)
      .select('name, points, riyal, successful_referrals, questions_count')
      .order('points', { ascending: false })
      .limit(limit);

    if (error) {
      console.error('Error fetching leaderboard:', error);
      return [];
    }

    return data?.map((item, index) => ({
      ...item,
      rank: index + 1
    })) || [];
  },

  // Get app statistics
  async getAppStatistics() {
    const { data, error } = await supabase
      .from('app_statistics')
      .select('*')
      .single();

    if (error) {
      console.error('Error fetching statistics:', error);
      return null;
    }

    return data;
  },

  // Send support message
  async sendSupportMessage(telegramId: number, message: string) {
    const { data, error } = await supabase
      .from(TABLES.SUPPORT_MESSAGES)
      .insert([{
        user_id: telegramId,
        message
      }])
      .select()
      .single();

    if (error) {
      console.error('Error sending support message:', error);
      throw new Error('فشل في إرسال الرسالة');
    }

    return data;
  },

  // Get app settings
  async getAppSettings() {
    const { data, error } = await supabase
      .from(TABLES.APP_SETTINGS)
      .select('setting_key, setting_value');

    if (error) {
      console.error('Error fetching settings:', error);
      return {};
    }

    const settings: Record<string, string> = {};
    data?.forEach(setting => {
      settings[setting.setting_key] = setting.setting_value;
    });

    return settings;
  }
};

export default supabase;