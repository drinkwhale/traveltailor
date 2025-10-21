'use client'

import { useEffect, useState } from 'react'

import type { MapBounds, MapDay } from '@shared-types/map'

import { MapView } from './MapView'
import { RouteInfo } from './RouteInfo'

interface RouteMapProps {
  bounds: MapBounds
  day: MapDay
}

export function RouteMap({ bounds, day }: RouteMapProps) {
  const [activeRouteId, setActiveRouteId] = useState<string | null>(null)

  useEffect(() => {
    setActiveRouteId(day.routes[0]?.id ?? null)
  }, [day.day_number, day.routes])

  return (
    <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr),320px]">
      <div className="h-[420px] rounded-xl border border-slate-200 bg-white shadow-sm">
        <MapView
          bounds={bounds}
          markers={day.markers}
          routes={day.routes}
          activeRouteId={activeRouteId}
          onRouteSelect={setActiveRouteId}
        />
      </div>
      <RouteInfo
        day={day}
        selectedRouteId={activeRouteId}
        onSelectRoute={setActiveRouteId}
      />
    </div>
  )
}
