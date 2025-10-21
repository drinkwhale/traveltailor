'use client'

import type { AccommodationOption } from '@shared-types/recommendations'

interface AccommodationCardProps {
  option: AccommodationOption
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

function formatStay(option: AccommodationOption) {
  if (!option.check_in_date || !option.check_out_date) {
    return null
  }
  const nights = option.nights ?? 0
  return `${option.check_in_date} ~ ${option.check_out_date} · ${nights}박`
}

export function AccommodationCard({ option }: AccommodationCardProps) {
  const stayInfo = formatStay(option)
  const amenities = option.amenities?.slice(0, 3) ?? []

  return (
    <article className="flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition hover:border-emerald-200 hover:shadow">
      <header className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="rounded-full bg-emerald-50 px-2 py-1 text-xs font-medium text-emerald-700">
              {option.provider}
            </span>
            {typeof option.rating === 'number' ? (
              <span className="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2 py-1 text-xs text-amber-700">
                ⭐ {option.rating.toFixed(1)}
                {option.review_count ? (
                  <span className="text-[11px] text-amber-600">
                    ({option.review_count.toLocaleString()} 리뷰)
                  </span>
                ) : null}
              </span>
            ) : null}
          </div>
          <h3 className="mt-1 text-sm font-semibold text-slate-900">{option.name}</h3>
          <p className="text-xs text-slate-500">{option.address ?? option.city ?? '주소 정보 없음'}</p>
          {stayInfo ? <p className="text-[11px] text-slate-400">{stayInfo}</p> : null}
        </div>
        <div className="text-right">
          <p className="text-sm font-semibold text-emerald-600">
            {formatPrice(option.total_price, option.price_currency)}
          </p>
          {option.price_per_night ? (
            <p className="text-[11px] text-slate-400">
              1박 기준 {formatPrice(option.price_per_night, option.price_currency)}
            </p>
          ) : null}
        </div>
      </header>

      {amenities.length > 0 ? (
        <ul className="flex flex-wrap gap-2 text-[11px] text-slate-500">
          {amenities.map((amenity) => (
            <li
              key={amenity}
              className="rounded-full bg-slate-100 px-2 py-1 text-slate-600"
            >
              {amenity}
            </li>
          ))}
        </ul>
      ) : null}

      <footer className="flex justify-end">
        <a
          href={option.booking_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 rounded-full bg-emerald-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-emerald-700"
        >
          예약 페이지 열기
          <span aria-hidden>↗</span>
        </a>
      </footer>
    </article>
  )
}
