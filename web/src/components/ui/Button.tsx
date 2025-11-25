import React from 'react';
import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';
import { cn } from '@/utils/cn';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'gold' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  icon?: LucideIcon;
  iconPosition?: 'left' | 'right';
  loading?: boolean;
  children: React.ReactNode;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ 
    className, 
    variant = 'primary', 
    size = 'md', 
    icon: Icon, 
    iconPosition = 'left',
    loading = false,
    children, 
    disabled,
    ...props 
  }, ref) => {
    const baseClasses = cn(
      "inline-flex items-center justify-center rounded-xl font-semibold transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900",
      "transform active:scale-95 hover:scale-105",
      "tap-highlight-none"
    );

    const variants = {
      primary: "bg-gradient-to-r from-primary-500 to-primary-600 text-white hover:from-primary-600 hover:to-primary-700 shadow-lg hover:shadow-xl focus:ring-primary-500",
      secondary: "bg-gray-700 text-white hover:bg-gray-600 border border-gray-600 focus:ring-gray-500",
      gold: "bg-gradient-to-r from-gold-400 to-gold-500 text-gray-900 hover:from-gold-500 hover:to-gold-600 shadow-lg hover:shadow-xl focus:ring-gold-400",
      outline: "border-2 border-primary-500 text-primary-500 hover:bg-primary-500 hover:text-white focus:ring-primary-500",
      ghost: "text-gray-300 hover:text-white hover:bg-gray-700 focus:ring-gray-500"
    };

    const sizes = {
      sm: "px-3 py-2 text-sm",
      md: "px-6 py-3 text-base",
      lg: "px-8 py-4 text-lg"
    };

    return (
      <motion.button
        ref={ref}
        className={cn(baseClasses, variants[variant], sizes[size], className)}
        disabled={disabled || loading}
        whileTap={{ scale: 0.95 }}
        whileHover={{ scale: disabled ? 1 : 1.05 }}
        {...props}
      >
        {loading ? (
          <motion.div
            className="w-5 h-5 border-2 border-current border-t-transparent rounded-full"
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          />
        ) : (
          <>
            {Icon && iconPosition === 'left' && (
              <Icon className={cn("w-5 h-5", children && "ml-2")} />
            )}
            {children}
            {Icon && iconPosition === 'right' && (
              <Icon className={cn("w-5 h-5", children && "mr-2")} />
            )}
          </>
        )}
      </motion.button>
    );
  }
);

Button.displayName = "Button";

export default Button;