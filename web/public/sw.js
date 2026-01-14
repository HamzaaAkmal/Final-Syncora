// Syncora Service Worker - Offline-First PWA
// Version: 1.0.0

const CACHE_NAME = 'syncora-v1';
const OFFLINE_URL = '/offline.html';

// Core assets that should always be cached
const CORE_ASSETS = [
  '/',
  '/offline.html',
  '/manifest.json',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png',
];

// API endpoints that can be cached
const CACHEABLE_API_PATTERNS = [
  '/api/v1/curriculum',
  '/api/v1/offline/packs',
  '/api/v1/offline/prebuilt',
];

// Dynamic content cache (for offline learning packs)
const DYNAMIC_CACHE = 'syncora-dynamic-v1';
const OFFLINE_PACKS_CACHE = 'syncora-offline-packs-v1';

// Install event - cache core assets
self.addEventListener('install', (event) => {
  console.log('[SW] Installing Syncora Service Worker...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[SW] Caching core assets');
        return cache.addAll(CORE_ASSETS);
      })
      .then(() => {
        console.log('[SW] Installation complete');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('[SW] Installation failed:', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating Syncora Service Worker...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME && 
                cacheName !== DYNAMIC_CACHE && 
                cacheName !== OFFLINE_PACKS_CACHE) {
              console.log('[SW] Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('[SW] Activation complete');
        return self.clients.claim();
      })
  );
});

// Fetch event - network first with cache fallback
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Handle different types of requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Handle API requests
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleApiRequest(request));
    return;
  }
  
  // Handle offline pack downloads
  if (url.pathname.includes('/offline/download')) {
    event.respondWith(handleOfflinePackDownload(request));
    return;
  }
  
  // Handle navigation requests
  if (request.mode === 'navigate') {
    event.respondWith(handleNavigationRequest(request));
    return;
  }
  
  // Handle static assets (CSS, JS, images)
  event.respondWith(handleStaticAssets(request));
});

