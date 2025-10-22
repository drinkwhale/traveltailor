/**
 * IndexedDB based offline storage and sync queue.
 *
 * The queue stores mutating API requests when the network is unavailable and
 * replays them once connectivity is restored.  Each entry is bucketed by
 * endpoint so replay order stays consistent per resource type.
 */

type QueueItem = {
  id: string;
  endpoint: string;
  method: string;
  payload: unknown;
  createdAt: number;
};

const DB_NAME = 'traveltailor-offline';
const STORE_NAME = 'sync-queue';
const DB_VERSION = 1;

function openDatabase(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        const store = db.createObjectStore(STORE_NAME, { keyPath: 'id' });
        store.createIndex('endpoint', 'endpoint');
        store.createIndex('createdAt', 'createdAt');
      }
    };

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function withStore<T>(mode: IDBTransactionMode, callback: (store: IDBObjectStore) => Promise<T> | T): Promise<T> {
  const db = await openDatabase();
  return new Promise<T>((resolve, reject) => {
    const transaction = db.transaction(STORE_NAME, mode);
    const store = transaction.objectStore(STORE_NAME);
    let resultValue: T;

    transaction.oncomplete = () => resolve(resultValue);
    transaction.onerror = () => reject(transaction.error);

    Promise.resolve(callback(store))
      .then((value) => {
        resultValue = value;
      })
      .catch((error) => {
        transaction.abort();
        reject(error);
      });
  });
}

export async function enqueueRequest(item: QueueItem): Promise<void> {
  await withStore('readwrite', (store) => {
    store.put(item);
  });
}

export async function dequeueAll(): Promise<QueueItem[]> {
  return withStore('readwrite', (store) => {
    return new Promise<QueueItem[]>((resolve, reject) => {
      const items: QueueItem[] = [];
      const request = store.index('createdAt').openCursor();

      request.onsuccess = () => {
        const cursor = request.result;
        if (cursor) {
          items.push(cursor.value as QueueItem);
          cursor.delete();
          cursor.continue();
        } else {
          resolve(items);
        }
      };
      request.onerror = () => reject(request.error);
    });
  });
}

export async function pendingRequests(): Promise<QueueItem[]> {
  return withStore('readonly', (store) => {
    return new Promise<QueueItem[]>((resolve, reject) => {
      const items: QueueItem[] = [];
      const request = store.index('createdAt').openCursor();
      request.onsuccess = () => {
        const cursor = request.result;
        if (cursor) {
          items.push(cursor.value as QueueItem);
          cursor.continue();
        } else {
          resolve(items);
        }
      };
      request.onerror = () => reject(request.error);
    });
  });
}

export async function clearQueue(): Promise<void> {
  await withStore('readwrite', (store) => {
    store.clear();
  });
}

export type { QueueItem };
