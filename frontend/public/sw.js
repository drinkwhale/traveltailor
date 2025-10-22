/* eslint-disable no-restricted-globals */
const VERSION = 'v1';
const STATIC_CACHE = `traveltailor-static-${VERSION}`;
const API_CACHE = `traveltailor-api-${VERSION}`;
const MAP_TILE_CACHE = `traveltailor-map-${VERSION}`;
const MAP_TILE_MAX_ENTRIES = 700; // ~50MB assuming 70KB avg tile size

const STATIC_ASSETS = [
  '/',
  '/favicon.ico',
  '/manifest.json',
  '/fonts/pretendard.css',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches
      .open(STATIC_CACHE)
      .then((cache) => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting()),
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(
          keys
            .filter((key) => ![STATIC_CACHE, API_CACHE, MAP_TILE_CACHE].includes(key))
            .map((key) => caches.delete(key)),
        ),
      )
      .then(() => self.clients.claim()),
  );
});

function cacheFirst(request) {
  return caches.match(request).then((cached) => cached || fetch(request));
}

function networkFirst(request) {
  return fetch(request)
    .then((response) => {
      const clone = response.clone();
      caches.open(API_CACHE).then((cache) => cache.put(request, clone));
      return response;
    })
    .catch(() =>
      caches.match(request).then((cached) => {
        if (cached) {
          return cached;
        }
        return new Response(JSON.stringify({ offline: true }), {
          status: 503,
          headers: { 'Content-Type': 'application/json' },
        });
      }),
    );
}

async function staleWhileRevalidate(request) {
  const cache = await caches.open(API_CACHE);
  const cached = await cache.match(request);
  const networkPromise = fetch(request)
    .then((response) => {
      cache.put(request, response.clone());
      return response;
    })
    .catch(() => cached);
  return cached || networkPromise;
}

async function handleMapTile(request) {
  const cache = await caches.open(MAP_TILE_CACHE);
  const cached = await cache.match(request);
  const fetchPromise = fetch(request)
    .then(async (response) => {
      await cache.put(request, response.clone());
      const keys = await cache.keys();
      if (keys.length > MAP_TILE_MAX_ENTRIES) {
        await cache.delete(keys[0]);
      }
      return response;
    })
    .catch(() => cached);
  return cached || fetchPromise;
}

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  if (request.method !== 'GET') {
    return;
  }

  if (url.origin === self.location.origin) {
    if (STATIC_ASSETS.includes(url.pathname)) {
      event.respondWith(cacheFirst(request));
      return;
    }
  }

  if (url.pathname.startsWith('/_next/static/')) {
    event.respondWith(cacheFirst(request));
    return;
  }

  if (url.hostname.includes('tiles.mapbox.com') || url.pathname.includes('/mapbox/tile')) {
    event.respondWith(handleMapTile(request));
    return;
  }

  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(request));
    return;
  }

  event.respondWith(staleWhileRevalidate(request));
});
