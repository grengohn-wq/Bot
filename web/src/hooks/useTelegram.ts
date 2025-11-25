import { useEffect, useState } from 'react';
import { TelegramWebApp } from '@/types';

export const useTelegram = () => {
  const [webApp, setWebApp] = useState<TelegramWebApp | null>(null);
  const [user, setUser] = useState<any>(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    
    if (tg) {
      setWebApp(tg);
      
      // Initialize Telegram WebApp
      tg.ready();
      tg.expand();
      
      // Set theme colors
      tg.setHeaderColor('#10b981');
      tg.setBackgroundColor('#111827');
      
      // Get user data
      if (tg.initDataUnsafe.user) {
        setUser(tg.initDataUnsafe.user);
      }
      
      setIsReady(true);
      
      console.log('✅ Telegram WebApp initialized:', {
        version: tg.version,
        platform: tg.platform,
        user: tg.initDataUnsafe.user
      });
    } else {
      // Fallback for development/testing
      console.warn('⚠️ Telegram WebApp not available. Running in development mode.');
      
      // Mock user for development
      if (import.meta.env.DEV) {
        setUser({
          id: 123456789,
          first_name: 'مصعب',
          last_name: 'فهد',
          username: 'mosap_dev',
          language_code: 'ar'
        });
      }
      
      setIsReady(true);
    }
  }, []);

  // Haptic feedback helpers
  const hapticFeedback = {
    impact: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft' = 'medium') => {
      webApp?.HapticFeedback?.impactOccurred(style);
    },
    notification: (type: 'error' | 'success' | 'warning' = 'success') => {
      webApp?.HapticFeedback?.notificationOccurred(type);
    },
    selection: () => {
      webApp?.HapticFeedback?.selectionChanged();
    }
  };

  // Main button helpers
  const mainButton = {
    show: (text: string, onClick: () => void) => {
      if (webApp?.MainButton) {
        webApp.MainButton.setText(text);
        webApp.MainButton.onClick(onClick);
        webApp.MainButton.show();
      }
    },
    hide: () => {
      webApp?.MainButton?.hide();
    },
    showProgress: () => {
      webApp?.MainButton?.showProgress();
    },
    hideProgress: () => {
      webApp?.MainButton?.hideProgress();
    }
  };

  // Back button helpers
  const backButton = {
    show: (onClick: () => void) => {
      if (webApp?.BackButton) {
        webApp.BackButton.onClick(onClick);
        webApp.BackButton.show();
      }
    },
    hide: () => {
      webApp?.BackButton?.hide();
    }
  };

  // Utility functions
  const openLink = (url: string) => {
    if (webApp) {
      webApp.openLink(url);
    } else {
      window.open(url, '_blank');
    }
  };

  const openTelegramLink = (url: string) => {
    if (webApp) {
      webApp.openTelegramLink(url);
    } else {
      window.open(url, '_blank');
    }
  };

  const close = () => {
    webApp?.close();
  };

  const sendData = (data: any) => {
    if (webApp) {
      webApp.sendData(JSON.stringify(data));
    }
  };

  return {
    webApp,
    user,
    isReady,
    hapticFeedback,
    mainButton,
    backButton,
    openLink,
    openTelegramLink,
    close,
    sendData,
    platform: webApp?.platform || 'unknown',
    version: webApp?.version || 'unknown',
    colorScheme: webApp?.colorScheme || 'dark'
  };
};