'use client'

import type { MapDay, MapMarker } from '@shared-types/map'

import { detectDevice, type DeviceType } from './device-detector'

interface ResolvedLink {
  web: string
  mobile?: string | null
}

function buildFallbackLink(markers: MapMarker[]): ResolvedLink {
  if (markers.length === 0) {
    return { web: 'https://www.google.com/maps' }
  }

  const origin = markers[0]
  const destination = markers[markers.length - 1]
  const waypoints = markers.slice(1, -1)

  const params = new URLSearchParams({
    api: '1',
    origin: `${origin.latitude.toFixed(6)},${origin.longitude.toFixed(6)}`,
    destination: `${destination.latitude.toFixed(6)},${destination.longitude.toFixed(6)}`,
    travelmode: 'driving',
  })

  if (waypoints.length) {
    params.set(
      'waypoints',
      waypoints
        .map((marker) => `${marker.latitude.toFixed(6)},${marker.longitude.toFixed(6)}`)
        .join('|')
    )
  }

  const base = `https://www.google.com/maps/dir/?${params.toString()}`
  return { web: base, mobile: base }
}

function resolveLinks(day: MapDay): ResolvedLink {
  if (day.export_links?.google_maps) {
    return day.export_links.google_maps
  }
  return buildFallbackLink(day.markers)
}

export function getGoogleMapLink(day: MapDay, device: DeviceType = detectDevice()): string {
  const links = resolveLinks(day)
  if (device === 'desktop' || !links.mobile) {
    return links.web
  }
  return links.mobile
}
