'use client'

import type { TravelPlanStatus } from '@shared-types/travel-plan'

interface ProgressIndicatorProps {
  status?: TravelPlanStatus
  isLoading?: boolean
}

export function ProgressIndicator({ status, isLoading }: ProgressIndicatorProps) {
  const progressValue = status?.progress ?? 0
  const statusLabel = status?.status ?? (isLoading ? 'generating' : 'idle')
  const message = status?.message

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-slate-700">생성 상태</span>
        <span className="text-xs uppercase tracking-wide text-slate-500">
          {isLoading ? '처리 중' : statusLabel}
        </span>
      </div>
      <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-slate-100">
        <div
          className="h-full rounded-full bg-indigo-500 transition-all"
          style={{ width: `${Math.min(progressValue * 100, 100)}%` }}
        />
      </div>
      {message ? <p className="mt-2 text-sm text-slate-600">{message}</p> : null}
    </div>
  )
}

