'use client'

import type { MapDay, MapRoute } from '@shared-types/map'

interface RouteInfoProps {
  day: MapDay
  selectedRouteId?: string | null
  onSelectRoute?: (routeId: string) => void
}

const transportLabels: Record<string, string> = {
  walking: '도보',
  driving: '차량',
  taxi: '택시',
  public_transit: '대중교통',
  bicycle: '자전거',
}

function formatDistance(distance?: number) {
  if (!distance) return '거리 정보 없음'
  if (distance < 1000) return `${distance} m`
  return `${(distance / 1000).toFixed(1)} km`
}

function formatDuration(duration?: number) {
  if (!duration) return '시간 정보 없음'
  if (duration < 60) return `${duration}분`
  const hours = Math.floor(duration / 60)
  const minutes = duration % 60
  return minutes === 0 ? `${hours}시간` : `${hours}시간 ${minutes}분`
}

function renderSummary(day: MapDay) {
  const distance = formatDistance(day.summary.total_distance_meters)
  const duration = formatDuration(day.summary.total_duration_minutes)
  return `${distance} · ${duration}`
}

function StepList({ route }: { route: MapRoute }) {
  if (!route.steps.length) {
    return (
      <p className="text-xs text-slate-500">
        세부 경로 안내를 불러오지 못했습니다. 지도에서 경로를 확인하세요.
      </p>
    )
  }

  return (
    <ol className="space-y-2 text-xs text-slate-600">
      {route.steps.map((step, index) => (
        <li key={`${route.id}-step-${index}`} className="flex items-start gap-2">
          <span className="mt-0.5 h-5 w-5 flex-shrink-0 rounded-full bg-slate-200 text-center text-[10px] font-semibold leading-5 text-slate-700">
            {index + 1}
          </span>
          <div className="space-y-1">
            <p className="font-medium text-slate-700">{step.instruction || '다음 지시를 따르세요.'}</p>
            <p className="text-[11px] text-slate-500">
              {formatDistance(Math.round(step.distance_meters))} ·{' '}
              {formatDuration(Math.max(1, Math.round(step.duration_seconds / 60)))}
            </p>
          </div>
        </li>
      ))}
    </ol>
  )
}

export function RouteInfo({ day, selectedRouteId, onSelectRoute }: RouteInfoProps) {
  const selectedRoute = selectedRouteId
    ? day.routes.find((route) => route.id === selectedRouteId)
    : day.routes[0]

  return (
    <aside className="space-y-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <header className="space-y-1">
        <p className="text-sm font-semibold text-slate-900">
          Day {day.day_number} 경로 요약
        </p>
        <p className="text-xs text-slate-500">{renderSummary(day)}</p>
      </header>

      {day.routes.length === 0 ? (
        <p className="text-xs text-slate-500">
          이 날은 이동 경로가 없습니다. 지도에서 방문지를 확인하세요.
        </p>
      ) : (
        <div className="space-y-3">
          <div className="space-y-2">
            {day.routes.map((route) => {
              const isActive = selectedRoute?.id === route.id
              return (
                <button
                  key={route.id}
                  type="button"
                  onClick={() => onSelectRoute?.(route.id)}
                  className={`w-full rounded-lg border px-3 py-2 text-left ${
                    isActive
                      ? 'border-blue-200 bg-blue-50 text-blue-700'
                      : 'border-slate-200 text-slate-700 hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700'
                  }`}
                >
                  <p className="text-xs font-medium">
                    {transportLabels[route.transport_mode] ?? '이동'} ·{' '}
                    {formatDistance(route.distance_meters)}
                  </p>
                  <p className="text-[11px] text-slate-500">
                    소요 시간: {formatDuration(route.duration_minutes)}
                  </p>
                </button>
              )
            })}
          </div>

          {selectedRoute ? (
            <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
              <p className="text-xs font-semibold text-slate-700">
                세부 안내
              </p>
              <StepList route={selectedRoute} />
            </div>
          ) : null}
        </div>
      )}
    </aside>
  )
}
