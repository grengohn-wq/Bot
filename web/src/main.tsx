import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

// Error boundary for production
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(): { hasError: boolean } {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('منهج AI Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-900 flex items-center justify-center text-white font-arabic">
          <div className="text-center p-6">
            <div className="text-6xl mb-4">😔</div>
            <h2 className="text-2xl font-bold text-red-400 mb-4">حدث خطأ غير متوقع</h2>
            <p className="text-gray-400 mb-6">نعتذر عن هذا الإزعاج. يرجى إعادة تحميل الصفحة.</p>
            <button
              onClick={() => window.location.reload()}
              className="bg-primary-500 hover:bg-primary-600 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
            >
              إعادة تحميل
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Initialize Telegram WebApp
const initTelegramWebApp = () => {
  if (window.Telegram?.WebApp) {
    const tg = window.Telegram.WebApp;
    
    // Configure WebApp
    tg.ready();
    tg.expand();
    tg.enableClosingConfirmation();
    
    // Set theme
    tg.headerColor = '#10b981';
    tg.backgroundColor = '#111827';
    
    console.log('🚀 Telegram WebApp initialized successfully');
    console.log('📱 Platform:', tg.platform);
    console.log('🎨 Color Scheme:', tg.colorScheme);
    console.log('👤 User:', tg.initDataUnsafe.user);
  }
};

// Initialize app
const init = () => {
  initTelegramWebApp();
  
  const rootElement = document.getElementById('root');
  if (!rootElement) {
    throw new Error('Root element not found');
  }

  const root = ReactDOM.createRoot(rootElement);
  
  root.render(
    <React.StrictMode>
      <ErrorBoundary>
        <App />
      </ErrorBoundary>
    </React.StrictMode>
  );
};

// Start app when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

// Service Worker registration for offline support
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  navigator.serviceWorker.register('/sw.js').catch(console.error);
}