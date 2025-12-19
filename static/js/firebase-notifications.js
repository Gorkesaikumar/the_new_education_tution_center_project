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
            
            // Wait for sw_registration from pwa.js if not yet available
            if (!window.sw_registration) {
                console.log('Waiting for service worker registration...');
                let attempts = 0;
                while (!window.sw_registration && attempts < 10) {
                    await new Promise(resolve => setTimeout(resolve, 500));
                    attempts++;
                }
            }

            if (!window.sw_registration) {
                console.warn('Service worker registration not found. Notifications might not work in background.');
            }

            // Get FCM Token
            // We pass the registration from pwa.js to ensure we use the unified worker
            const token = await messaging.getToken({ 
                vapidKey: VAPID_KEY,
                serviceWorkerRegistration: window.sw_registration 
            });

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
        // Simple browser detection for better backend tracking
        const userAgent = navigator.userAgent;
        let browserName = "Unknown";
        if (userAgent.match(/chrome|chromium|crios/i)) browserName = "Chrome";
        else if (userAgent.match(/firefox|fxios/i)) browserName = "Firefox";
        else if (userAgent.match(/safari/i)) browserName = "Safari";
        else if (userAgent.match(/edg/i)) browserName = "Edge";

        const response = await fetch('/notifications/save-token/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // CSRF token is handled by the csrf_exempt decorator on the view
            },
            body: JSON.stringify({
                token: token,
                device_id: userAgent,
                device_type: /Mobi|Android/i.test(userAgent) ? 'MOBILE' : 'WEB',
                browser: browserName
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
    // Listen for our custom sw-ready event from pwa.js
    window.addEventListener('sw-ready', () => {
        console.log('Detected sw-ready event, setting up push...');
        setupPushNotifications();
    });

    // Fallback: If registration already happened
    window.addEventListener('load', () => {
        setTimeout(() => {
            if (window.sw_registration) {
                console.log('SW already registered on load, setting up push...');
                setupPushNotifications();
            }
        }, 1000);
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
