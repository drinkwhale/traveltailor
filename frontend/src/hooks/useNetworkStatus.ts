import { useCallback, useEffect, useState } from 'react';

import { dequeueAll, enqueueRequest, QueueItem } from '@/lib/offline-storage';

type SyncHandler = (item: QueueItem) => Promise<void>;

export function useNetworkStatus(onSync?: SyncHandler) {
  const [isOnline, setIsOnline] = useState<boolean>(() =>
    typeof window === 'undefined' ? true : navigator.onLine,
  );
  const [pending, setPending] = useState<QueueItem[]>([]);

  const refreshQueue = useCallback(async () => {
    const queued = await dequeueAll();
    if (!queued.length) {
      setPending([]);
      return;
    }

    if (!onSync) {
      setPending(queued);
      return;
    }

    for (const item of queued) {
      try {
        await onSync(item);
      } catch (error) {
        // If syncing fails, push the item back for later retry
        await enqueueRequest(item);
        console.error('Failed to sync offline request', error);
      }
    }
    setPending([]);
  }, [onSync]);

  useEffect(() => {
    function onlineHandler() {
      setIsOnline(true);
      refreshQueue();
    }

    function offlineHandler() {
      setIsOnline(false);
    }

    window.addEventListener('online', onlineHandler);
    window.addEventListener('offline', offlineHandler);

    if (navigator.onLine) {
      refreshQueue();
    }

    return () => {
      window.removeEventListener('online', onlineHandler);
      window.removeEventListener('offline', offlineHandler);
    };
  }, [refreshQueue]);

  return { isOnline, pendingCount: pending.length, pending };
}
