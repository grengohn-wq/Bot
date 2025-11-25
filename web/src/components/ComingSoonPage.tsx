import React from 'react';
import { motion } from 'framer-motion';
import { Construction } from 'lucide-react';
import Card from '@/components/ui/Card';

interface ComingSoonPageProps {
  title: string;
  description: string;
  icon?: React.ReactNode;
}

const ComingSoonPage: React.FC<ComingSoonPageProps> = ({ title, description, icon }) => {
  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center max-w-md"
      >
        <Card className="text-center">
          <motion.div
            className="text-6xl mb-6"
            animate={{ 
              rotate: [0, 10, -10, 0],
              scale: [1, 1.1, 1]
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          >
            {icon || <Construction className="w-16 h-16 text-gold-400 mx-auto" />}
          </motion.div>
          
          <h1 className="text-2xl font-bold text-white mb-4">
            {title}
          </h1>
          
          <p className="text-gray-400 mb-6 leading-relaxed">
            {description}
          </p>
          
          <motion.div
            className="bg-primary-500/10 border border-primary-500/20 rounded-xl p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            <p className="text-primary-400 font-semibold text-sm">
              🚀 قريباً جداً
            </p>
            <p className="text-gray-500 text-xs mt-1">
              نعمل على تطوير هذه الميزة بأفضل جودة ممكنة
            </p>
          </motion.div>
        </Card>
      </motion.div>
    </div>
  );
};

export default ComingSoonPage;