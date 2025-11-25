// public/sounds.js - Sound files management for Mini App

class SoundManager {
  constructor() {
    this.sounds = {};
    this.initialized = false;
    this.volume = 0.7;
    this.enabled = true;
    
    // Load settings from localStorage
    this.loadSettings();
    
    // Initialize Web Audio API
    this.initializeAudio();
  }

  initializeAudio() {
    try {
      // Create audio context
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      this.masterGain = this.audioContext.createGain();
      this.masterGain.connect(this.audioContext.destination);
      this.masterGain.gain.value = this.volume;
      
      // Preload sound effects
      this.preloadSounds();
      
      this.initialized = true;
      console.log('✅ Sound Manager initialized');
    } catch (error) {
      console.warn('❌ Sound Manager failed to initialize:', error);
      this.initialized = false;
    }
  }

  async preloadSounds() {
    // Define sound effects as base64 data URLs or generate them procedurally
    const soundDefinitions = {
      'click': this.generateClickSound(),
      'success': this.generateSuccessSound(),
      'error': this.generateErrorSound(),
      'cash': this.generateCashSound(),
      'notification': this.generateNotificationSound(),
      'achievement': this.generateAchievementSound(),
      'whoosh': this.generateWhooshSound()
    };

    for (const [name, soundData] of Object.entries(soundDefinitions)) {
      try {
        const audioBuffer = await this.audioContext.decodeAudioData(soundData);
        this.sounds[name] = audioBuffer;
      } catch (error) {
        console.warn(`Failed to load sound: ${name}`, error);
      }
    }
  }

  generateClickSound() {
    // Generate a short click sound
    const sampleRate = 44100;
    const duration = 0.1;
    const length = sampleRate * duration;
    const buffer = this.audioContext.createBuffer(1, length, sampleRate);
    const data = buffer.getChannelData(0);

    for (let i = 0; i < length; i++) {
      const t = i / sampleRate;
      data[i] = Math.sin(2 * Math.PI * 800 * t) * Math.exp(-t * 30) * 0.3;
    }

    return buffer;
  }

  generateSuccessSound() {
    // Generate success chime
    const sampleRate = 44100;
    const duration = 0.6;
    const length = sampleRate * duration;
    const buffer = this.audioContext.createBuffer(1, length, sampleRate);
    const data = buffer.getChannelData(0);

    for (let i = 0; i < length; i++) {
      const t = i / sampleRate;
      const note1 = Math.sin(2 * Math.PI * 523.25 * t); // C5
      const note2 = Math.sin(2 * Math.PI * 659.25 * t); // E5
      const note3 = Math.sin(2 * Math.PI * 783.99 * t); // G5
      const envelope = Math.exp(-t * 2);
      data[i] = (note1 + note2 + note3) * envelope * 0.2;
    }

    return buffer;
  }

  generateErrorSound() {
    // Generate error buzzer
    const sampleRate = 44100;
    const duration = 0.3;
    const length = sampleRate * duration;
    const buffer = this.audioContext.createBuffer(1, length, sampleRate);
    const data = buffer.getChannelData(0);

    for (let i = 0; i < length; i++) {
      const t = i / sampleRate;
      const buzz = Math.sin(2 * Math.PI * 150 * t);
      const envelope = Math.exp(-t * 5);
      data[i] = buzz * envelope * 0.3;
    }

    return buffer;
  }

  generateCashSound() {
    // Generate cash register sound
    const sampleRate = 44100;
    const duration = 0.8;
    const length = sampleRate * duration;
    const buffer = this.audioContext.createBuffer(1, length, sampleRate);
    const data = buffer.getChannelData(0);

    for (let i = 0; i < length; i++) {
      const t = i / sampleRate;
      let sound = 0;
      
      // Cha-ching effect
      if (t < 0.1) {
        sound = Math.sin(2 * Math.PI * 1000 * t) * Math.exp(-t * 20);
      } else if (t < 0.3) {
        sound = Math.sin(2 * Math.PI * 1500 * t) * Math.exp(-(t - 0.1) * 10);
      } else if (t < 0.8) {
        sound = Math.sin(2 * Math.PI * 800 * t) * Math.exp(-(t - 0.3) * 3);
      }
      
      data[i] = sound * 0.4;
    }

    return buffer;
  }

