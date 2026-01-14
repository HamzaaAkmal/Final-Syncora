'use client';

import { useEffect, useState } from 'react';

// PWA Install prompt event type
interface BeforeInstallPromptEvent extends Event {
  readonly platforms: string[];
  readonly userChoice: Promise<{
    outcome: 'accepted' | 'dismissed';
    platform: string;
  }>;
  prompt(): Promise<void>;
}

declare global {
  interface WindowEventMap {
    beforeinstallprompt: BeforeInstallPromptEvent;
  }
}

export default function ServiceWorkerRegistration() {
  const [isOnline, setIsOnline] = useState(true);
  const [showOfflineBanner, setShowOfflineBanner] = useState(false);
  const [showInstallPrompt, setShowInstallPrompt] = useState(false);
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [showUpdateBanner, setShowUpdateBanner] = useState(false);

  useEffect(() => {
    // Check initial online status
    setIsOnline(navigator.onLine);

    // Register service worker
    if ('serviceWorker' in navigator) {
      registerServiceWorker();
    }

    // Online/Offline event listeners
    const handleOnline = () => {
      setIsOnline(true);
      setShowOfflineBanner(false);
      
      // Sync any offline data
      if ('serviceWorker' in navigator && 'sync' in ServiceWorkerRegistration.prototype) {
        navigator.serviceWorker.ready.then((registration) => {
          (registration as any).sync?.register('sync-progress');
        });
      }
    };

    const handleOffline = () => {
      setIsOnline(false);
      setShowOfflineBanner(true);
    };

    // PWA install prompt
    const handleInstallPrompt = (e: BeforeInstallPromptEvent) => {
      e.preventDefault();
      setDeferredPrompt(e);

      // Respect user's preference if they chose not to see the install prompt
      try {
        const dontShow = localStorage.getItem('syncora_dont_show_install') === 'true';
        if (dontShow) return;
      } catch (err) {
        // ignore localStorage errors
      }
      
      // Show install prompt if not already installed
      const isInstalled = window.matchMedia('(display-mode: standalone)').matches;
      if (!isInstalled) {
        setTimeout(() => setShowInstallPrompt(true), 30000); // Show after 30 seconds
      }
    };

    // Service worker message handler
    const handleSwMessage = (event: MessageEvent) => {
      const { type, message } = event.data || {};
      
      switch (type) {
        case 'SYNC_COMPLETE':
          console.log('[App] Sync complete:', message);
          break;
        case 'OFFLINE_PACK_DOWNLOADED':
          console.log('[App] Offline pack downloaded:', event.data.url);
          break;
        case 'UPDATE_AVAILABLE':
          setShowUpdateBanner(true);
          break;
      }
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    window.addEventListener('beforeinstallprompt', handleInstallPrompt as any);
    navigator.serviceWorker?.addEventListener('message', handleSwMessage);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      window.removeEventListener('beforeinstallprompt', handleInstallPrompt as any);
      navigator.serviceWorker?.removeEventListener('message', handleSwMessage);
    };
  }, []);

  async function registerServiceWorker() {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js', {
        scope: '/',
      });

      console.log('[App] Service Worker registered:', registration.scope);

      // Check for updates
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing;
        if (newWorker) {
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              setShowUpdateBanner(true);
            }
          });
        }
      });

      // Periodic update check
      setInterval(() => {
        registration.update();
      }, 60 * 60 * 1000); // Check every hour

    } catch (error) {
      console.error('[App] Service Worker registration failed:', error);
    }
  }

  async function handleInstall() {
    if (!deferredPrompt) return;

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    
    console.log('[App] Install prompt outcome:', outcome);
    setDeferredPrompt(null);
    setShowInstallPrompt(false);

    try {
      // If the user accepted installation, don't show the prompt again
      if (outcome === 'accepted') {
        localStorage.setItem('syncora_dont_show_install', 'true');
      }
    } catch (err) {
      // ignore localStorage errors
    }
  }

  function handleUpdate() {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.ready.then((registration) => {
        registration.waiting?.postMessage({ type: 'SKIP_WAITING' });
      });
      window.location.reload();
    }
  }

  return (
    <>
      {/* Offline Banner */}
      {showOfflineBanner && (
        <div className="fixed top-0 left-0 right-0 z-50 bg-amber-500 text-white px-4 py-2 text-center text-sm font-medium animate-slideDown">
          <div className="flex items-center justify-center gap-2">
            <span className="inline-block w-2 h-2 bg-red-500 rounded-full animate-pulse" />
            <span>You&apos;re offline. Some features may be limited.</span>
            <span className="mr-4">|</span>
            <span dir="rtl" className="font-urdu">آپ آف لائن ہیں۔ کچھ خصوصیات محدود ہو سکتی ہیں۔</span>
            <button 
              onClick={() => setShowOfflineBanner(false)}
              className="ml-4 text-white/80 hover:text-white"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {/* Install PWA Prompt */}
      {showInstallPrompt && (
        <div className="fixed bottom-4 right-4 z-50 bg-white dark:bg-slate-800 rounded-xl shadow-2xl p-4 max-w-sm animate-slideUp border border-emerald-200 dark:border-emerald-800">
          <div className="flex items-start gap-3">
            <div className="text-3xl">📱</div>
            <div className="flex-1">
              <h4 className="font-bold text-slate-800 dark:text-white mb-1">
                Install Syncora
              </h4>
              <p className="text-sm text-slate-600 dark:text-slate-300 mb-3">
                Install the app for faster access and offline learning!
              </p>
              <p dir="rtl" className="text-sm text-emerald-600 dark:text-emerald-400 font-urdu mb-3">
                آف لائن سیکھنے کے لیے ایپ انسٹال کریں!
              </p>
              <div className="flex gap-2">
                <button
                  onClick={handleInstall}
                  className="flex-1 bg-emerald-600 text-white px-3 py-2 rounded-lg text-sm font-medium hover:bg-emerald-700 transition-colors"
                >
                  Install
                </button>
                <button
                  onClick={() => {
                    try {
                      localStorage.setItem('syncora_dont_show_install', 'true');
                    } catch (err) {
                      // ignore
                    }
                    setShowInstallPrompt(false);
                  }}
                  className="px-3 py-2 rounded-lg text-sm text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                >
                  Don't show again
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Update Available Banner */}
      {showUpdateBanner && (
        <div className="fixed bottom-4 left-4 z-50 bg-blue-600 text-white rounded-xl shadow-2xl p-4 max-w-sm animate-slideUp">
          <div className="flex items-start gap-3">
            <div className="text-2xl">🔄</div>
            <div className="flex-1">
              <h4 className="font-bold mb-1">Update Available</h4>
              <p className="text-sm text-blue-100 mb-3">
                A new version of Syncora is ready!
              </p>
              <div className="flex gap-2">
                <button
                  onClick={handleUpdate}
                  className="flex-1 bg-white text-blue-600 px-3 py-2 rounded-lg text-sm font-medium hover:bg-blue-50 transition-colors"
                >
                  Update Now
                </button>
                <button
                  onClick={() => setShowUpdateBanner(false)}
                  className="px-3 py-2 rounded-lg text-sm text-blue-100 hover:bg-blue-500 transition-colors"
                >
                  Later
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Online Status Indicator (subtle) */}
      <div 
        className={`fixed bottom-2 left-2 z-40 flex items-center gap-1.5 px-2 py-1 rounded-full text-xs transition-all duration-300 ${
          isOnline 
            ? 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400' 
            : 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
        }`}
      >
        <span 
          className={`w-1.5 h-1.5 rounded-full ${
            isOnline ? 'bg-emerald-500' : 'bg-red-500 animate-pulse'
          }`} 
        />
        {isOnline ? 'Online' : 'Offline'}
      </div>

      {/* Animations */}
      <style jsx>{`
        @keyframes slideDown {
          from {
            transform: translateY(-100%);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }
        
        @keyframes slideUp {
          from {
            transform: translateY(100%);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }
        
        .animate-slideDown {
          animation: slideDown 0.3s ease-out;
        }
        
        .animate-slideUp {
          animation: slideUp 0.3s ease-out;
        }
      `}</style>
    </>
  );
}
