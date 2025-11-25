// src/hooks/useSound.ts - Enhanced sound effects hook for Telegram Mini App

import { useCallback, useEffect, useState } from 'react';

interface SoundOptions {
  volume?: number;
  rate?: number;
}

type SoundType = 'click' | 'success' | 'error' | 'cash' | 'notification' | 'achievement' | 'whoosh';

declare global {
  interface Window {
    soundManager?: any;
    playSound?: (soundName: string, options?: SoundOptions) => void;
  }
}

export const useSound = () => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isEnabled, setIsEnabled] = useState(true);
  const [volume, setVolumeState] = useState(0.7);

  // Load sound manager script
  useEffect(() => {
    const script = document.createElement('script');
    script.src = '/sounds.js';
    script.onload = () => {
      setIsLoaded(true);
      if (window.soundManager) {
        setIsEnabled(window.soundManager.isEnabled());
        setVolumeState(window.soundManager.getVolume());
      }
    };
    script.onerror = () => {
      console.warn('Failed to load sound manager');
      setIsLoaded(false);
    };
    document.head.appendChild(script);

    return () => {
      if (document.head.contains(script)) {
        document.head.removeChild(script);
      }
    };
  }, []);

  const playSound = useCallback((type: SoundType, options?: SoundOptions) => {
    if (!isLoaded || !isEnabled || !window.playSound) return;

    try {
      window.playSound(type, {
        volume: options?.volume || 1.0,
        rate: options?.rate || 1.0
      });
    } catch (error) {
      console.warn('Sound playback failed:', error);
    }
  }, [isLoaded, isEnabled]);

  const toggleSound = useCallback(() => {
    if (!isLoaded || !window.soundManager) return false;

    const newState = !isEnabled;
    window.soundManager.setEnabled(newState);
    setIsEnabled(newState);
    return newState;
  }, [isLoaded, isEnabled]);

  const setVolume = useCallback((newVolume: number) => {
    if (!isLoaded || !window.soundManager) return;

    const clampedVolume = Math.max(0, Math.min(1, newVolume));
    window.soundManager.setVolume(clampedVolume);
    setVolumeState(clampedVolume);
  }, [isLoaded]);

  // Legacy methods for backwards compatibility
  const playCashSound = useCallback((volume?: number) => {
    playSound('cash', { volume });
  }, [playSound]);

  const playSuccessSound = useCallback((volume?: number) => {
    playSound('success', { volume });
  }, [playSound]);

  const playErrorSound = useCallback((volume?: number) => {
    playSound('error', { volume });
  }, [playSound]);

  const playClickSound = useCallback((volume?: number) => {
    playSound('click', { volume });
  }, [playSound]);

  const playNotificationSound = useCallback((volume?: number) => {
    playSound('notification', { volume });
  }, [playSound]);

  // Convenient sound effect methods
  const sounds = {
    click: (options?: SoundOptions) => playSound('click', options),
    success: (options?: SoundOptions) => playSound('success', options),
    error: (options?: SoundOptions) => playSound('error', options),
    cash: (options?: SoundOptions) => playSound('cash', options),
    notification: (options?: SoundOptions) => playSound('notification', options),
    achievement: (options?: SoundOptions) => playSound('achievement', options),
    whoosh: (options?: SoundOptions) => playSound('whoosh', options),
  };

  return { 
    playSound, 
    toggleSound,
    setVolume,
    volume,
    isLoaded,
    isEnabled,
    // Legacy compatibility
    playCashSound,
    playSuccessSound,
    playErrorSound,
    playClickSound,
    playNotificationSound,
    // New sound methods
    ...sounds
  };
};