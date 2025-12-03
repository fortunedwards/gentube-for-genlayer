// Service Worker for PWA functionality
const CACHE_NAME = 'gentube-v1.0.0';
const STATIC_CACHE = 'gentube-static-v1.0.0';
const DYNAMIC_CACHE = 'gentube-dynamic-v1.0.0';

// Files to cache immediately
const STATIC_FILES = [
    '/',
    '/index.html',
    '/css/app.css',
    '/js/app.js',
    '/manifest.json',
    '/videos.json',
    'https://unpkg.com/vue@3/dist/vue.global.js'
];

// Install event - cache static files
self.addEventListener('install', (event) => {
    console.log('Service Worker installing...');
    
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then((cache) => {
                console.log('Caching static files');
                return cache.addAll(STATIC_FILES);
            })
            .then(() => {
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('Failed to cache static files:', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('Service Worker activating...');
    
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                            console.log('Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                return self.clients.claim();
            })
    );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Skip external requests (except Vue.js CDN)
    if (url.origin !== location.origin && !url.href.includes('unpkg.com')) {
        return;
    }
    
    event.respondWith(
        caches.match(request)
            .then((cachedResponse) => {
                // Return cached version if available
                if (cachedResponse) {
                    // For videos.json, try to update in background
                    if (request.url.includes('videos.json')) {
                        updateVideoCache(request);
                    }
                    return cachedResponse;
                }
                
                // Fetch from network and cache
                return fetch(request)
                    .then((networkResponse) => {
                        // Don't cache if not successful
                        if (!networkResponse || networkResponse.status !== 200) {
                            return networkResponse;
                        }
                        
                        // Clone response for caching
                        const responseClone = networkResponse.clone();
                        
                        // Determine cache type
                        const cacheType = isStaticFile(request.url) ? STATIC_CACHE : DYNAMIC_CACHE;
                        
                        caches.open(cacheType)
                            .then((cache) => {
                                cache.put(request, responseClone);
                            });
                        
                        return networkResponse;
                    })
                    .catch((error) => {
                        console.log('Network request failed:', error);
                        
                        // Return offline fallback for HTML requests
                        if (request.headers.get('accept').includes('text/html')) {
                            return caches.match('/index.html');
                        }
                        
                        // Return empty response for other requests
                        return new Response('Offline', {
                            status: 503,
                            statusText: 'Service Unavailable'
                        });
                    });
            })
    );
});

// Background sync for updating video cache
function updateVideoCache(request) {
    fetch(request)
        .then((response) => {
            if (response && response.status === 200) {
                caches.open(DYNAMIC_CACHE)
                    .then((cache) => {
                        cache.put(request, response.clone());
                    });
            }
        })
        .catch((error) => {
            console.log('Background update failed:', error);
        });
}

// Check if file is static
function isStaticFile(url) {
    return STATIC_FILES.some(staticFile => url.includes(staticFile)) ||
           url.includes('.css') ||
           url.includes('.js') ||
           url.includes('.png') ||
           url.includes('.jpg') ||
           url.includes('.svg') ||
           url.includes('.ico');
}

// Handle background sync
self.addEventListener('sync', (event) => {
    console.log('Background sync triggered:', event.tag);
    
    if (event.tag === 'update-videos') {
        event.waitUntil(
            fetch('/videos.json')
                .then((response) => {
                    if (response && response.status === 200) {
                        return caches.open(DYNAMIC_CACHE)
                            .then((cache) => {
                                return cache.put('/videos.json', response);
                            });
                    }
                })
                .catch((error) => {
                    console.log('Background sync failed:', error);
                })
        );
    }
});

// Handle push notifications (for future use)
self.addEventListener('push', (event) => {
    console.log('Push notification received:', event);
    
    const options = {
        body: event.data ? event.data.text() : 'New videos available!',
        icon: '/icons/icon-192x192.png',
        badge: '/icons/icon-72x72.png',
        vibrate: [200, 100, 200],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'View Videos',
                icon: '/icons/checkmark.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/icons/xmark.png'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('GenTube', options)
    );
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
    console.log('Notification clicked:', event);
    
    event.notification.close();
    
    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Handle messages from main thread
self.addEventListener('message', (event) => {
    console.log('Message received:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'UPDATE_CACHE') {
        event.waitUntil(
            caches.open(DYNAMIC_CACHE)
                .then((cache) => {
                    return cache.add('/videos.json');
                })
        );
    }
});

// Periodic background sync (for browsers that support it)
self.addEventListener('periodicsync', (event) => {
    console.log('Periodic sync triggered:', event.tag);
    
    if (event.tag === 'update-content') {
        event.waitUntil(
            updateVideoCache(new Request('/videos.json'))
        );
    }
});

// Handle errors
self.addEventListener('error', (event) => {
    console.error('Service Worker error:', event.error);
});

self.addEventListener('unhandledrejection', (event) => {
    console.error('Service Worker unhandled rejection:', event.reason);
});

console.log('Service Worker loaded successfully');