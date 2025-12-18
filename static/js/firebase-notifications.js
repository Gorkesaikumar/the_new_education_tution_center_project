// VAPID KEY - Get this from Firebase Console -> Cloud Messaging -> Web Configuration -> Web Push certificates
const VAPID_KEY = (typeof firebaseConfig !== 'undefined') ? firebaseConfig.vapidKey : "YOUR_PUBLIC_VAPID_KEY";

// Note: firebase and messaging are initialized in base.html
// We use window.fcm_messaging to access the initialized instance
const getMessaging = () => {
    return window.fcm_messaging || null;
};

/**
 * Handle FCM Token Retrieval and Server Sync
 */
async function setupPushNotifications() {
    try {
        const messaging = getMessaging();
        if (!messaging) {
            console.warn('Messaging not initialized. Check Firebase config.');
            return;
        }

        // Request Permission
        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
            console.log('Notification permission granted.');
            
            // Get FCM Token
            const token = await messaging.getToken({ vapidKey: VAPID_KEY });
            if (token) {
                console.log('FCM Token:', token);
                await sendTokenToServer(token);
            } else {
                console.warn('No registration token available. Request permission to generate one.');
            }
        } else {
            console.warn('Notification permission denied.');
        }
    } catch (err) {
        console.error('An error occurred while retrieving token:', err);
    }
}

/**
 * Send Token to Django Backend
 */
async function sendTokenToServer(token) {
    try {
        const response = await fetch('/notifications/save-token/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // CSRF token is handled by the csrf_exempt decorator on the view for simplicity,
                // but adding it here is better production practice if you have it available.
            },
            body: JSON.stringify({
                token: token,
                device_id: navigator.userAgent // Simple device ID
            })
        });
        const data = await response.json();
        console.log('Server response:', data);
    } catch (err) {
        console.error('Failed to send token to server:', err);
    }
}

// Automatically try to setup on login/load if supported
if ('serviceWorker' in navigator && 'PushManager' in window) {
    // We wait for the page to load and the SW to be ready
    window.addEventListener('load', () => {
        // We assume the service worker is already registered in base.html
        // setupPushNotifications(); // Call this when you want to prompt (usually after login)
    });
}

// Handle Foreground Messages
const messaging = getMessaging();
if (messaging) {
    messaging.onMessage((payload) => {
        console.log('Message received in foreground:', payload);
        const { title, body } = payload.notification;
        
        // Show a browser notification (since the browser won't show it automatically in foreground)
        const notificationTitle = title;
        const notificationOptions = {
            body: body,
            icon: '/static/images/icon-192x192.png',
            data: payload.data
        };

        if (Notification.permission === 'granted') {
            new Notification(notificationTitle, notificationOptions);
        }
    });
}
