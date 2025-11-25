import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, AlertCircle } from 'lucide-react';
import { useUserStore } from '@/store/userStore';
import { useChatStore, initializeChat } from '@/store/chatStore';
import { useTelegram } from '@/hooks/useTelegram';
import { useSound } from '@/hooks/useSound';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { ChatMessage } from '@/types';

const ChatPage: React.FC = () => {
  const { user } = useUserStore();
  const { messages, isTyping, isLoading, sendQuestion } = useChatStore();
  const { hapticFeedback } = useTelegram();
  const { playClickSound, playSuccessSound, playErrorSound } = useSound();
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Initialize chat on first load
  useEffect(() => {
    if (user && messages.length === 0) {
      initializeChat();
    }
  }, [user, messages.length]);

  // Auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const message = inputMessage.trim();
    setInputMessage('');
    
    hapticFeedback.impact('medium');
    playClickSound();

    try {
      await sendQuestion(message);
      playSuccessSound();
      hapticFeedback.notification('success');
    } catch (error) {
      playErrorSound();
      hapticFeedback.notification('error');
      console.error('Error sending message:', error);
    }

    // Focus back on input
    inputRef.current?.focus();
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const MessageBubble: React.FC<{ message: ChatMessage; index: number }> = ({ message, index }) => {
    const isUser = message.type === 'user';
    
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: index * 0.1 }}
        className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
      >
        <div className={`flex items-start gap-3 max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
          {/* Avatar */}
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
            isUser 
              ? 'bg-primary-500' 
              : message.isError 
                ? 'bg-red-500' 
                : 'bg-gold-400'
          }`}>
            {isUser ? (
              <User className="w-4 h-4 text-white" />
            ) : message.isError ? (
              <AlertCircle className="w-4 h-4 text-white" />
            ) : (
              <Bot className="w-4 h-4 text-gray-900" />
            )}
          </div>

          {/* Message Content */}
          <div className={`rounded-2xl px-4 py-3 ${
            isUser
              ? 'bg-primary-500 text-white'
              : message.isError
                ? 'bg-red-500/20 border border-red-500 text-red-300'
                : 'bg-gray-700 text-white'
          }`}>
            <div className="text-sm font-medium mb-1 opacity-75">
              {isUser ? user?.name || 'أنت' : message.isError ? 'خطأ' : 'منهج AI'}
            </div>
            <div className="whitespace-pre-wrap leading-relaxed">
              {message.content}
            </div>
            <div className="text-xs opacity-50 mt-2">
              {new Date(message.timestamp).toLocaleTimeString('ar-SA', {
                hour: '2-digit',
                minute: '2-digit'
              })}
            </div>
          </div>
        </div>
      </motion.div>
    );
  };

  const TypingIndicator: React.FC = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="flex justify-start mb-4"
    >
      <div className="flex items-start gap-3 max-w-[80%]">
        <div className="w-8 h-8 rounded-full bg-gold-400 flex items-center justify-center">
          <Bot className="w-4 h-4 text-gray-900" />
        </div>
        <div className="bg-gray-700 rounded-2xl px-4 py-3">
          <div className="text-sm font-medium mb-1 opacity-75">منهج AI</div>
          <div className="flex items-center gap-1">
            <span className="text-sm">يكتب</span>
            <div className="flex gap-1">
              <motion.div
                className="w-2 h-2 bg-primary-400 rounded-full"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ repeat: Infinity, duration: 1, delay: 0 }}
              />
              <motion.div
                className="w-2 h-2 bg-primary-400 rounded-full"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ repeat: Infinity, duration: 1, delay: 0.2 }}
              />
              <motion.div
                className="w-2 h-2 bg-primary-400 rounded-full"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ repeat: Infinity, duration: 1, delay: 0.4 }}
              />
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <Card className="text-center">
          <Bot className="w-12 h-12 text-gold-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-white mb-2">
            الدردشة الذكية
          </h2>
          <p className="text-gray-400">
            يرجى تسجيل الدخول أولاً للوصول للدردشة
          </p>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col">
      {/* Header */}
      <motion.header 
        className="bg-gray-800 border-b border-gray-700 p-4 safe-top"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-r from-primary-500 to-gold-400 rounded-full flex items-center justify-center">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-white">منهج AI الذكي</h1>
            <p className="text-sm text-gray-400">مساعدك التعليمي الشخصي</p>
          </div>
        </div>
      </motion.header>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
        <AnimatePresence>
          {messages.map((message, index) => (
            <MessageBubble 
              key={message.id} 
              message={message} 
              index={index}
            />
          ))}
          {isTyping && <TypingIndicator />}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <motion.div 
        className="bg-gray-800 border-t border-gray-700 p-4 safe-bottom"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-end gap-3">
          <div className="flex-1">
            <input
              ref={inputRef}
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="اكتب سؤالك هنا..."
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
              disabled={isLoading}
              autoComplete="off"
            />
          </div>
          <Button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="px-4 py-3 h-12"
          >
            {isLoading ? (
              <LoadingSpinner size="sm" color="white" />
            ) : (
              <Send className="w-5 h-5 rtl-flip" />
            )}
          </Button>
        </div>

        {/* Quick Suggestions */}
        {messages.length <= 1 && (
          <motion.div
            className="mt-3 flex flex-wrap gap-2"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            {[
              'اشرح لي الرياضيات',
              'ساعدني في الفيزياء',
              'أسئلة تاريخ',
              'قواعد اللغة العربية'
            ].map((suggestion) => (
              <motion.button
                key={suggestion}
                className="px-3 py-1 text-sm bg-gray-700 text-gray-300 rounded-full hover:bg-primary-500 hover:text-white transition-colors"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => {
                  setInputMessage(suggestion);
                  hapticFeedback.selection();
                }}
              >
                {suggestion}
              </motion.button>
            ))}
          </motion.div>
        )}
      </motion.div>
    </div>
  );
};

export default ChatPage;