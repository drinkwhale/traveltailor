'use client'

import { useNetworkStatus } from '@/hooks/useNetworkStatus'
import { apiClient } from '@/lib/api'

export function NetworkStatusBanner() {
  const { isOnline, pendingCount } = useNetworkStatus(async (item) => {
    await apiClient.request({
      url: item.endpoint,
      method: item.method,
      data: item.payload,
    })
  })

  if (isOnline && pendingCount === 0) {
    return null
  }

  return (
    <div className="fixed bottom-4 left-1/2 z-50 -translate-x-1/2 rounded-md bg-gray-900 px-4 py-2 text-sm text-white shadow-lg">
      {!isOnline ? '오프라인 모드 - 작업이 큐에 저장됩니다.' : `대기 중 동기화 ${pendingCount}건`}
    </div>
  )
}
