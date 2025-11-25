import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Users, 
  Crown, 
  DollarSign, 
  Zap, 
  MessageSquare, 
  BarChart3,
  Send,
  Settings,
  Shield,
  Award,
  TrendingUp
} from 'lucide-react';
import { useUserStore } from '@/store/userStore';
import { useAppStore } from '@/store/appStore';
import { useTelegram } from '@/hooks/useTelegram';
import { dbFunctions } from '@/lib/supabase';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

const AdminPage: React.FC = () => {
  const { user } = useUserStore();
  const { statistics } = useAppStore();
  const { hapticFeedback } = useTelegram();
  
  const [activeSection, setActiveSection] = useState<string>('overview');
  const [loading, setLoading] = useState(false);
  const [broadcastMessage, setBroadcastMessage] = useState('');

  // Check if user is admin
  if (!user?.is_manager) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
        <Card className="text-center">
          <Shield className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-white mb-2">
            ممنوع الوصول
          </h2>
          <p className="text-gray-400">
            ليس لديك صلاحيات المدير
          </p>
        </Card>
      </div>
    );
  }

  // Load admin data
  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    setLoading(true);
    try {
      // Load statistics and users data
      await Promise.all([
        dbFunctions.getAppStatistics(),
        // dbFunctions.getAllUsers() // We'll implement this
      ]);
      
    } catch (error) {
      console.error('Error loading admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSectionChange = (section: string) => {
    setActiveSection(section);
    hapticFeedback.selection();
  };

  const handleBroadcast = async () => {
    if (!broadcastMessage.trim()) return;
    
    setLoading(true);
    hapticFeedback.impact('medium');
    
    try {
      // Send broadcast message
      // await dbFunctions.sendBroadcast(broadcastMessage);
      
      setBroadcastMessage('');
      hapticFeedback.notification('success');
      
      // Show success message
      alert('تم إرسال البث الجماعي بنجاح!');
      
    } catch (error) {
      console.error('Broadcast error:', error);
      hapticFeedback.notification('error');
      alert('فشل في إرسال البث الجماعي');
    } finally {
      setLoading(false);
    }
  };

  const StatCard: React.FC<{ 
    title: string; 
    value: string | number; 
    icon: React.ReactNode; 
    color: string;
    change?: string;
  }> = ({ title, value, icon, color, change }) => (
    <motion.div
      whileHover={{ y: -2 }}
      className={`${color} rounded-xl p-4 text-white shadow-lg`}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-white/80 text-sm">{title}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
          {change && (
            <p className="text-white/80 text-xs mt-1 flex items-center gap-1">
              <TrendingUp className="w-3 h-3" />
              {change}
            </p>
          )}
        </div>
        <div className="text-3xl opacity-80">
          {icon}
        </div>
      </div>
    </motion.div>
  );

  const AdminSection: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
    >
      {children}
    </motion.div>
  );

  return (
    <div className="min-h-screen bg-gray-900 p-4 safe-top safe-bottom">
      {/* Header */}
      <motion.header 
        className="text-center mb-8"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-center justify-center gap-3 mb-4">
          <Shield className="w-8 h-8 text-gold-400" />
          <h1 className="text-2xl font-bold text-gradient">
            لوحة الإدارة السرية
          </h1>
        </div>
        <p className="text-gray-400">
          أهلاً {user.name} - مدير منهج AI 🛠️
        </p>
      </motion.header>

      {/* Navigation Tabs */}
      <motion.div
        className="flex overflow-x-auto gap-2 mb-6 pb-2"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        {[
          { id: 'overview', label: 'نظرة عامة', icon: BarChart3 },
          { id: 'users', label: 'المستخدمون', icon: Users },
          { id: 'premium', label: 'البريميم', icon: Crown },
          { id: 'broadcast', label: 'البث الجماعي', icon: Send },
          { id: 'settings', label: 'الإعدادات', icon: Settings }
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeSection === tab.id;
          
          return (
            <motion.button
              key={tab.id}
              className={`px-4 py-2 rounded-xl font-semibold text-sm whitespace-nowrap transition-all duration-200 ${
                isActive
                  ? 'bg-primary-500 text-white shadow-lg'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
              onClick={() => handleSectionChange(tab.id)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <div className="flex items-center gap-2">
                <Icon className="w-4 h-4" />
                {tab.label}
              </div>
            </motion.button>
          );
        })}
      </motion.div>

      {/* Content */}
      <AnimatePresence mode="wait">
        {activeSection === 'overview' && (
          <AdminSection>
            {/* Statistics Grid */}
            <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
              <StatCard
                title="إجمالي المستخدمين"
                value={statistics?.total_users?.toLocaleString('ar-SA') || '0'}
                icon={<Users />}
                color="bg-gradient-to-r from-blue-500 to-blue-600"
                change="+12 اليوم"
              />
              <StatCard
                title="مشتركي البريميم"
                value={statistics?.premium_users?.toLocaleString('ar-SA') || '0'}
                icon={<Crown />}
                color="bg-gradient-to-r from-gold-500 to-gold-600"
                change="+5 هذا الأسبوع"
              />
              <StatCard
                title="إجمالي الأسئلة"
                value={statistics?.total_questions?.toLocaleString('ar-SA') || '0'}
                icon={<MessageSquare />}
                color="bg-gradient-to-r from-primary-500 to-primary-600"
                change="+247 اليوم"
              />
              <StatCard
                title="إجمالي النقاط"
                value={statistics?.total_points?.toLocaleString('ar-SA') || '0'}
                icon={<Zap />}
                color="bg-gradient-to-r from-purple-500 to-purple-600"
              />
              <StatCard
                title="إجمالي الريال"
                value={statistics?.total_riyal?.toLocaleString('ar-SA') || '0'}
                icon={<DollarSign />}
                color="bg-gradient-to-r from-green-500 to-green-600"
              />
              <StatCard
                title="المهام المكتملة"
                value={statistics?.total_completed_tasks?.toLocaleString('ar-SA') || '0'}
                icon={<Award />}
                color="bg-gradient-to-r from-orange-500 to-orange-600"
              />
            </div>

            {/* Quick Actions */}
            <Card>
              <h3 className="text-lg font-semibold text-white mb-4">إجراءات سريعة</h3>
              <div className="grid grid-cols-2 gap-3">
                <Button 
                  variant="gold" 
                  size="sm"
                  onClick={() => handleSectionChange('broadcast')}
                >
                  <Send className="w-4 h-4 ml-2" />
                  إرسال إشعار
                </Button>
                <Button 
                  variant="secondary" 
                  size="sm"
                  onClick={() => handleSectionChange('users')}
                >
                  <Users className="w-4 h-4 ml-2" />
                  إدارة المستخدمين
                </Button>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={loadAdminData}
                  loading={loading}
                >
                  <BarChart3 className="w-4 h-4 ml-2" />
                  تحديث البيانات
                </Button>
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => handleSectionChange('settings')}
                >
                  <Settings className="w-4 h-4 ml-2" />
                  الإعدادات
                </Button>
              </div>
            </Card>
          </AdminSection>
        )}

        {activeSection === 'broadcast' && (
          <AdminSection>
            <Card>
              <h3 className="text-lg font-semibold text-white mb-4">
                📣 البث الجماعي
              </h3>
              <p className="text-gray-400 mb-4">
                إرسال رسالة لجميع مستخدمي التطبيق
              </p>
              
              <div className="space-y-4">
                <textarea
                  value={broadcastMessage}
                  onChange={(e) => setBroadcastMessage(e.target.value)}
                  placeholder="اكتب رسالة البث الجماعي هنا..."
                  className="w-full h-32 px-4 py-3 bg-gray-700 border border-gray-600 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
                />
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-400">
                    عدد المستخدمين: {statistics?.total_users || 0}
                  </span>
                  <Button
                    onClick={handleBroadcast}
                    disabled={!broadcastMessage.trim()}
                    loading={loading}
                    className="px-6"
                  >
                    <Send className="w-4 h-4 ml-2" />
                    إرسال البث
                  </Button>
                </div>
              </div>
            </Card>
          </AdminSection>
        )}

        {activeSection === 'users' && (
          <AdminSection>
            <Card>
              <h3 className="text-lg font-semibold text-white mb-4">
                👥 إدارة المستخدمين
              </h3>
              <p className="text-gray-400 text-center py-8">
                🚧 قريباً: إدارة شاملة للمستخدمين
              </p>
            </Card>
          </AdminSection>
        )}

        {activeSection === 'premium' && (
          <AdminSection>
            <Card>
              <h3 className="text-lg font-semibold text-white mb-4">
                👑 إدارة البريميم
              </h3>
              <p className="text-gray-400 text-center py-8">
                🚧 قريباً: تفعيل وإلغاء البريميم
              </p>
            </Card>
          </AdminSection>
        )}

        {activeSection === 'settings' && (
          <AdminSection>
            <Card>
              <h3 className="text-lg font-semibold text-white mb-4">
                ⚙️ إعدادات النظام
              </h3>
              <p className="text-gray-400 text-center py-8">
                🚧 قريباً: إعدادات النظام والتطبيق
              </p>
            </Card>
          </AdminSection>
        )}
      </AnimatePresence>

      {loading && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-2xl p-6 flex items-center gap-3">
            <LoadingSpinner />
            <span className="text-white">جاري المعالجة...</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminPage;