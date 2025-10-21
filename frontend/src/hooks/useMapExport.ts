'use client'

import { useCallback, useEffect, useState } from 'react'

import { getMapExport } from '@/services/exports'
import type { MapDay, MapExportResponse } from '@shared-types/map'

interface UseMapExportResult {
  data?: MapExportResponse
  days: MapDay[]
  isLoading: boolean
  error?: string
  refresh: () => Promise<void>
}

export function useMapExport(planId?: string): UseMapExportResult {
  const [data, setData] = useState<MapExportResponse | undefined>(undefined)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | undefined>(undefined)

  const fetchData = useCallback(async () => {
    if (!planId) return
    try {
      setIsLoading(true)
      setError(undefined)
      const response = await getMapExport(planId)
      setData(response)
    } catch (err: any) {
      setError(err?.message ?? '지도 정보를 불러오는 데 실패했습니다.')
    } finally {
      setIsLoading(false)
    }
  }, [planId])

  useEffect(() => {
    void fetchData()
  }, [fetchData])

  return {
    data,
    days: data?.days ?? [],
    isLoading,
    error,
    refresh: fetchData,
  }
}
