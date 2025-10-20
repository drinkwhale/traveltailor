/**
 * Mapbox GL JS 설정 및 유틸리티
 *
 * Mapbox를 사용한 지도 시각화 및 경로 표시
 */

import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'

/**
 * Mapbox 액세스 토큰 설정
 */
const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN

if (!MAPBOX_TOKEN) {
  console.warn(
    'Mapbox 액세스 토큰이 설정되지 않았습니다. ' +
    'NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN 환경 변수를 확인하세요.'
  )
} else {
  mapboxgl.accessToken = MAPBOX_TOKEN
}

/**
 * 기본 지도 스타일
 */
export const MAP_STYLES = {
  streets: 'mapbox://styles/mapbox/streets-v12',
  outdoors: 'mapbox://styles/mapbox/outdoors-v12',
  light: 'mapbox://styles/mapbox/light-v11',
  dark: 'mapbox://styles/mapbox/dark-v11',
  satellite: 'mapbox://styles/mapbox/satellite-v9',
  satelliteStreets: 'mapbox://styles/mapbox/satellite-streets-v12',
} as const

/**
 * 기본 지도 설정
 */
export const DEFAULT_MAP_CONFIG = {
  style: MAP_STYLES.streets,
  center: [126.9780, 37.5665] as [number, number], // 서울 중심
  zoom: 12,
  pitch: 0,
  bearing: 0,
}

/**
 * 좌표 타입
 */
export interface Coordinates {
  latitude: number
  longitude: number
}

/**
 * 마커 타입
 */
export interface MapMarker {
  id: string
  coordinates: Coordinates
  title?: string
  description?: string
  color?: string
}

/**
 * 경로 타입
 */
export interface Route {
  coordinates: [number, number][]
  color?: string
  width?: number
}

/**
 * 지도 인스턴스 생성
 */
export function createMapInstance(
  container: string | HTMLElement,
  options?: Partial<mapboxgl.MapboxOptions>
): mapboxgl.Map {
  return new mapboxgl.Map({
    container,
    ...DEFAULT_MAP_CONFIG,
    ...options,
  })
}

/**
 * 마커 추가
 */
export function addMarker(
  map: mapboxgl.Map,
  marker: MapMarker
): mapboxgl.Marker {
  const el = document.createElement('div')
  el.className = 'custom-marker'
  el.style.backgroundColor = marker.color || '#3b82f6'
  el.style.width = '30px'
  el.style.height = '30px'
  el.style.borderRadius = '50%'
  el.style.border = '3px solid white'
  el.style.boxShadow = '0 2px 4px rgba(0,0,0,0.3)'
  el.style.cursor = 'pointer'

  const mapboxMarker = new mapboxgl.Marker(el)
    .setLngLat([marker.coordinates.longitude, marker.coordinates.latitude])
    .addTo(map)

  // 팝업 추가 (제목이나 설명이 있는 경우)
  if (marker.title || marker.description) {
    const popup = new mapboxgl.Popup({ offset: 25 }).setHTML(`
      ${marker.title ? `<h3 class="font-bold text-lg mb-1">${marker.title}</h3>` : ''}
      ${marker.description ? `<p class="text-sm text-gray-600">${marker.description}</p>` : ''}
    `)
    mapboxMarker.setPopup(popup)
  }

  return mapboxMarker
}

/**
 * 경로 추가
 */
export function addRoute(
  map: mapboxgl.Map,
  route: Route,
  id: string = 'route'
): void {
  // 경로 소스 추가
  if (!map.getSource(id)) {
    map.addSource(id, {
      type: 'geojson',
      data: {
        type: 'Feature',
        properties: {},
        geometry: {
          type: 'LineString',
          coordinates: route.coordinates,
        },
      },
    })
  }

  // 경로 레이어 추가
  if (!map.getLayer(id)) {
    map.addLayer({
      id,
      type: 'line',
      source: id,
      layout: {
        'line-join': 'round',
        'line-cap': 'round',
      },
      paint: {
        'line-color': route.color || '#3b82f6',
        'line-width': route.width || 4,
        'line-opacity': 0.8,
      },
    })
  }
}

/**
 * 여러 좌표를 포함하는 영역으로 지도 이동
 */
export function fitBounds(
  map: mapboxgl.Map,
  coordinates: Coordinates[],
  options?: mapboxgl.FitBoundsOptions
): void {
  if (coordinates.length === 0) return

  const bounds = new mapboxgl.LngLatBounds()

  coordinates.forEach((coord) => {
    bounds.extend([coord.longitude, coord.latitude])
  })

  map.fitBounds(bounds, {
    padding: 50,
    ...options,
  })
}

/**
 * Mapbox Directions API를 사용한 경로 계산
 */
export async function getDirections(
  origin: Coordinates,
  destination: Coordinates,
  profile: 'driving' | 'walking' | 'cycling' = 'driving'
): Promise<any> {
  const url = `https://api.mapbox.com/directions/v5/mapbox/${profile}/${origin.longitude},${origin.latitude};${destination.longitude},${destination.latitude}`

  const response = await fetch(
    `${url}?geometries=geojson&access_token=${MAPBOX_TOKEN}`
  )

  if (!response.ok) {
    throw new Error('Failed to fetch directions')
  }

  return response.json()
}

/**
 * 거리 계산 (Haversine formula)
 */
export function calculateDistance(
  coord1: Coordinates,
  coord2: Coordinates
): number {
  const R = 6371 // 지구 반지름 (km)
  const dLat = ((coord2.latitude - coord1.latitude) * Math.PI) / 180
  const dLon = ((coord2.longitude - coord1.longitude) * Math.PI) / 180

  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((coord1.latitude * Math.PI) / 180) *
      Math.cos((coord2.latitude * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2)

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  const distance = R * c

  return Math.round(distance * 100) / 100 // 소수점 둘째자리까지
}

export { mapboxgl }
