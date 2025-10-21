'use client'

import type { MapMarker } from '@shared-types/map'

interface PlacePopupProps {
  marker: MapMarker
}

export function PlacePopup({ marker }: PlacePopupProps) {
  return (
    <div className="space-y-1 text-left">
      <p className="text-sm font-semibold text-slate-900">{marker.name}</p>
      <p className="text-xs uppercase tracking-wide text-slate-500">{marker.category}</p>
      {marker.visit_time ? (
        <p className="text-xs text-slate-600">방문 시간: {marker.visit_time}</p>
      ) : null}
      {marker.address ? <p className="text-xs text-slate-500">{marker.address}</p> : null}
    </div>
  )
}
