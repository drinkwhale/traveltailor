'use client'

import type { FlightOption } from '@shared-types/recommendations'

interface FlightCardProps {
  option: FlightOption
}

const DATE_FORMAT = new Intl.DateTimeFormat('ko-KR', {
  month: 'short',
  day: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
})

function formatDateTime(value: string) {
  const date = new Date(value)
  return DATE_FORMAT.format(date)
}

function formatDuration(minutes: number) {
  if (!minutes || minutes <= 0) {
    return '소요 시간 정보 없음'
  }
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  const parts = []
  if (hours > 0) parts.push(`${hours}시간`)
  if (mins > 0) parts.push(`${mins}분`)
  return parts.join(' ') || `${minutes}분`
}

function formatPrice(amount: number, currency: string) {
  try {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: currency || 'KRW',
      currencyDisplay: 'narrowSymbol',
    }).format(amount)
  } catch {
    return `${amount.toLocaleString()} ${currency}`
  }
}

export function FlightCard({ option }: FlightCardProps) {
  const stopsLabel = option.stops === 0 ? '직항' : `${option.stops}회 경유`

  return (
    <article className="flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition hover:border-blue-200 hover:shadow">
      <header className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="rounded-full bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700">
              {option.provider}
            </span>
            <p className="text-xs text-slate-500">{stopsLabel}</p>
          </div>
          <h3 className="mt-1 text-sm font-semibold text-slate-900">
            {option.carrier} · {option.flight_number}
          </h3>
          <p className="text-xs text-slate-500">
            {option.departure_airport} → {option.arrival_airport}
          </p>
        </div>
        <div className="text-right">
          <p className="text-sm font-semibold text-blue-600">
            {formatPrice(option.price_amount, option.price_currency)}
          </p>
          <p className="text-[11px] text-slate-400">
            업데이트: {formatDateTime(option.updated_at)}
          </p>
        </div>
      </header>

      <dl className="grid grid-cols-2 gap-3 text-xs text-slate-600 lg:grid-cols-4">
        <div>
          <dt className="font-medium text-slate-500">출발</dt>
          <dd className="mt-0.5 text-slate-700">{formatDateTime(option.departure_time)}</dd>
        </div>
        <div>
          <dt className="font-medium text-slate-500">도착</dt>
          <dd className="mt-0.5 text-slate-700">{formatDateTime(option.arrival_time)}</dd>
        </div>
        <div>
          <dt className="font-medium text-slate-500">총 소요 시간</dt>
          <dd className="mt-0.5 text-slate-700">{formatDuration(option.duration_minutes)}</dd>
        </div>
        <div>
          <dt className="font-medium text-slate-500">좌석 등급</dt>
          <dd className="mt-0.5 text-slate-700">{option.seat_class ?? '정보 없음'}</dd>
        </div>
      </dl>

      <footer className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-[11px] text-slate-400">
          수하물: {option.baggage_info ? '포함' : '정보 없음'}
        </p>
        <a
          href={option.booking_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 rounded-full bg-blue-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-700"
        >
          예약하기
          <span aria-hidden>↗</span>
        </a>
      </footer>
    </article>
  )
}
