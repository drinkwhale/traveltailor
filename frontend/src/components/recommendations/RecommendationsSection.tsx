'use client'

import { useMemo } from 'react'

import { AccommodationCard } from './AccommodationCard'
import { FlightCard } from './FlightCard'
import type {
  AccommodationRecommendations,
  FlightRecommendations,
} from '@shared-types/recommendations'

interface RecommendationsSectionProps {
  flights?: FlightRecommendations
  accommodations?: AccommodationRecommendations
  isLoading: boolean
  error?: string
  hasFetched: boolean
  onRefresh: () => Promise<void>
}

export function RecommendationsSection({
  flights,
  accommodations,
  isLoading,
  error,
  hasFetched,
  onRefresh,
}: RecommendationsSectionProps) {
  const hasData =
    (flights && flights.options.length > 0) || (accommodations && accommodations.options.length > 0)

  const headingDetail = useMemo(() => {
    if (flights && flights.origin_airport && flights.destination_airport) {
      return `${flights.origin_airport} ↔ ${flights.destination_airport}`
    }
    return undefined
  }, [flights])

  return (
    <section className="flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">추천 항공 & 숙박 옵션</h2>
          <p className="text-sm text-slate-500">
            최신 항공편과 숙박 제휴 링크를 한 곳에서 확인하고, 바로 예약으로 연결해보세요.
          </p>
          {headingDetail ? (
            <p className="text-xs text-slate-400">항공 노선: {headingDetail}</p>
          ) : null}
        </div>
        <button
          type="button"
          onClick={() => {
            void onRefresh()
          }}
          disabled={isLoading}
          className="inline-flex items-center gap-1 self-start rounded-full border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-600 transition hover:border-blue-200 hover:text-blue-700 disabled:cursor-not-allowed disabled:border-slate-100 disabled:text-slate-300"
        >
          {isLoading ? '갱신 중...' : '추천 새로고침'}
          <span aria-hidden>⟳</span>
        </button>
      </div>

      {error ? (
        <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          {error}
        </div>
      ) : null}

      {isLoading && !hasData ? (
        <div className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-6 text-sm text-slate-500">
          추천 정보를 불러오는 중입니다...
        </div>
      ) : null}

      {!isLoading && !hasData && hasFetched ? (
        <div className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-6 text-sm text-slate-500">
          현재 표시할 추천 항공편 또는 숙박 정보가 없습니다. 새로고침으로 다시 시도해보세요.
        </div>
      ) : null}

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-slate-800">항공편 추천</h3>
          {flights?.options.map((option) => (
            <FlightCard key={option.id} option={option} />
          ))}
          {!flights || flights.options.length === 0 ? (
            <p className="rounded-lg border border-dashed border-slate-200 px-4 py-6 text-center text-xs text-slate-400">
              항공편 추천이 아직 준비되지 않았습니다.
            </p>
          ) : null}
        </div>

        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-slate-800">숙박 추천</h3>
          {accommodations?.options.map((option) => (
            <AccommodationCard key={option.id} option={option} />
          ))}
          {!accommodations || accommodations.options.length === 0 ? (
            <p className="rounded-lg border border-dashed border-slate-200 px-4 py-6 text-center text-xs text-slate-400">
              숙박 추천이 아직 준비되지 않았습니다.
            </p>
          ) : null}
        </div>
      </div>
    </section>
  )
}
