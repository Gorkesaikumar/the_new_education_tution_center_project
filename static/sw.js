const CACHE_NAME = 'shoeb-academy-v2';
const STATIC_ASSETS = [
  '/static/css/style.css',
  '/static/images/shoeb_sir_academy_logo.jpg',
  '/static/images/icon-192x192.png',
  '/static/images/icon-512x512.png'
];

// Install Event - Cache Static Assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS).catch(error => {
        console.error('Failed to cache assets:', error);
        // We do NOT re-throw here to prevent the SW from becoming "redundant"
        // But in production, you might want to know if critical assets failed.
        // For now, let it pass so the worker at least installs.
      });
    })
  );
  self.skipWaiting();
});

// Activate Event - Clean Old Caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            return caches.delete(cache);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch Event - Dynamic Caching Strategy
self.addEventListener('fetch', (event) => {
  // Check if request is POST or non-GET (don't cache)
  if (event.request.method !== 'GET') {
    return;
  }

  const url = new URL(event.request.url);

  // Strategy 1: Cache First for Static Assets (CSS, JS, Images, Fonts)
  if (url.pathname.startsWith('/static/') || 
      url.href.includes('fonts.googleapis.com') || 
      url.href.includes('fonts.gstatic.com') ||
      url.href.includes('cdn.jsdelivr.net') ||
      url.href.includes('unpkg.com')) {
    
    event.respondWith(
      caches.match(event.request).then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }
        return fetch(event.request).then((networkResponse) => {
          // Check for valid response
          if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic' && networkResponse.type !== 'cors') {
            return networkResponse;
          }
          // Clone and cache
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
          return networkResponse;
        });
      })
    );
    return;
  }

  // Strategy 2: Network First for HTML/Navigation (Core App Logic)
  // This ensures users always get fresh data (dashboard, marks, etc.)
  if (event.request.mode === 'navigate' || url.pathname.startsWith('/')) {
    event.respondWith(
      fetch(event.request)
        .catch(() => {
          return caches.match('/offline.html'); // Optional offline page
        })
    );
    return;
  }
});
