'use client'

import type { ItineraryPlace } from '@shared-types/travel-plan'

interface PlaceCardProps {
  place: ItineraryPlace
}

export function PlaceCard({ place }: PlaceCardProps) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-semibold text-slate-900">{place.name}</p>
          <p className="text-xs text-slate-500">{place.address ?? '주소 정보 없음'}</p>
        </div>
        <span className="rounded-full bg-indigo-50 px-2 py-0.5 text-xs font-medium text-indigo-600">
          #{place.visit_order}
        </span>
      </div>
      <div className="mt-3 space-y-1 text-xs text-slate-600">
        <p>
          <span className="font-medium text-slate-700">유형:</span> {place.category}
        </p>
        {place.visit_time ? (
          <p>
            <span className="font-medium text-slate-700">시간:</span> {place.visit_time}
          </p>
        ) : null}
        {place.duration_minutes ? (
          <p>
            <span className="font-medium text-slate-700">체류:</span> 약 {place.duration_minutes}분
          </p>
        ) : null}
        {place.estimated_cost ? (
          <p>
            <span className="font-medium text-slate-700">예산:</span> {place.estimated_cost.toLocaleString()}원
          </p>
        ) : null}
        {place.ai_recommendation_reason ? (
          <p className="text-[11px] text-slate-500">{place.ai_recommendation_reason}</p>
        ) : null}
      </div>
    </div>
  )
}

