const CACHE_NAME = 'shoeb-academy-static-v3';

const STATIC_ASSETS = [
  '/static/css/style.css',
  '/static/images/shoeb_sir_academy_logo.jpg',
  '/static/images/icon-192x192.png',
  '/static/images/icon-512x512.png'
];

/* INSTALL */
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

/* ACTIVATE */
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.map(k => k !== CACHE_NAME && caches.delete(k)))
    )
  );
  self.clients.claim();
});

/* FETCH */
self.addEventListener('fetch', event => {
  const req = event.request;
  const url = new URL(req.url);

  // 🚫 NEVER cache POST / PUT / DELETE
  if (req.method !== 'GET') return;

  // ✅ HTML → ALWAYS NETWORK FIRST
  if (req.mode === 'navigate') {
    event.respondWith(fetch(req));
    return;
  }

  // ✅ STATIC FILES → CACHE FIRST
  if (
    url.pathname.startsWith('/static/') ||
    url.hostname.includes('fonts.googleapis.com') ||
    url.hostname.includes('fonts.gstatic.com') ||
    url.hostname.includes('cdn.jsdelivr.net') ||
    url.hostname.includes('unpkg.com')
  ) {
    event.respondWith(
      caches.match(req).then(res => res || fetch(req))
    );
  }
});
