import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { AppStore } from '@/types';
import { dbFunctions } from '@/lib/supabase';

export const useAppStore = create<AppStore>()(
  persist(
    (set) => ({
      theme: 'dark',
      language: 'ar',
      currentScreen: 'home',
      isOnline: navigator.onLine,
      statistics: null,
      settings: {},

      setTheme: (theme) => {
        set({ theme });
      },

      setCurrentScreen: (screen) => {
        set({ currentScreen: screen });
        
        // Telegram WebApp haptic feedback
        if (window.Telegram?.WebApp?.HapticFeedback) {
          window.Telegram.WebApp.HapticFeedback.selectionChanged();
        }
      },

      setOnlineStatus: (online) => {
        set({ isOnline: online });
      },

      setStatistics: (statistics) => {
        set({ statistics });
      },

      setSettings: (settings) => {
        set({ settings });
      }
    }),
    {
      name: 'manhaj-ai-app',
      partialize: (state) => ({
        theme: state.theme,
        language: state.language,
        settings: state.settings
      })
    }
  )
);

// Load initial data
export const initializeApp = async () => {
  const { setSettings, setStatistics, setOnlineStatus } = useAppStore.getState();
  
  try {
    // Load app settings
    const settings = await dbFunctions.getAppSettings();
    setSettings(settings);
    
    // Load statistics
    const statistics = await dbFunctions.getAppStatistics();
    if (statistics) {
      setStatistics(statistics);
    }
    
    // Setup online/offline listeners
    const handleOnline = () => setOnlineStatus(true);
    const handleOffline = () => setOnlineStatus(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
    
  } catch (error) {
    console.error('Failed to initialize app:', error);
  }
};