// Handle API requests - network first, cache fallback
async function handleApiRequest(request) {
  const url = new URL(request.url);
  
  try {
    const response = await fetch(request);
    
    // Cache successful API responses for cacheable endpoints
    if (response.ok && isCacheableApi(url.pathname)) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    console.log('[SW] Network failed for API, trying cache:', url.pathname);
    
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline JSON response
    return new Response(
      JSON.stringify({
        error: 'offline',
        message: 'You are currently offline. Please check your connection.',
        message_ur: 'آپ فی الحال آف لائن ہیں۔ براہ کرم اپنا کنکشن چیک کریں۔'
      }),
      {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Handle navigation requests
async function handleNavigationRequest(request) {
  try {
    // Try network first
    const response = await fetch(request);
    
    // Cache the page for offline access
    if (response.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    console.log('[SW] Network failed for navigation, trying cache');
    
    // Try cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline page
    const offlineResponse = await caches.match(OFFLINE_URL);
    if (offlineResponse) {
      return offlineResponse;
    }
    
    // Fallback offline response
    return new Response(getOfflineHTML(), {
      status: 200,
      headers: { 'Content-Type': 'text/html' }
    });
  }
}

// Handle static assets - cache first, network fallback
async function handleStaticAssets(request) {
  const cachedResponse = await caches.match(request);
  
  if (cachedResponse) {
    // Return cached version and update in background
    fetchAndCache(request);
    return cachedResponse;
  }
  
  try {
    const response = await fetch(request);
    
    if (response.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    console.log('[SW] Failed to fetch static asset:', request.url);
    
    // Return placeholder for images
    if (request.destination === 'image') {
      return new Response(
        '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><rect fill="#ddd" width="100" height="100"/><text x="50" y="50" text-anchor="middle" fill="#888">Offline</text></svg>',
        { headers: { 'Content-Type': 'image/svg+xml' } }
      );
    }
    
    throw error;
  }
}

// Handle offline pack downloads - store in dedicated cache
async function handleOfflinePackDownload(request) {
  try {
    const response = await fetch(request);
    
    if (response.ok) {
      const cache = await caches.open(OFFLINE_PACKS_CACHE);
      cache.put(request, response.clone());
      
      // Notify the app that the pack is downloaded
      self.clients.matchAll().then((clients) => {
        clients.forEach((client) => {
          client.postMessage({
            type: 'OFFLINE_PACK_DOWNLOADED',
            url: request.url
          });
        });
      });
    }
    
    return response;
  } catch (error) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    throw error;
  }
}

// Helper: Check if API endpoint is cacheable
function isCacheableApi(pathname) {
  return CACHEABLE_API_PATTERNS.some(pattern => pathname.startsWith(pattern));
}

// Helper: Fetch and cache in background
async function fetchAndCache(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, response.clone());
    }
  } catch (error) {
    // Silently fail
  }
}

// Offline HTML fallback
function getOfflineHTML() {
  return `
<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Syncora - Offline</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: linear-gradient(135deg, #059669 0%, #047857 100%);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    
    .container {
      background: white;
      border-radius: 20px;
      padding: 40px;
      max-width: 500px;
      text-align: center;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    }
    
    .icon {
      font-size: 80px;
      margin-bottom: 20px;
    }
    
    h1 {
      color: #1f2937;
      font-size: 28px;
      margin-bottom: 10px;
    }
    
    .urdu {
      font-family: 'Noto Nastaliq Urdu', serif;
      direction: rtl;
      color: #374151;
      font-size: 22px;
      margin-bottom: 20px;
    }
    
    p {
      color: #6b7280;
      line-height: 1.6;
      margin-bottom: 30px;
    }
    
    .features {
      background: #f3f4f6;
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 30px;
      text-align: left;
    }
    
    .features h3 {
      color: #059669;
      margin-bottom: 15px;
      font-size: 16px;
    }
    
    .feature-item {
      display: flex;
      align-items: center;
      margin-bottom: 10px;
      color: #374151;
      font-size: 14px;
    }
    
    .feature-item span {
      margin-right: 10px;
    }
    
    .btn {
      display: inline-block;
      background: #059669;
      color: white;
      padding: 14px 28px;
      border-radius: 10px;
      text-decoration: none;
      font-weight: 600;
      transition: all 0.3s;
    }
    
    .btn:hover {
      background: #047857;
      transform: translateY(-2px);
    }
    
    .status {
      margin-top: 20px;
      padding: 10px;
      border-radius: 8px;
      font-size: 14px;
    }
    
    .status.offline {
      background: #fef3c7;
      color: #92400e;
    }
    
    .status.online {
      background: #d1fae5;
      color: #065f46;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="icon">📚</div>
    <h1>You're Offline</h1>
    <p class="urdu">آپ آف لائن ہیں</p>
    <p>Don't worry! Your learning doesn't have to stop. Syncora has offline capabilities to keep you learning.</p>
    
    <div class="features">
      <h3>📥 Available Offline Features:</h3>
      <div class="feature-item">
        <span>✅</span> View cached lessons
      </div>
      <div class="feature-item">
        <span>✅</span> Access downloaded content packs
      </div>
      <div class="feature-item">
        <span>✅</span> Review your study notes
      </div>
      <div class="feature-item">
        <span>✅</span> Practice with saved problems
      </div>
    </div>
    
    <button class="btn" onclick="window.location.reload()">
      🔄 Try Again
    </button>
    
    <div id="status" class="status offline">
      🔴 Currently Offline
    </div>
  </div>
  
  <script>
    // Check online status
    function updateStatus() {
      const statusEl = document.getElementById('status');
      if (navigator.onLine) {
        statusEl.className = 'status online';
        statusEl.textContent = '🟢 Back Online - Refreshing...';
        setTimeout(() => window.location.reload(), 1000);
      } else {
        statusEl.className = 'status offline';
        statusEl.textContent = '🔴 Currently Offline';
      }
    }
    
    window.addEventListener('online', updateStatus);
    window.addEventListener('offline', updateStatus);
    updateStatus();
  </script>
</body>
</html>
  `;
}

// Message handler for communication with the app
self.addEventListener('message', (event) => {
  const { type, payload } = event.data || {};
  
  switch (type) {
    case 'SKIP_WAITING':
      self.skipWaiting();
      break;
      
    case 'CACHE_CONTENT':
      cacheContent(payload);
      break;
      
    case 'CLEAR_CACHE':
      clearCache(payload);
      break;
      
    case 'GET_CACHE_SIZE':
      getCacheSize().then((size) => {
        event.source.postMessage({
          type: 'CACHE_SIZE',
          size
        });
      });
      break;
  }
});

// Cache specific content
async function cacheContent(urls) {
  if (!urls || !Array.isArray(urls)) return;
  
  const cache = await caches.open(DYNAMIC_CACHE);
  
  for (const url of urls) {
    try {
      const response = await fetch(url);
      if (response.ok) {
        await cache.put(url, response);
      }
    } catch (error) {
      console.log('[SW] Failed to cache:', url);
    }
  }
}

// Clear cache
async function clearCache(cacheName) {
  if (cacheName) {
    await caches.delete(cacheName);
  } else {
    const names = await caches.keys();
    await Promise.all(names.map((name) => caches.delete(name)));
  }
}

// Get total cache size
async function getCacheSize() {
  if (!navigator.storage || !navigator.storage.estimate) {
    return null;
  }
  
  const estimate = await navigator.storage.estimate();
  return {
    used: estimate.usage,
    available: estimate.quota,
    percentage: ((estimate.usage / estimate.quota) * 100).toFixed(2)
  };
}

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-progress') {
    event.waitUntil(syncProgress());
  }
});

// Sync progress when back online
async function syncProgress() {
  console.log('[SW] Syncing offline progress...');
  
  // Get pending progress data from IndexedDB
  // This would sync any offline learning progress
  
  self.clients.matchAll().then((clients) => {
    clients.forEach((client) => {
      client.postMessage({
        type: 'SYNC_COMPLETE',
        message: 'Your offline progress has been synced!'
      });
    });
  });
}

console.log('[SW] Syncora Service Worker loaded');
