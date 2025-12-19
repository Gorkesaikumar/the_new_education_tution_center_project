/* ------------------------------------------------------------------
   UNIFIED SERVICE WORKER
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

// Background message handling via FCM High-Level API
messaging.onBackgroundMessage((payload) => {
  console.log('[sw.js] Received onBackgroundMessage ', payload);
  // Note: If 'notification' is present in payload, the browser might show it automatically.
  // We only manually show if we want custom behavior or if it's a data-only message.
});

// RAW PUSH LISTENER (Backup & Core)
self.addEventListener('push', (event) => {
    console.log('[sw.js] Push event received', event);
    
    let data = {};
    if (event.data) {
        try {
            data = event.data.json();
            console.log('[sw.js] Push data (JSON):', data);
        } catch (e) {
            console.log('[sw.js] Push data (Text):', event.data.text());
        }
    }

    // FCM sends 'notification' and 'data' blocks.
    // If the browser hasn't shown the notification yet, we do it here.
    const title = (data.notification && data.notification.title) || (data.data && data.data.title) || "New Academy Update";
    const body = (data.notification && data.notification.body) || (data.data && data.data.body) || "You have a new notification.";
    
    const options = {
        body: body,
        icon: '/static/images/icon-192x192.png',
        badge: '/static/images/icon-192x192.png',
        tag: 'academy-update',
        renotify: true,
        data: {
            url: (data.data && data.data.url) || (data.fcm_options && data.fcm_options.link) || '/'
        }
    };

    // Only show if the message wasn't automatically handled by FCM
    // Avoid double notifications by checking if notification block exists (FCM usually shows those)
    if (!data.notification) {
        event.waitUntil(self.registration.showNotification(title, options));
    }
});

// 2. CACHING LOGIC
const CACHE_NAME = 'shoeb-academy-v5'; // Busting cache
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
