import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Home, MessageCircle, Users, Trophy, Settings } from 'lucide-react';

// Hooks & Stores
import { useTelegram } from '@/hooks/useTelegram';
import { useUserStore } from '@/store/userStore';
import { useAppStore, initializeApp } from '@/store/appStore';

// Pages
import HomePage from '@/pages/HomePage';
import ChatPage from '@/pages/ChatPage';
import TasksPage from '@/pages/TasksPage';
import StatsPage from '@/pages/StatsPage';
import AdminPage from '@/pages/AdminPage';
import ComingSoonPage from '@/components/ComingSoonPage';

// Components
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { cn } from '@/utils/cn';

const App: React.FC = () => {
  const { user, isLoading, login, setLoading } = useUserStore();
  const { currentScreen, setCurrentScreen } = useAppStore();
  const { isReady, user: telegramUser, hapticFeedback, backButton } = useTelegram();
  const [isInitialized, setIsInitialized] = useState(false);

  // Initialize app
  useEffect(() => {
    const init = async () => {
      if (!isReady) return;

      try {
        setLoading(true);
        
        // Initialize app settings and data
        await initializeApp();
        
        // Auto login if telegram user is available
        if (telegramUser) {
          await login(telegramUser);
        }
        
        setIsInitialized(true);
        
      } catch (error) {
        console.error('App initialization error:', error);
      } finally {
        setLoading(false);
      }
    };

    init();
  }, [isReady, telegramUser, login, setLoading]);

  // Handle back button
  useEffect(() => {
    if (currentScreen !== 'home') {
      backButton.show(() => {
        setCurrentScreen('home');
        hapticFeedback.impact('light');
      });
    } else {
      backButton.hide();
    }

    return () => {
      backButton.hide();
    };
  }, [currentScreen, backButton, setCurrentScreen, hapticFeedback]);

  // Navigation items
  const navigationItems = [
    { id: 'home', icon: Home, label: 'الرئيسية' },
    { id: 'chat', icon: MessageCircle, label: 'الدردشة' },
    { id: 'referral', icon: Users, label: 'الإحالة' },
    { id: 'leaderboard', icon: Trophy, label: 'الترتيب' }
  ];

  const handleNavigation = (screen: string) => {
    if (screen !== currentScreen) {
      setCurrentScreen(screen);
      hapticFeedback.selection();
    }
  };

  // Loading state
  if (!isInitialized || isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <motion.div
            className="text-6xl mb-4"
            animate={{ rotate: [0, 360] }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          >
            🧠
          </motion.div>
          <h1 className="text-2xl font-bold text-gradient mb-4">منهج AI</h1>
          <LoadingSpinner size="lg" />
          <p className="text-gray-400 mt-4">جاري التحميل...</p>
        </div>
      </div>
    );
  }

  // Render current page
  const renderCurrentPage = () => {
    switch (currentScreen) {
      case 'home':
        return <HomePage />;
      case 'chat':
        return <ChatPage />;
      case 'points':
        return (
          <ComingSoonPage
            title="نظام النقاط والمدفوعات"
            description="صفحة إدارة النقاط وتحويلها لريال، بالإضافة لشراء البريميم وتحويل الأموال."
            icon="💎"
          />
        );
      case 'tasks':
        return <TasksPage />;
      case 'referral':
        return (
          <ComingSoonPage
            title="نظام الإحالة"
            description="ادع أصدقاءك واحصل على 100 نقطة لكل إحالة ناجحة."
            icon="👥"
          />
        );
      case 'leaderboard':
        return <StatsPage />;
      case 'admin':
        return user?.is_manager ? (
          <AdminPage />
        ) : <HomePage />;
      default:
        return <HomePage />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white font-arabic">
      {/* Main Content */}
      <main className="pb-20">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentScreen}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            {renderCurrentPage()}
          </motion.div>
        </AnimatePresence>
      </main>

      {/* Bottom Navigation */}
      <motion.nav
        className="fixed bottom-0 left-0 right-0 bg-gray-800 border-t border-gray-700 safe-bottom"
        initial={{ y: 100 }}
        animate={{ y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <div className="flex items-center justify-around px-4 py-2">
          {navigationItems.map((item, index) => {
            const Icon = item.icon;
            const isActive = currentScreen === item.id;
            
            return (
              <motion.button
                key={item.id}
                className={cn(
                  'flex flex-col items-center gap-1 p-2 rounded-lg transition-all duration-200',
                  isActive 
                    ? 'text-primary-400 bg-primary-500/10' 
                    : 'text-gray-400 hover:text-gray-300'
                )}
                onClick={() => handleNavigation(item.id)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                initial={{ y: 50, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.6 + index * 0.1 }}
              >
                <Icon className={cn('w-6 h-6', isActive && 'animate-bounce-slow')} />
                <span className="text-xs font-medium">{item.label}</span>
              </motion.button>
            );
          })}
        </div>
      </motion.nav>

      {/* Admin Access */}
      {user?.is_manager && currentScreen === 'home' && (
        <motion.button
          className="fixed top-4 left-4 bg-gray-800 text-gray-400 p-2 rounded-full border border-gray-600 shadow-lg"
          onClick={() => handleNavigation('admin')}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
        >
          <Settings className="w-5 h-5" />
        </motion.button>
      )}

      {/* Quick Chat Access */}
      <motion.div
        className="fixed top-4 right-4"
        initial={{ opacity: 0, scale: 0 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.8, type: "spring" }}
      >
        <button
          onClick={() => handleNavigation('chat')}
          className="bg-gradient-to-r from-primary-500 to-primary-600 text-white p-3 rounded-full shadow-lg hover:shadow-xl transform hover:scale-105 active:scale-95 transition-all duration-200"
        >
          <MessageCircle className="w-6 h-6" />
        </button>
      </motion.div>

      {/* Version Info */}
      <div className="fixed bottom-20 right-4 text-xs text-gray-500 opacity-50">
        v2.0
      </div>
    </div>
  );
};

export default App;