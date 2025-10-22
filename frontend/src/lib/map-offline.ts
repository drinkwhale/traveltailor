/**
 * Map tile helper for offline caching control.
 */

const MAP_CACHE = 'traveltailor-map-v1';

export async function cacheTile(url: string): Promise<void> {
  if (!('caches' in window)) {
    return;
  }
  const cache = await caches.open(MAP_CACHE);
  const response = await fetch(url, { mode: 'no-cors' });
  await cache.put(url, response);
}

export async function isTileCached(url: string): Promise<boolean> {
  if (!('caches' in window)) {
    return false;
  }
  const cache = await caches.open(MAP_CACHE);
  return Boolean(await cache.match(url));
}

export async function clearTileCache(): Promise<void> {
  if (!('caches' in window)) {
    return;
  }
  const keys = await caches.keys();
  await Promise.all(keys.filter((key) => key.startsWith('traveltailor-map-')).map((key) => caches.delete(key)));
}
