/**
 * PWA Handling Script for Shoeb Sir's Academy
 * SAFE for Django + Cloud Run
 * - Registers Service Worker at ROOT scope
 * - Forces SW update on each load
 * - Shows install prompt ONLY on mobile
 * - Avoids desktop spam
 */

/* -------------------------------------------------
   1. SERVICE WORKER REGISTRATION (ROOT SCOPE)
-------------------------------------------------- */

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {

    // Unregister any OLD static-scoped service worker (important)
    navigator.serviceWorker.getRegistration('/static/')
      .then(oldReg => {
        if (oldReg) {
          oldReg.unregister();
          console.log('Old static Service Worker unregistered');
        }
      });

    // Register ROOT service worker
    navigator.serviceWorker.register('/service-worker.js')
      .then(reg => {
        console.log('Unified Service Worker registered:', reg.scope);
        window.sw_registration = reg; 

        // Let firebase-notifications.js know we are ready
        window.dispatchEvent(new Event('sw-ready'));
      })
      .catch(err => {
        console.error('Service Worker registration failed:', err);
      });
  });
}

/* -------------------------------------------------
   2. INSTALL PROMPT LOGIC (MOBILE ONLY)
-------------------------------------------------- */

let deferredPrompt = null;

const installContainer = document.getElementById('pwa-install-container');
const installBtn = document.getElementById('pwa-install-btn');

// Device detection
const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i
  .test(navigator.userAgent);

const isIOS = /iPhone|iPad|iPod/.test(navigator.userAgent) && !window.MSStream;

// Capture install prompt
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;

  // Show install UI ONLY on mobile
  if (isMobile && installContainer) {
    installContainer.style.display = 'flex';
  }
});

// Install button click
if (installBtn) {
  installBtn.addEventListener('click', async () => {
    if (!deferredPrompt) return;

    installContainer.style.display = 'none';
    deferredPrompt.prompt();

    const { outcome } = await deferredPrompt.userChoice;
    console.log('Install prompt outcome:', outcome);

    deferredPrompt = null;
  });
}

/* -------------------------------------------------
   3. iOS SAFARI (NO AUTO PROMPT)
-------------------------------------------------- */

if (isIOS && !window.navigator.standalone) {
  console.log(
    'iOS detected: show manual Add to Home Screen instructions'
  );
  // Optional: show custom banner here
}

/* -------------------------------------------------
   4. APP INSTALLED EVENT
-------------------------------------------------- */

window.addEventListener('appinstalled', () => {
  console.log('PWA installed successfully');

  if (installContainer) {
    installContainer.style.display = 'none';
  }

  deferredPrompt = null;
});