  generateNotificationSound() {
    // Generate notification bell
    const sampleRate = 44100;
    const duration = 0.4;
    const length = sampleRate * duration;
    const buffer = this.audioContext.createBuffer(1, length, sampleRate);
    const data = buffer.getChannelData(0);

    for (let i = 0; i < length; i++) {
      const t = i / sampleRate;
      const bell = Math.sin(2 * Math.PI * 1046.5 * t) * Math.exp(-t * 3); // C6
      const harmonics = Math.sin(2 * Math.PI * 2093 * t) * Math.exp(-t * 5) * 0.3; // C7
      data[i] = (bell + harmonics) * 0.5;
    }

    return buffer;
  }

  generateAchievementSound() {
    // Generate fanfare
    const sampleRate = 44100;
    const duration = 1.2;
    const length = sampleRate * duration;
    const buffer = this.audioContext.createBuffer(1, length, sampleRate);
    const data = buffer.getChannelData(0);

    const notes = [261.63, 329.63, 392, 523.25]; // C-E-G-C major chord
    
    for (let i = 0; i < length; i++) {
      const t = i / sampleRate;
      let sound = 0;
      
      for (let j = 0; j < notes.length; j++) {
        const delay = j * 0.1;
        if (t > delay) {
          sound += Math.sin(2 * Math.PI * notes[j] * (t - delay)) * Math.exp(-(t - delay) * 2);
        }
      }
      
      data[i] = sound * 0.2;
    }

    return buffer;
  }

  generateWhooshSound() {
    // Generate whoosh for transitions
    const sampleRate = 44100;
    const duration = 0.5;
    const length = sampleRate * duration;
    const buffer = this.audioContext.createBuffer(1, length, sampleRate);
    const data = buffer.getChannelData(0);

    for (let i = 0; i < length; i++) {
      const t = i / sampleRate;
      const freq = 1000 * (1 - t); // Frequency sweep down
      const noise = (Math.random() - 0.5) * 2;
      const tone = Math.sin(2 * Math.PI * freq * t);
      const envelope = Math.sin(Math.PI * t / duration);
      data[i] = (noise * 0.3 + tone * 0.7) * envelope * 0.3;
    }

    return buffer;
  }

  playSound(soundName, options = {}) {
    if (!this.enabled || !this.initialized || !this.sounds[soundName]) {
      return;
    }

    try {
      const source = this.audioContext.createBufferSource();
      const gainNode = this.audioContext.createGain();
      
      source.buffer = this.sounds[soundName];
      source.connect(gainNode);
      gainNode.connect(this.masterGain);
      
      // Apply options
      gainNode.gain.value = options.volume || 1.0;
      source.playbackRate.value = options.rate || 1.0;
      
      source.start();
      
      // Cleanup after playback
      source.onended = () => {
        source.disconnect();
        gainNode.disconnect();
      };
      
    } catch (error) {
      console.warn(`Failed to play sound: ${soundName}`, error);
    }
  }

  setVolume(volume) {
    this.volume = Math.max(0, Math.min(1, volume));
    if (this.masterGain) {
      this.masterGain.gain.value = this.volume;
    }
    this.saveSettings();
  }

  setEnabled(enabled) {
    this.enabled = enabled;
    this.saveSettings();
  }

  isEnabled() {
    return this.enabled;
  }

  getVolume() {
    return this.volume;
  }

  saveSettings() {
    try {
      const settings = {
        volume: this.volume,
        enabled: this.enabled
      };
      localStorage.setItem('soundSettings', JSON.stringify(settings));
    } catch (error) {
      console.warn('Failed to save sound settings:', error);
    }
  }

  loadSettings() {
    try {
      const settings = JSON.parse(localStorage.getItem('soundSettings') || '{}');
      this.volume = settings.volume || 0.7;
      this.enabled = settings.enabled !== false;
    } catch (error) {
      console.warn('Failed to load sound settings:', error);
      this.volume = 0.7;
      this.enabled = true;
    }
  }

  // Quick access methods for common sounds
  click(options) { this.playSound('click', options); }
  success(options) { this.playSound('success', options); }
  error(options) { this.playSound('error', options); }
  cash(options) { this.playSound('cash', options); }
  notification(options) { this.playSound('notification', options); }
  achievement(options) { this.playSound('achievement', options); }
  whoosh(options) { this.playSound('whoosh', options); }
}

// Create global sound manager instance
window.soundManager = new SoundManager();

// Expose API for React components
window.playSound = (soundName, options) => {
  window.soundManager.playSound(soundName, options);
};

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = SoundManager;
}