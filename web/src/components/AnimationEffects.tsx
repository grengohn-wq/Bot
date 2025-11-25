// src/components/AnimationEffects.tsx - Advanced animations and effects

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface FloatingPoint {
  id: string;
  points: number;
  x: number;
  y: number;
  color: string;
}

interface Confetti {
  id: string;
  x: number;
  y: number;
  rotation: number;
  scale: number;
  color: string;
  emoji: string;
}

interface AnimationEffectsProps {
  children: React.ReactNode;
}

export const AnimationEffects: React.FC<AnimationEffectsProps> = ({ children }) => {
  const [floatingPoints, setFloatingPoints] = useState<FloatingPoint[]>([]);
  const [confetti, setConfetti] = useState<Confetti[]>([]);

  // Floating points animation for earning points
  const showFloatingPoints = (points: number, element?: HTMLElement) => {
    const rect = element?.getBoundingClientRect() || { 
      left: window.innerWidth / 2, 
      top: window.innerHeight / 2 
    };
    
    const newPoint: FloatingPoint = {
      id: Math.random().toString(36),
      points,
      x: rect.left + ((rect as DOMRect).width || 0) / 2,
      y: rect.top,
      color: points > 50 ? '#10B981' : points > 20 ? '#3B82F6' : '#6B7280'
    };

    setFloatingPoints(prev => [...prev, newPoint]);

    // Remove after animation
    setTimeout(() => {
      setFloatingPoints(prev => prev.filter(p => p.id !== newPoint.id));
    }, 2000);
  };

  // Confetti explosion for achievements
  const showConfetti = (centerX?: number, centerY?: number) => {
    const x = centerX || window.innerWidth / 2;
    const y = centerY || window.innerHeight / 2;
    
    const emojis = ['🎉', '⭐', '🏆', '💎', '✨', '🎊', '🌟'];
    const colors = ['#FFD700', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'];
    
    const newConfetti: Confetti[] = Array.from({ length: 20 }, () => ({
      id: Math.random().toString(36),
      x: x + (Math.random() - 0.5) * 200,
      y: y + (Math.random() - 0.5) * 100,
      rotation: Math.random() * 360,
      scale: 0.5 + Math.random() * 0.5,
      color: colors[Math.floor(Math.random() * colors.length)],
      emoji: emojis[Math.floor(Math.random() * emojis.length)]
    }));

    setConfetti(newConfetti);

    // Remove after animation
    setTimeout(() => {
      setConfetti([]);
    }, 3000);
  };

  // Expose functions globally for easy access
  useEffect(() => {
    (window as any).showFloatingPoints = showFloatingPoints;
    (window as any).showConfetti = showConfetti;
    
    return () => {
      (window as any).showFloatingPoints = undefined;
      (window as any).showConfetti = undefined;
    };
  }, []);

  return (
    <>
      {children}
      
      {/* Floating Points */}
      <AnimatePresence>
        {floatingPoints.map((point) => (
          <motion.div
            key={point.id}
            initial={{ 
              opacity: 1, 
              y: 0, 
              scale: 0.8,
              x: point.x - 40
            }}
            animate={{ 
              opacity: 0, 
              y: -100, 
              scale: 1.2,
              x: point.x - 40 + (Math.random() - 0.5) * 50
            }}
            exit={{ opacity: 0 }}
            transition={{ duration: 2, ease: "easeOut" }}
            className="fixed z-50 pointer-events-none"
            style={{ 
              top: point.y,
              left: 0,
              color: point.color
            }}
          >
            <div className="bg-white rounded-full px-3 py-1 shadow-lg border-2 font-bold text-sm flex items-center gap-1">
              <span>+{point.points}</span>
              <span className="text-yellow-500">💰</span>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>

      {/* Confetti */}
      <AnimatePresence>
        {confetti.map((particle) => (
          <motion.div
            key={particle.id}
            initial={{ 
              opacity: 1,
              scale: 0,
              x: particle.x,
              y: particle.y,
              rotate: 0
            }}
            animate={{ 
              opacity: [1, 1, 0],
              scale: [0, particle.scale, particle.scale * 0.5],
              x: particle.x + (Math.random() - 0.5) * 300,
              y: particle.y + Math.random() * 400 + 200,
              rotate: particle.rotation + 720
            }}
            exit={{ opacity: 0 }}
            transition={{ 
              duration: 3, 
              ease: "easeOut",
              opacity: { times: [0, 0.7, 1] }
            }}
            className="fixed z-50 pointer-events-none text-2xl"
            style={{ 
              color: particle.color,
              top: 0,
              left: 0
            }}
          >
            {particle.emoji}
          </motion.div>
        ))}
      </AnimatePresence>
    </>
  );
};

// Utility hook for triggering animations
export const useAnimations = () => {
  const triggerFloatingPoints = (points: number, element?: HTMLElement) => {
    if ((window as any).showFloatingPoints) {
      (window as any).showFloatingPoints(points, element);
    }
  };

  const triggerConfetti = (centerX?: number, centerY?: number) => {
    if ((window as any).showConfetti) {
      (window as any).showConfetti(centerX, centerY);
    }
  };

  return {
    triggerFloatingPoints,
    triggerConfetti
  };
};

// Pre-defined animation variants for common use cases
export const animationVariants = {
  // Fade in from bottom
  fadeInUp: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 }
  },

  // Scale in
  scaleIn: {
    initial: { opacity: 0, scale: 0.8 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.8 }
  },

  // Slide in from right
  slideInRight: {
    initial: { opacity: 0, x: 50 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -50 }
  },

  // Slide in from left
  slideInLeft: {
    initial: { opacity: 0, x: -50 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: 50 }
  },

  // Bounce in
  bounceIn: {
    initial: { opacity: 0, scale: 0.3 },
    animate: { 
      opacity: 1, 
      scale: 1,
      transition: {
        type: "spring",
        damping: 10,
        stiffness: 400
      }
    },
    exit: { opacity: 0, scale: 0.3 }
  },

  // Stagger children animation
  staggerContainer: {
    initial: {},
    animate: {
      transition: {
        staggerChildren: 0.1
      }
    },
    exit: {}
  },

  // Stagger child items
  staggerItem: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: 20 }
  },

  // Pulse animation for attention
  pulse: {
    animate: {
      scale: [1, 1.05, 1],
      transition: {
        duration: 2,
        repeat: Infinity,
        ease: "easeInOut"
      }
    }
  },

  // Shake animation for errors
  shake: {
    animate: {
      x: [0, -10, 10, -10, 10, 0],
      transition: {
        duration: 0.5,
        ease: "easeInOut"
      }
    }
  },

  // Success checkmark animation
  successCheck: {
    initial: { pathLength: 0, opacity: 0 },
    animate: { 
      pathLength: 1, 
      opacity: 1,
      transition: {
        pathLength: { type: "spring", duration: 0.6, bounce: 0 },
        opacity: { duration: 0.2 }
      }
    }
  }
};

// Transition presets
export const transitionPresets = {
  smooth: { duration: 0.3, ease: "easeInOut" },
  bouncy: { type: "spring", damping: 15, stiffness: 400 },
  slow: { duration: 0.6, ease: "easeInOut" },
  fast: { duration: 0.15, ease: "easeOut" }
};