'use client'

import type { DailyItinerary, RouteSegment } from '@shared-types/travel-plan'

import { PlaceCard } from './PlaceCard'

interface DailyTimelineProps {
  itinerary: DailyItinerary
}

function RoutePill({ route }: { route: RouteSegment }) {
  return (
    <div className="ml-6 border-l border-dashed border-slate-300 pl-4">
      <div className="rounded-md bg-slate-100 px-3 py-2 text-xs text-slate-600">
        <p className="font-medium text-slate-700">이동 수단: {route.transport_mode}</p>
        <p>
          거리: {route.distance_meters ? `${(route.distance_meters / 1000).toFixed(1)}km` : '정보 없음'} · 시간:{' '}
          {route.duration_minutes ? `${route.duration_minutes}분` : '정보 없음'}
        </p>
        {route.estimated_cost ? <p>예상 비용: {route.estimated_cost.toLocaleString()}원</p> : null}
      </div>
    </div>
  )
}

export function DailyTimeline({ itinerary }: DailyTimelineProps) {
  const formattedDate = new Date(itinerary.date).toLocaleDateString('ko-KR', {
    month: 'long',
    day: 'numeric',
    weekday: 'short',
  })

  return (
    <section className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <header>
        <h3 className="text-lg font-semibold text-slate-900">
          Day {itinerary.day_number} · {formattedDate}
        </h3>
        {itinerary.theme ? <p className="text-sm text-slate-600">{itinerary.theme}</p> : null}
        {itinerary.notes ? <p className="mt-1 text-xs text-slate-500">{itinerary.notes}</p> : null}
      </header>

      <div className="space-y-6">
        {itinerary.places.map((place) => {
          const route = itinerary.routes.find((r) => r.from_order === place.visit_order)
          return (
            <div key={place.id} className="space-y-3">
              <PlaceCard place={place} />
              {route ? <RoutePill route={route} /> : null}
            </div>
          )
        })}
      </div>
    </section>
  )
}

