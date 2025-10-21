'use client'

import { useMemo } from 'react'

import { detectDevice } from '@/lib/device-detector'
import { getGoogleMapLink } from '@/lib/google-map-link'
import { getKakaoMapLink } from '@/lib/kakao-map-link'
import type { MapDay } from '@shared-types/map'

interface ExportButtonsProps {
  day: MapDay
}

export function ExportButtons({ day }: ExportButtonsProps) {
  const device = useMemo(() => detectDevice(), [])
  const isDisabled = day.markers.length === 0

  const googleLink = isDisabled ? '#' : getGoogleMapLink(day, device)
  const kakaoLink = isDisabled ? '#' : getKakaoMapLink(day, device)

  return (
    <div className="flex flex-wrap gap-2">
      <a
        href={googleLink}
        target="_blank"
        rel="noopener noreferrer"
        className={`inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-medium ${
          isDisabled
            ? 'cursor-not-allowed border-slate-200 bg-slate-100 text-slate-400'
            : 'border-slate-200 bg-white text-slate-700 hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700'
        }`}
        aria-disabled={isDisabled}
      >
        <span role="img" aria-hidden>
          🗺️
        </span>
        Google 지도 열기
      </a>
      <a
        href={kakaoLink}
        target="_blank"
        rel="noopener noreferrer"
        className={`inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-medium ${
          isDisabled
            ? 'cursor-not-allowed border-slate-200 bg-slate-100 text-slate-400'
            : 'border-yellow-200 bg-yellow-50 text-yellow-700 hover:border-yellow-300 hover:bg-yellow-100'
        }`}
        aria-disabled={isDisabled}
      >
        <span role="img" aria-hidden>
          🧭
        </span>
        카카오맵으로 내보내기
      </a>
    </div>
  )
}
