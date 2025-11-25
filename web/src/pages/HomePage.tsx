import React from 'react';
import { motion } from 'framer-motion';
import { 
  Brain, 
  MessageCircle, 
  Users, 
  Trophy, 
  Target, 
  Zap,
  Crown,
  Gift
} from 'lucide-react';
import { useUserStore } from '@/store/userStore';
import { useAppStore } from '@/store/appStore';
import { useTelegram } from '@/hooks/useTelegram';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import BalanceDisplay from '@/components/ui/BalanceDisplay';

const HomePage: React.FC = () => {
  const { user } = useUserStore();
  const { setCurrentScreen, statistics } = useAppStore();
  const { hapticFeedback, openTelegramLink } = useTelegram();

  const handleNavigate = (screen: string) => {
    hapticFeedback.selection();
    setCurrentScreen(screen);
  };

  const handleOpenBot = () => {
    hapticFeedback.impact();
    openTelegramLink('https://t.me/manhaj_ai_bot');
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <Card className="text-center max-w-md">
          <div className="text-6xl mb-4">🧠</div>
          <h2 className="text-2xl font-bold text-gradient mb-4">
            منهج AI
          </h2>
          <p className="text-gray-400 mb-6">
            يرجى تسجيل الدخول أولاً عبر البوت
          </p>
          <Button onClick={handleOpenBot} className="w-full">
            فتح البوت
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 p-4 safe-top safe-bottom">
      {/* Header */}
      <motion.header 
        className="text-center mb-8"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-center justify-center gap-3 mb-4">
          <motion.div
            className="text-4xl"
            animate={{ rotate: [0, 360] }}
            transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
          >
            🧠
          </motion.div>
          <h1 className="text-3xl font-bold text-gradient">
            منهج AI
          </h1>
        </div>
        
        <p className="text-gray-400 mb-6">
          ياهلا يا بطل {user.name}! دراستك بذكاء 🌟
        </p>

        {/* Balance Display */}
        <BalanceDisplay 
          points={user.points} 
          riyal={user.riyal} 
          className="mb-6"
        />

        {/* Premium Status */}
        {user.is_premium && (
          <motion.div
            className="inline-flex items-center gap-2 bg-gradient-to-r from-gold-500 to-gold-600 text-gray-900 px-4 py-2 rounded-full font-semibold shadow-lg mb-4"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.5, type: "spring" }}
          >
            <Crown className="w-5 h-5" />
            عضو بريميم
            {user.is_gift_premium && (
              <Gift className="w-4 h-4" />
            )}
          </motion.div>
        )}
      </motion.header>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 gap-4 mb-8">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="text-center cursor-pointer hover:scale-105" onClick={handleOpenBot}>
            <MessageCircle className="w-8 h-8 text-primary-500 mx-auto mb-3" />
            <h3 className="font-semibold text-white">الدردشة مع البوت</h3>
            <p className="text-sm text-gray-400 mt-1">اسأل أي سؤال منهجي</p>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card className="text-center cursor-pointer hover:scale-105" onClick={() => handleNavigate('chat')}>
            <Brain className="w-8 h-8 text-gold-400 mx-auto mb-3" />
            <h3 className="font-semibold text-white">الدردشة الذكية</h3>
            <p className="text-sm text-gray-400 mt-1">AI مدمج بالتطبيق</p>
          </Card>
        </motion.div>
      </div>

      {/* Main Features Grid */}
      <div className="grid grid-cols-1 gap-4 mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card variant="glow" className="cursor-pointer" onClick={() => handleNavigate('points')}>
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-white mb-1">نظام النقاط والمكافآت</h3>
                <p className="text-gray-400 text-sm">اكسب النقاط وحولها لريال سعودي</p>
              </div>
              <Zap className="w-8 h-8 text-primary-500" />
            </div>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card variant="glow" className="cursor-pointer" onClick={() => handleNavigate('tasks')}>
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-white mb-1">المهام والتحديات</h3>
                <p className="text-gray-400 text-sm">أكمل المهام واحصل على نقاط</p>
              </div>
              <Target className="w-8 h-8 text-gold-400" />
            </div>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <Card variant="glow" className="cursor-pointer" onClick={() => handleNavigate('referral')}>
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-white mb-1">نظام الإحالة</h3>
                <p className="text-gray-400 text-sm">ادع أصدقاءك واحصل على 100 نقطة</p>
                <div className="text-primary-400 font-semibold text-sm mt-1">
                  {user.successful_referrals} إحالة ناجحة
                </div>
              </div>
              <Users className="w-8 h-8 text-primary-500" />
            </div>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
        >
          <Card variant="glow" className="cursor-pointer" onClick={() => handleNavigate('leaderboard')}>
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-white mb-1">لوحة الترتيب</h3>
                <p className="text-gray-400 text-sm">تنافس مع الطلاب الآخرين</p>
              </div>
              <Trophy className="w-8 h-8 text-gold-400" />
            </div>
          </Card>
        </motion.div>
      </div>

      {/* Statistics */}
      {statistics && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
        >
          <Card className="text-center">
            <h3 className="text-lg font-semibold text-white mb-4">إحصائيات التطبيق</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <div className="text-2xl font-bold text-primary-400">
                  {statistics.total_users?.toLocaleString('ar-SA')}
                </div>
                <div className="text-gray-400">مستخدم</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-gold-400">
                  {statistics.total_questions?.toLocaleString('ar-SA')}
                </div>
                <div className="text-gray-400">سؤال</div>
              </div>
            </div>
          </Card>
        </motion.div>
      )}

      {/* User Stats */}
      <motion.div
        className="mt-6 text-center text-gray-400 text-sm"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
      >
        <p>
          عدد أسئلتك: {user.questions_count?.toLocaleString('ar-SA') || 0} • 
          عضو منذ: {new Date(user.created_at).toLocaleDateString('ar-SA')}
        </p>
      </motion.div>
    </div>
  );
};

export default HomePage;