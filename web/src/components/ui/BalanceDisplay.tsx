import React from 'react';
import { motion } from 'framer-motion';
import { Gem, DollarSign } from 'lucide-react';
import { cn } from '@/utils/cn';

interface BalanceDisplayProps {
  points: number;
  riyal: number;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  showLabels?: boolean;
}

const BalanceDisplay: React.FC<BalanceDisplayProps> = ({
  points,
  riyal,
  className,
  size = 'md',
  showLabels = true
}) => {
  const sizeClasses = {
    sm: {
      container: 'gap-2',
      badge: 'px-3 py-1.5 text-sm',
      icon: 'w-4 h-4',
      text: 'text-sm'
    },
    md: {
      container: 'gap-3',
      badge: 'px-4 py-2 text-base',
      icon: 'w-5 h-5',
      text: 'text-base'
    },
    lg: {
      container: 'gap-4',
      badge: 'px-6 py-3 text-lg',
      icon: 'w-6 h-6',
      text: 'text-lg'
    }
  };

  const currentSize = sizeClasses[size];

  return (
    <div className={cn('flex items-center justify-center', currentSize.container, className)}>
      {/* Points Display */}
      <motion.div
        className={cn(
          'bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-full font-semibold shadow-lg flex items-center gap-2',
          currentSize.badge
        )}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <Gem className={cn('text-white', currentSize.icon)} />
        <span className={currentSize.text}>
          {points.toLocaleString('ar-SA')}
        </span>
        {showLabels && (
          <span className="opacity-80 text-xs">نقطة</span>
        )}
      </motion.div>

      {/* Riyal Display */}
      <motion.div
        className={cn(
          'bg-gradient-to-r from-gold-400 to-gold-500 text-gray-900 rounded-full font-semibold shadow-lg flex items-center gap-2',
          currentSize.badge
        )}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <DollarSign className={cn('text-gray-900', currentSize.icon)} />
        <span className={currentSize.text}>
          {riyal.toLocaleString('ar-SA')}
        </span>
        {showLabels && (
          <span className="opacity-80 text-xs">ريال</span>
        )}
      </motion.div>
    </div>
  );
};

export default BalanceDisplay;