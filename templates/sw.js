/* ------------------------------------------------------------------
   UINIFIED SERVICE WORKER
   - Caching (Static Assets)
   - Firebase Cloud Messaging (Background Notifications)
------------------------------------------------------------------ */

// 1. FIREBASE SETUP
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-compat.js');

firebase.initializeApp({
    apiKey: "{{ FIREBASE_API_KEY }}",
    authDomain: "{{ FIREBASE_AUTH_DOMAIN }}",
    projectId: "{{ FIREBASE_PROJECT_ID }}",
    storageBucket: "{{ FIREBASE_STORAGE_BUCKET }}",
    messagingSenderId: "{{ FIREBASE_MESSAGING_SENDER_ID }}",
    appId: "{{ FIREBASE_APP_ID }}",
    measurementId: "{{ FIREBASE_MEASUREMENT_ID }}"
});

const messaging = firebase.messaging();

// Background message handling
messaging.onBackgroundMessage((payload) => {
  console.log('[sw.js] Received background message ', payload);
  
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: '/static/images/icon-192x192.png',
    badge: '/static/images/icon-192x192.png',
    tag: 'academy-notification', // Prevents duplicates
    data: payload.data || {}
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});

// 2. CACHING LOGIC
const CACHE_NAME = 'shoeb-academy-v4'; // Busting cache
const STATIC_ASSETS = [
    '/static/css/style.css',
    '/static/images/shoeb_sir_academy_logo.jpg',
    '/static/images/icon-192x192.png',
    '/static/images/icon-512x512.png'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS))
    );
    self.skipWaiting();
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(keys.map(k => k !== CACHE_NAME && caches.delete(k)))
        )
    );
    self.clients.claim();
});

self.addEventListener('fetch', event => {
    const req = event.request;
    const url = new URL(req.url);

    if (req.method !== 'GET') return;
    if (req.mode === 'navigate') {
        event.respondWith(fetch(req));
        return;
    }

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

// 3. NOTIFICATION CLICK
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    
    let urlToOpen = '/';
    if (event.notification.data && event.notification.data.url) {
        urlToOpen = event.notification.data.url;
    }

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then((windowClients) => {
            for (let i = 0; i < windowClients.length; i++) {
                const client = windowClients[i];
                if (client.url === urlToOpen && 'focus' in client) {
                    return client.focus();
                }
            }
            if (clients.openWindow) {
                return clients.openWindow(urlToOpen);
            }
        })
    );
});
