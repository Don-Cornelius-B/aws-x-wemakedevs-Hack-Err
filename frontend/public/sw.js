self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open('v1').then((cache) => {
            return cache.addAll([
                '/',
                '/index.html',
                '/manifest.json'
            ]);
        })
    );
});

self.addEventListener('fetch', (event) => {
    // Cache-first for static assets, network-first for API
    if (event.request.url.includes('/api/')) {
        event.respondWith(
            fetch(event.request).catch(() => caches.match(event.request))
        );
    } else {
        event.respondWith(
            caches.match(event.request).then((response) => {
                return response || fetch(event.request);
            })
        );
    }
});

self.addEventListener('sync', (event) => {
    if (event.tag === 'sync-reports') {
        // In a real implementation, we would access IndexedDB here
        // and POST pending reports to /api/sync/push
        console.log('Background sync event fired: sync-reports');
    }
});
