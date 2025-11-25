import { create } from 'zustand';
import { ChatStore, ChatMessage } from '@/types';
import { useUserStore } from './userStore';
import { dbFunctions } from '@/lib/supabase';

export const useChatStore = create<ChatStore>((set, get) => ({
  messages: [],
  isTyping: false,
  isLoading: false,

  addMessage: (message) => {
    const { messages } = get();
    set({ messages: [...messages, message] });
  },

  setTyping: (typing) => {
    set({ isTyping: typing });
  },

  setLoading: (loading) => {
    set({ isLoading: loading });
  },

  sendQuestion: async (question) => {
    const { addMessage, setTyping, setLoading } = get();
    const { user } = useUserStore.getState();

    if (!user) {
      addMessage({
        id: Date.now().toString(),
        type: 'bot',
        content: 'يرجى تسجيل الدخول أولاً',
        timestamp: Date.now(),
        isError: true
      });
      return;
    }

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: question,
      timestamp: Date.now()
    };
    addMessage(userMessage);

    setLoading(true);
    setTyping(true);

    try {
      // Record question in database
      await dbFunctions.recordQuestion(user.telegram_id, question);

      // Check if user needs to see ad
      if (!user.is_premium && user.ads_response_count >= 2) {
        const adMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: 'bot',
          content: `🛑 **نحتاج دعمك (إعلان):**

أنت بحاجة لدعم البوت لتمويل استمرار الخدمة.

يمكنك شراء البريميم لإزالة الإعلانات تماماً، أو مشاهدة إعلان سريع.

للعودة للبوت واستكمال السؤال، اضغط على الزر "الدردشة مع البوت" في الأعلى.`,
          timestamp: Date.now() + 1
        };
        addMessage(adMessage);
        setLoading(false);
        setTyping(false);
        return;
      }

      // Call AI through our API
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question,
          user_id: user.telegram_id,
          user_name: user.name,
          education_stage: user.education_stage,
          country: user.country
        })
      });

      const data = await response.json();

      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: data.success 
          ? data.answer 
          : 'آسف، حدث خطأ في معالجة سؤالك. حاول مرة أخرى.',
        timestamp: Date.now() + 1,
        isError: !data.success
      };

      addMessage(botMessage);

      // Haptic feedback
      if (window.Telegram?.WebApp?.HapticFeedback) {
        window.Telegram.WebApp.HapticFeedback.notificationOccurred(
          data.success ? 'success' : 'error'
        );
      }

    } catch (error) {
      console.error('Error sending question:', error);
      
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: 'حدث خطأ في الاتصال. تحقق من الإنترنت وحاول مرة أخرى.',
        timestamp: Date.now() + 1,
        isError: true
      };
      addMessage(errorMessage);

      // Error haptic feedback
      if (window.Telegram?.WebApp?.HapticFeedback) {
        window.Telegram.WebApp.HapticFeedback.notificationOccurred('error');
      }
    } finally {
      setLoading(false);
      setTyping(false);
    }
  },

  clearMessages: () => {
    set({ messages: [] });
  }
}));

// Load initial chat messages
export const initializeChat = () => {
  const { addMessage } = useChatStore.getState();
  const { user } = useUserStore.getState();

  if (user) {
    const welcomeMessage: ChatMessage = {
      id: 'welcome',
      type: 'bot',
      content: `🎓 أهلاً بك ${user.name}!

أنا مساعدك الذكي في منهج AI. يمكنني مساعدتك في:

📚 الإجابة على أسئلة المناهج الدراسية
🎯 شرح المفاهيم المعقدة
📝 مساعدتك في الواجبات والمراجعة
💡 تقديم نصائح دراسية مخصصة

اكتب سؤالك وسأجيبك فوراً بإجابة منهجية دقيقة!`,
      timestamp: Date.now()
    };
    
    addMessage(welcomeMessage);
  }
};