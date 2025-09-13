const CACHE_NAME = 'salo-v1757346483';
const urlsToCache = ["/", "/index.html", "/manifest.json"];

// Install event - cache resources
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(urlsToCache);
    }),
  );
});

// Fetch event - network-first for HTML, cache-first for assets
self.addEventListener("fetch", (event) => {
  console.log("Version SW:", CACHE_NAME);

  // Network-first for HTML and manifest
  if (
    event.request.url.endsWith("/") ||
    event.request.url.endsWith(".html") ||
    event.request.url.endsWith("manifest.json")
  ) {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          // Cache the fresh response
          const responseClone = response.clone();
          caches
            .open(CACHE_NAME)
            .then((cache) => cache.put(event.request, responseClone));
          return response;
        })
        .catch(() => caches.match(event.request)), // Fallback to cache if offline
    );
  } else {
    // Cache-first for other resources
    event.respondWith(
      caches
        .match(event.request)
        .then((response) => response || fetch(event.request)),
    );
  }
});

// Activate event - clean up old caches
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        }),
      );
    }),
  );
});
