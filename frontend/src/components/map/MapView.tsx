'use client'

import { useEffect, useMemo, useRef } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'

import {
  createMapInstance,
  decodePolyline,
  mapboxgl,
} from '@/lib/mapbox'
import type { MapBounds, MapMarker, MapRoute } from '@shared-types/map'

import { PlacePopup } from './PlacePopup'

interface MapViewProps {
  bounds: MapBounds
  markers: MapMarker[]
  routes: MapRoute[]
  activeRouteId?: string | null
  onRouteSelect?: (routeId: string) => void
}

interface RouteLayer {
  layerId: string
  sourceId: string
}

export function MapView({
  bounds,
  markers,
  routes,
  activeRouteId,
  onRouteSelect,
}: MapViewProps) {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const mapRef = useRef<mapboxgl.Map | null>(null)
  const markersRef = useRef<mapboxgl.Marker[]>([])
  const routeLayersRef = useRef<RouteLayer[]>([])
  const routeClickHandlersRef = useRef<
    Array<{ layerId: string; handler: (event: mapboxgl.MapLayerMouseEvent) => void }>
  >([])

  const center = useMemo<[number, number]>(() => {
    const lat =
      (bounds.southwest.latitude + bounds.northeast.latitude) / 2
    const lng =
      (bounds.southwest.longitude + bounds.northeast.longitude) / 2
    return [lng, lat]
  }, [bounds])

  const markerMap = useMemo(() => {
    const map = new Map<string, MapMarker>()
    markers.forEach((marker) => map.set(marker.place_id, marker))
    return map
  }, [markers])

  useEffect(() => {
    if (!containerRef.current || mapRef.current) {
      return
    }

    const map = createMapInstance(containerRef.current, {
      center,
      zoom: 11,
    })
    mapRef.current = map

    const fitToBounds = () => {
      map.fitBounds(
        [
          [bounds.southwest.longitude, bounds.southwest.latitude],
          [bounds.northeast.longitude, bounds.northeast.latitude],
        ],
        { padding: 60, maxZoom: 13 }
      )
    }

    if (map.loaded()) {
      fitToBounds()
    } else {
      map.once('load', fitToBounds)
    }

    return () => {
      routeClickHandlersRef.current.forEach(({ layerId, handler }) => {
        map.off('click', layerId, handler)
      })
      routeClickHandlersRef.current = []

      markersRef.current.forEach((marker) => marker.remove())
      markersRef.current = []

      routeLayersRef.current.forEach(({ layerId, sourceId }) => {
        if (map.getLayer(layerId)) {
          map.removeLayer(layerId)
        }
        if (map.getSource(sourceId)) {
          map.removeSource(sourceId)
        }
      })
      routeLayersRef.current = []
      map.remove()
    }
  }, [bounds, center])

  useEffect(() => {
    const map = mapRef.current
    if (!map) return

    markersRef.current.forEach((marker) => marker.remove())
    markersRef.current = []

    markers.forEach((marker, index) => {
      const element = document.createElement('div')
      element.className =
        'flex h-8 w-8 items-center justify-center rounded-full border-2 border-white shadow-lg bg-orange-500 text-xs font-semibold text-white'
      element.textContent = `${index + 1}`

      const popup = new mapboxgl.Popup({ offset: 16 }).setHTML(
        renderToStaticMarkup(<PlacePopup marker={marker} />)
      )

      const mapMarker = new mapboxgl.Marker({ element })
        .setLngLat([marker.longitude, marker.latitude])
        .setPopup(popup)
        .addTo(map)

      markersRef.current.push(mapMarker)
    })
  }, [markers])

  useEffect(() => {
    const map = mapRef.current
    if (!map) return

    routeClickHandlersRef.current.forEach(({ layerId, handler }) => {
      map.off('click', layerId, handler)
    })
    routeClickHandlersRef.current = []

    routeLayersRef.current.forEach(({ layerId, sourceId }) => {
      if (map.getLayer(layerId)) {
        map.removeLayer(layerId)
      }
      if (map.getSource(sourceId)) {
        map.removeSource(sourceId)
      }
    })
    routeLayersRef.current = []

    routes.forEach((route, index) => {
      const coordinates = decodePolyline(route.polyline)
      if (coordinates.length === 0) {
        const start = markerMap.get(route.from_place_id)
        const end = markerMap.get(route.to_place_id)
        if (start && end) {
          coordinates.push(
            [start.longitude, start.latitude],
            [end.longitude, end.latitude]
          )
        }
      }

      if (coordinates.length < 2) {
        return
      }

      const sourceId = `route-${route.id}-source`
      const layerId = `route-${route.id}`

      map.addSource(sourceId, {
        type: 'geojson',
        data: {
          type: 'Feature',
          properties: {},
          geometry: {
            type: 'LineString',
            coordinates,
          },
        },
      })

      map.addLayer({
        id: layerId,
        type: 'line',
        source: sourceId,
        layout: {
          'line-join': 'round',
          'line-cap': 'round',
        },
        paint: {
          'line-color':
            route.id === activeRouteId ? '#2563eb' : '#60a5fa',
          'line-width': route.id === activeRouteId ? 5 : 3,
          'line-opacity': route.id === activeRouteId ? 0.9 : 0.6,
        },
      })

      if (onRouteSelect) {
        const handler = () => onRouteSelect(route.id)
        map.on('click', layerId, handler)
        routeClickHandlersRef.current.push({ layerId, handler })
      }

      routeLayersRef.current.push({ layerId, sourceId })
    })
  }, [routes, markerMap, onRouteSelect, activeRouteId])

  useEffect(() => {
    const map = mapRef.current
    if (!map) return

    const updatePaint = () => {
      routeLayersRef.current.forEach(({ layerId }) => {
        if (!map.getLayer(layerId)) return
        const isActive = activeRouteId
          ? layerId === `route-${activeRouteId}`
          : false
        map.setPaintProperty(
          layerId,
          'line-color',
          isActive ? '#2563eb' : '#60a5fa'
        )
        map.setPaintProperty(
          layerId,
          'line-width',
          isActive ? 5 : 3
        )
        map.setPaintProperty(
          layerId,
          'line-opacity',
          isActive ? 0.9 : 0.6
        )
      })
    }

    if (map.loaded()) {
      updatePaint()
    } else {
      map.once('load', updatePaint)
    }
  }, [activeRouteId])

  useEffect(() => {
    const map = mapRef.current
    if (!map) return

    const fitToBounds = () => {
      map.fitBounds(
        [
          [bounds.southwest.longitude, bounds.southwest.latitude],
          [bounds.northeast.longitude, bounds.northeast.latitude],
        ],
        { padding: 60, maxZoom: 13 }
      )
    }

    if (map.loaded()) {
      fitToBounds()
    } else {
      map.once('load', fitToBounds)
    }
  }, [bounds])

  return <div ref={containerRef} className="h-full w-full" />
}
