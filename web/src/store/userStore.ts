import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { UserStore } from '@/types';
import { dbFunctions } from '@/lib/supabase';

export const useUserStore = create<UserStore>()(
  persist(
    (set, get) => ({
      user: null,
      isLoading: false,
      isAuthenticated: false,

      setUser: (user) => {
        set({ 
          user, 
          isAuthenticated: !!user 
        });
      },

      updateUser: (updates) => {
        const currentUser = get().user;
        if (currentUser) {
          set({
            user: { ...currentUser, ...updates }
          });
        }
      },

      setLoading: (loading) => {
        set({ isLoading: loading });
      },

      login: async (telegramUser) => {
        set({ isLoading: true });
        
        try {
          // Try to get existing user
          let user = await dbFunctions.getUserByTelegramId(telegramUser.id);
          
          // If user doesn't exist, we need registration flow
          if (!user) {
            set({ 
              isLoading: false, 
              isAuthenticated: false,
              user: null 
            });
            return;
          }

          // Update last activity
          const updatedUser = await dbFunctions.updateUserPoints(telegramUser.id, 0); // Just update timestamp
          
          set({
            user: updatedUser || user,
            isAuthenticated: true,
            isLoading: false
          });
          
        } catch (error) {
          console.error('Login error:', error);
          set({ 
            isLoading: false, 
            isAuthenticated: false,
            user: null 
          });
        }
      },

      logout: () => {
        set({
          user: null,
          isAuthenticated: false,
          isLoading: false
        });
      }
    }),
    {
      name: 'manhaj-ai-user', // localStorage key
      partialize: (state) => ({ 
        user: state.user,
        isAuthenticated: state.isAuthenticated 
      })
    }
  )
);