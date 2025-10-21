'use client'

import type { MapDay, MapMarker } from '@shared-types/map'

import { detectDevice, type DeviceType } from './device-detector'

interface ResolvedLink {
  web: string
  mobile?: string | null
}

function buildFallbackLink(markers: MapMarker[]): ResolvedLink {
  if (markers.length === 0) {
    return { web: 'https://map.kakao.com' }
  }

  const segments = markers.map((marker) => {
    const value = `${marker.name},${marker.latitude.toFixed(6)},${marker.longitude.toFixed(6)}`
    return encodeURIComponent(value).replace(/%2C/g, ',')
  })

  const origin = markers[0]
  const destination = markers[markers.length - 1]

  const mobile = `kakaomap://route?sp=${origin.latitude.toFixed(6)},${origin.longitude.toFixed(
    6
  )}&ep=${destination.latitude.toFixed(6)},${destination.longitude.toFixed(6)}&by=CAR`

  return {
    web: `https://map.kakao.com/link/route/${segments.join('/')}`,
    mobile,
  }
}

function resolveLinks(day: MapDay): ResolvedLink {
  if (day.export_links?.kakao_map) {
    return day.export_links.kakao_map
  }
  return buildFallbackLink(day.markers)
}

export function getKakaoMapLink(day: MapDay, device: DeviceType = detectDevice()): string {
  const links = resolveLinks(day)
  if (device === 'desktop' || !links.mobile) {
    return links.web
  }
  return links.mobile
}
