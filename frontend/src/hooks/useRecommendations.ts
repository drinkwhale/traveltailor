'use client'

import { useCallback, useEffect, useState } from 'react'

import {
  getAccommodationRecommendations,
  getFlightRecommendations,
} from '@/services/recommendations'
import type {
  AccommodationRecommendations,
  FlightRecommendations,
} from '@shared-types/recommendations'

interface UseRecommendationsResult {
  flights?: FlightRecommendations
  accommodations?: AccommodationRecommendations
  isLoading: boolean
  error?: string
  hasFetched: boolean
  refresh: () => Promise<void>
}

export function useRecommendations(planId?: string): UseRecommendationsResult {
  const [flights, setFlights] = useState<FlightRecommendations | undefined>(undefined)
  const [accommodations, setAccommodations] = useState<AccommodationRecommendations | undefined>(
    undefined
  )
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | undefined>(undefined)
  const [hasFetched, setHasFetched] = useState(false)

  const fetchRecommendations = useCallback(async () => {
    if (!planId) {
      return
    }
    setIsLoading(true)
    setError(undefined)

    const parseError = (reason: unknown): string => {
      if (!reason) {
        return '추천 정보를 불러오지 못했습니다.'
      }
      if (reason instanceof Error) {
        return reason.message
      }
      if (typeof reason === 'object' && 'message' in reason) {
        const message = (reason as { message?: unknown }).message
        if (typeof message === 'string') {
          return message
        }
      }
      return '추천 정보를 불러오지 못했습니다.'
    }

    try {
      const [flightResult, accommodationResult] = await Promise.allSettled([
        getFlightRecommendations(planId),
        getAccommodationRecommendations(planId),
      ])

      if (flightResult.status === 'fulfilled') {
        setFlights(flightResult.value)
      } else {
        setFlights(undefined)
        setError(parseError(flightResult.reason))
      }

      if (accommodationResult.status === 'fulfilled') {
        setAccommodations(accommodationResult.value)
      } else {
        setAccommodations(undefined)
        setError((prev) => prev ?? parseError(accommodationResult.reason))
      }
    } finally {
      setIsLoading(false)
      setHasFetched(true)
    }
  }, [planId])

  useEffect(() => {
    if (!planId) {
      setFlights(undefined)
      setAccommodations(undefined)
      setError(undefined)
      setHasFetched(false)
      return
    }
    void fetchRecommendations()
  }, [fetchRecommendations])

  return {
    flights,
    accommodations,
    isLoading,
    error,
    hasFetched,
    refresh: fetchRecommendations,
  }
}
