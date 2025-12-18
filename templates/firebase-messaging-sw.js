// MUST BE IN THE ROOT OR ACCESSIBLE FROM THE ROOT
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-compat.js');

// Initialize the Firebase app in the service worker by passing in the messagingSenderId.
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
  console.log('[firebase-messaging-sw.js] Received background message ', payload);
  
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: '/static/images/icon-192x192.png',
    badge: '/static/images/icon-192x192.png',
    data: payload.data
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});

// Handle notification click
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    
    let urlToOpen = '/';
    if (event.notification.data && event.notification.data.url) {
        urlToOpen = event.notification.data.url;
    }

    event.waitUntil(
        clients.matchAll({ type: 'window' }).then((windowClients) => {
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
