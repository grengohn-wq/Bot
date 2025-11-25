// src/components/SoundSettings.tsx - Sound settings component

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import Card from './ui/Card';
import Button from './ui/Button';
import { useSound } from '../hooks/useSound';
import { useTelegram } from '../hooks/useTelegram';

interface SoundSettingsProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SoundSettings: React.FC<SoundSettingsProps> = ({ isOpen, onClose }) => {
  const { webApp } = useTelegram();
  const { 
    isEnabled, 
    volume, 
    toggleSound, 
    setVolume, 
    playClickSound, 
    playSuccessSound,
    playErrorSound,
    playCashSound,
    playNotificationSound,
    achievement,
    whoosh
  } = useSound();
  
  const [tempVolume, setTempVolume] = useState(volume);

  const handleVolumeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(event.target.value);
    setTempVolume(newVolume);
    setVolume(newVolume);
    
    // Play test sound
    setTimeout(() => playClickSound(), 100);
  };

  const handleToggleSound = () => {
    const newState = toggleSound();
    webApp?.HapticFeedback.selectionChanged();
    
    if (newState) {
      setTimeout(() => playSuccessSound(), 100);
    }
  };

  const testSounds = [
    { name: 'النقر', action: playClickSound, icon: '👆' },
    { name: 'النجاح', action: playSuccessSound, icon: '✅' },
    { name: 'خطأ', action: playErrorSound, icon: '❌' },
    { name: 'الأموال', action: playCashSound, icon: '💰' },
    { name: 'التنبيه', action: playNotificationSound, icon: '🔔' },
    { name: 'الإنجاز', action: achievement, icon: '🏆' },
    { name: 'الانتقال', action: whoosh, icon: '💨' }
  ];

  if (!isOpen) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="w-full max-w-md"
        onClick={e => e.stopPropagation()}
      >
        <Card className="bg-white">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-gray-900">🔊 إعدادات الصوت</h3>
            <Button
              onClick={onClose}
              variant="outline"
              size="sm"
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </Button>
          </div>

          {/* Sound Toggle */}
          <div className="mb-6">
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <h4 className="font-medium text-gray-900">تفعيل الأصوات</h4>
                <p className="text-sm text-gray-600">تشغيل/إيقاف جميع المؤثرات الصوتية</p>
              </div>
              <button
                onClick={handleToggleSound}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  isEnabled ? 'bg-blue-500' : 'bg-gray-300'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    isEnabled ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          </div>

          {/* Volume Control */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-900 mb-2">
              مستوى الصوت: {Math.round(tempVolume * 100)}%
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={tempVolume}
              onChange={handleVolumeChange}
              disabled={!isEnabled}
              className={`w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer ${
                !isEnabled ? 'opacity-50 cursor-not-allowed' : ''
              }`}
              style={{
                background: isEnabled ? `linear-gradient(to right, #3B82F6 0%, #3B82F6 ${tempVolume * 100}%, #E5E7EB ${tempVolume * 100}%, #E5E7EB 100%)` : '#E5E7EB'
              }}
            />
          </div>

          {/* Test Sounds */}
          <div className="mb-6">
            <h4 className="font-medium text-gray-900 mb-3">🎵 اختبار الأصوات</h4>
            <div className="grid grid-cols-2 gap-2">
              {testSounds.map((sound) => (
                <Button
                  key={sound.name}
                  onClick={() => {
                    webApp?.HapticFeedback.impactOccurred('light');
                    sound.action();
                  }}
                  disabled={!isEnabled}
                  variant="outline"
                  size="sm"
                  className="text-sm"
                >
                  <span className="ml-1">{sound.icon}</span>
                  {sound.name}
                </Button>
              ))}
            </div>
          </div>

          {/* Volume Presets */}
          <div className="mb-6">
            <h4 className="font-medium text-gray-900 mb-3">📊 إعدادات سريعة</h4>
            <div className="flex gap-2">
              {[
                { label: 'هادئ', value: 0.3, icon: '🔈' },
                { label: 'متوسط', value: 0.6, icon: '🔉' },
                { label: 'عالي', value: 1.0, icon: '🔊' }
              ].map((preset) => (
                <Button
                  key={preset.label}
                  onClick={() => {
                    setTempVolume(preset.value);
                    setVolume(preset.value);
                    webApp?.HapticFeedback.selectionChanged();
                    setTimeout(() => playClickSound(), 100);
                  }}
                  disabled={!isEnabled}
                  variant={Math.abs(tempVolume - preset.value) < 0.1 ? 'primary' : 'outline'}
                  size="sm"
                  className="flex-1"
                >
                  <span className="ml-1">{preset.icon}</span>
                  {preset.label}
                </Button>
              ))}
            </div>
          </div>

          {/* Info */}
          <div className="bg-blue-50 p-3 rounded-lg">
            <p className="text-sm text-blue-700">
              💡 <strong>نصيحة:</strong> الأصوات تضيف تجربة تفاعلية أفضل وتساعد في التنقل داخل التطبيق.
            </p>
          </div>

          {/* Close Button */}
          <div className="mt-6 flex justify-end">
            <Button 
              onClick={onClose} 
              className="bg-blue-500 hover:bg-blue-600 text-white"
            >
              تم ✅
            </Button>
          </div>
        </Card>
      </motion.div>
    </motion.div>
  );
};