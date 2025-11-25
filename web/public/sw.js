// Service Worker for منهج AI Mini App
// Provides offline support and caching

const CACHE_NAME = 'manhaj-ai-v2.0';
const STATIC_CACHE = 'manhaj-ai-static-v2.0';

// Files to cache
const STATIC_FILES = [
  '/',
  '/web/',
  '/web/index.html',
  '/favicon.svg',
  '/sounds/cash.mp3',
  '/sounds/success.mp3',
  '/sounds/error.mp3',
  '/sounds/click.mp3',
  '/sounds/notification.mp3'
];

// API routes to cache
const API_CACHE_PATTERNS = [
  /^\/api\/settings/,
  /^\/api\/statistics/
];

// Install event
self.addEventListener('install', (event) => {
  console.log('🔧 Service Worker installing...');
  
  event.waitUntil(
    Promise.all([
      // Cache static files
      caches.open(STATIC_CACHE).then(cache => {
        return cache.addAll(STATIC_FILES).catch(err => {
          console.warn('Failed to cache some static files:', err);
          return Promise.resolve();
        });
      }),
      
      // Force activation
      self.skipWaiting()
    ])
  );
});

// Activate event
self.addEventListener('activate', (event) => {
  console.log('✅ Service Worker activated');
  
  event.waitUntil(
    Promise.all([
      // Clean old caches
      caches.keys().then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (cacheName !== CACHE_NAME && cacheName !== STATIC_CACHE) {
              console.log('🗑️ Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      
      // Take control of all clients
      self.clients.claim()
    ])
  );
});

// Fetch event
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Handle different types of requests
  if (url.pathname.startsWith('/api/')) {
    // API requests - network first, cache fallback
    event.respondWith(handleApiRequest(request));
  } else {
    // Static assets - cache first, network fallback
    event.respondWith(handleStaticRequest(request));
  }
});

// Handle API requests
async function handleApiRequest(request) {
  const url = new URL(request.url);
  
  // Check if this API should be cached
  const shouldCache = API_CACHE_PATTERNS.some(pattern => pattern.test(url.pathname));
  
  if (!shouldCache) {
    // Don't cache user-specific or dynamic data
    return fetch(request);
  }
  
  try {
    // Try network first
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      // Cache successful responses
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
    
  } catch (error) {
    // Network failed, try cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline fallback
    return new Response(
      JSON.stringify({
        success: false,
        error: 'No internet connection',
        offline: true
      }),
      {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Handle static requests
async function handleStaticRequest(request) {
  try {
    // Try cache first for static assets
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Try network
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      // Cache successful responses
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
    
  } catch (error) {
    // If it's the main app, return cached index.html
    if (request.destination === 'document') {
      const cachedApp = await caches.match('/web/index.html') || 
                        await caches.match('/index.html');
      if (cachedApp) {
        return cachedApp;
      }
    }
    
    // Return a basic offline page
    return new Response(
      `<!DOCTYPE html>
      <html lang="ar" dir="rtl">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>منهج AI - غير متصل</title>
        <style>
          body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                 background: #111827; color: white; text-align: center; padding: 20px; }
          .offline { background: linear-gradient(135deg, #10b981, #059669); 
                    border-radius: 12px; padding: 40px 20px; margin: 20px auto; max-width: 400px; }
          .emoji { font-size: 4rem; margin-bottom: 20px; }
          h1 { margin: 20px 0 10px; }
          p { opacity: 0.8; margin: 10px 0; }
          button { background: white; color: #059669; border: none; padding: 12px 24px; 
                  border-radius: 8px; font-weight: bold; cursor: pointer; margin-top: 20px; }
        </style>
      </head>
      <body>
        <div class="offline">
          <div class="emoji">📡</div>
          <h1>منهج AI</h1>
          <h2>غير متصل بالإنترنت</h2>
          <p>تحقق من اتصال الإنترنت وحاول مرة أخرى</p>
          <button onclick="window.location.reload()">إعادة المحاولة</button>
        </div>
      </body>
      </html>`,
      {
        status: 503,
        headers: { 'Content-Type': 'text/html; charset=utf-8' }
      }
    );
  }
}

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-offline-data') {
    event.waitUntil(syncOfflineData());
  }
});

async function syncOfflineData() {
  // Handle any queued offline actions
  try {
    const offlineActions = await getOfflineActions();
    
    for (const action of offlineActions) {
      try {
        await processOfflineAction(action);
        await removeOfflineAction(action.id);
      } catch (error) {
        console.error('Failed to sync offline action:', error);
      }
    }
  } catch (error) {
    console.error('Background sync failed:', error);
  }
}

async function getOfflineActions() {
  // Get offline actions from IndexedDB or localStorage
  return [];
}

async function processOfflineAction(action) {
  // Process the offline action
  return fetch('/api/sync', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(action)
  });
}

async function removeOfflineAction(actionId) {
  // Remove processed action from storage
  return true;
}

// Handle push notifications (future feature)
self.addEventListener('push', (event) => {
  if (event.data) {
    const data = event.data.json();
    
    const options = {
      body: data.body,
      icon: '/favicon.svg',
      badge: '/favicon.svg',
      tag: data.tag || 'manhaj-ai',
      requireInteraction: data.requireInteraction || false,
      actions: data.actions || []
    };
    
    event.waitUntil(
      self.registration.showNotification(data.title, options)
    );
  }
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  event.waitUntil(
    self.clients.openWindow('/web/')
  );
});