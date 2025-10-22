'use client'

import { useCallback, useEffect, useState } from 'react'

import type { ApiError } from '@/lib/api'
import { getUserPreferences, updateUserPreferences } from '@/services/preferences'
import {
  emptyPreferenceResponse,
  type UserPreferenceResponse,
  type UserPreferenceUpdatePayload,
} from '@shared-types/preferences'

interface UsePreferences {
  preferences: UserPreferenceResponse
  isLoading: boolean
  isSaving: boolean
  error?: string
  fetchPreferences: () => Promise<void>
  savePreferences: (payload: UserPreferenceUpdatePayload) => Promise<UserPreferenceResponse>
}

export function usePreferences(): UsePreferences {
  const [preferences, setPreferences] = useState<UserPreferenceResponse>(emptyPreferenceResponse)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [isSaving, setIsSaving] = useState<boolean>(false)
  const [error, setError] = useState<string | undefined>(undefined)

  const fetchPreferences = useCallback(async () => {
    setIsLoading(true)
    setError(undefined)
    try {
      const response = await getUserPreferences()
      setPreferences(response)
    } catch (err) {
      const apiError = err as ApiError
      setError(apiError.message)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const savePreferences = useCallback(
    async (payload: UserPreferenceUpdatePayload) => {
      setIsSaving(true)
      setError(undefined)
      try {
        const response = await updateUserPreferences(payload)
        setPreferences(response)
        return response
      } catch (err) {
        const apiError = err as ApiError
        setError(apiError.message)
        throw apiError
      } finally {
        setIsSaving(false)
      }
    },
  []
  )

  useEffect(() => {
    void fetchPreferences()
  }, [fetchPreferences])

  return {
    preferences,
    isLoading,
    isSaving,
    error,
    fetchPreferences,
    savePreferences,
  }
}
