/**
 * PWA Handling Script for Shoeb Sir's Academy
 * Handles Service Worker registration and "Add to Home Screen" prompts
 */

// 1. Register Service Worker (Safe for all devices)
// Register from ROOT to ensure correct scope (/)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // UNREGISTER old static scope if it exists (Fix for "deleted" state)
        navigator.serviceWorker.getRegistration('/static/').then(registration => {
            if (registration) {
                registration.unregister();
                console.log('Old static ServiceWorker unregistered');
            }
        });

        // Register new ROOT scope
        navigator.serviceWorker.register('/service-worker.js')
            .then(registration => {
                console.log('ServiceWorker registration successful with scope: ', registration.scope);
            })
            .catch(err => {
                console.log('ServiceWorker registration failed: ', err);
            });
    });
}

// 2. Install Prompt Logic (Mobile Only)
let deferredPrompt;
const installBtn = document.getElementById('pwa-install-btn');
const installContainer = document.getElementById('pwa-install-container');

// Check if device is mobile (simple user agent check)
const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
const isIOS = /iPhone|iPad|iPod/.test(navigator.userAgent) && !window.MSStream;

window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent Chrome 67 and earlier from automatically showing the prompt
    e.preventDefault();
    // Stash the event so it can be triggered later.
    deferredPrompt = e;

    // ONLY show custom install button on mobile devices
    // Desktop users should NOT see this
    if (isMobile) {
        showInstallPromotion();
    } else {
        console.log('PWA: Desktop detected, suppressing install prompt');
    }
});

function showInstallPromotion() {
    // Show your custom install button/banner here
    if (installContainer) {
        installContainer.style.display = 'flex';
    }
    
    // Add click listener
    if (installBtn) {
        installBtn.addEventListener('click', async () => {
            // Hide the promotion UI
            installContainer.style.display = 'none';
            
            // Show the install prompt
            if (deferredPrompt) {
                deferredPrompt.prompt();
                
                // Wait for the user to respond to the prompt
                const { outcome } = await deferredPrompt.userChoice;
                console.log(`User response to the install prompt: ${outcome}`);
                
                // We've used the prompt, and can't use it again, throw it away
                deferredPrompt = null;
            }
        });
    }
}

// 3. iOS Safari Manual Instructions (Since no beforeinstallprompt)
if (isIOS && !window.navigator.standalone) {
    // Ideally, show a toast or banner specifically for iOS users
    // instructing them to tap Share -> Add to Home Screen
    console.log('PWA: iOS detected, consider showing manual install instructions');
    // Logic for iOS specific banner can be added here
}

// 4. App Installed Event
window.addEventListener('appinstalled', () => {
    // Hide the app-provided install promotion
    if (installContainer) {
        installContainer.style.display = 'none';
    }
    // Clear the deferredPrompt so it can be garbage collected
    deferredPrompt = null;
    console.log('PWA was installed');
});
