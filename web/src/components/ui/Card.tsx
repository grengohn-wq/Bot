import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/utils/cn';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'glow' | 'glass';
  children: React.ReactNode;
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant = 'default', children, ...props }, ref) => {
    const baseClasses = "rounded-2xl p-6 shadow-2xl transition-all duration-300";
    
    const variants = {
      default: "bg-gray-800 border border-gray-700 backdrop-blur-sm",
      glow: "bg-gray-800 border border-gray-700 backdrop-blur-sm relative overflow-hidden hover:shadow-primary-500/20",
      glass: "glass-effect border border-white/10"
    };

    return (
      <motion.div
        ref={ref}
        className={cn(baseClasses, variants[variant], className)}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        whileHover={{ y: -2 }}
        transition={{ duration: 0.3 }}
        {...props}
      >
        {variant === 'glow' && (
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-primary-500/10 to-gold-400/10 opacity-0 hover:opacity-100 transition-opacity duration-300"
            layoutId="card-glow"
          />
        )}
        <div className="relative z-10">
          {children}
        </div>
      </motion.div>
    );
  }
);

Card.displayName = "Card";

export default Card;