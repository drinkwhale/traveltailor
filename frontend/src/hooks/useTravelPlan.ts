'use client'

import { useCallback, useEffect, useRef, useState } from 'react'

import {
  createTravelPlan,
  deleteTravelPlan,
  getTravelPlan,
  getTravelPlanStatus,
  listTravelPlans,
  updateTravelPlan,
} from '@/services/travel-plans'
import type {
  TravelPlanCreate,
  TravelPlanDetail,
  TravelPlanStatus,
  TravelPlanSummary,
  TravelPlanUpdate,
} from '@shared-types/travel-plan'
import type { PaginatedResponse } from '@shared-types/common'

interface UseTravelPlanOptions {
  pollInterval?: number
}

interface UseTravelPlanResult {
  plan?: TravelPlanDetail
  status?: TravelPlanStatus
  histories?: PaginatedResponse<TravelPlanSummary>
  warnings: string[]
  isLoading: boolean
  isPolling: boolean
  error?: string
  createPlan: (payload: TravelPlanCreate) => Promise<TravelPlanDetail>
  refreshStatus: (planId: string) => Promise<TravelPlanStatus>
  fetchPlan: (planId: string) => Promise<TravelPlanDetail>
  updatePlan: (planId: string, payload: TravelPlanUpdate) => Promise<TravelPlanDetail>
  deletePlan: (planId: string) => Promise<void>
  loadHistories: (page?: number, pageSize?: number) => Promise<void>
  reset: () => void
}

export function useTravelPlan(options: UseTravelPlanOptions = {}): UseTravelPlanResult {
  const pollInterval = options.pollInterval ?? 4000
  const [plan, setPlan] = useState<TravelPlanDetail | undefined>(undefined)
  const [status, setStatus] = useState<TravelPlanStatus | undefined>(undefined)
  const [histories, setHistories] = useState<PaginatedResponse<TravelPlanSummary> | undefined>(
    undefined
  )
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | undefined>(undefined)
  const [isPolling, setIsPolling] = useState(false)
  const pollingRef = useRef<NodeJS.Timeout | null>(null)

  const clearPolling = () => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current)
      pollingRef.current = null
    }
    setIsPolling(false)
  }

  useEffect(() => {
    return () => clearPolling()
  }, [])

  const refreshStatus = useCallback(
    async (planId: string) => {
      try {
        const nextStatus = await getTravelPlanStatus(planId)
        setStatus(nextStatus)
        if (nextStatus.status === 'completed' || nextStatus.status === 'failed') {
          clearPolling()
        }
        return nextStatus
      } catch (err: any) {
        setError(err?.message ?? '상태를 확인하지 못했습니다.')
        clearPolling()
        throw err
      }
    },
    []
  )

  const startPolling = useCallback(
    (planId: string) => {
      if (pollingRef.current) {
        return
      }
      setIsPolling(true)
      pollingRef.current = setInterval(() => {
        refreshStatus(planId).catch(() => undefined)
      }, pollInterval)
    },
    [pollInterval, refreshStatus]
  )

  const fetchPlan = useCallback(async (planId: string) => {
    try {
      setIsLoading(true)
      const detail = await getTravelPlan(planId)
      setPlan(detail)
      if (detail.status !== 'completed') {
        startPolling(detail.id)
      } else {
        clearPolling()
      }
      return detail
    } catch (err: any) {
      setError(err?.message ?? '여행 일정을 불러오지 못했습니다.')
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [startPolling])

  const createPlan = useCallback(
    async (payload: TravelPlanCreate) => {
      try {
        setIsLoading(true)
        setError(undefined)
        const detail = await createTravelPlan(payload)
        setPlan(detail)
        setStatus({ id: detail.id, status: detail.status, progress: detail.status === 'completed' ? 1 : 0.5 })
        if (detail.status !== 'completed') {
          startPolling(detail.id)
        }
        return detail
      } catch (err: any) {
        const message = err?.message ?? '여행 계획 생성에 실패했습니다.'
        setError(message)
        throw err
      } finally {
        setIsLoading(false)
      }
    },
    [startPolling]
  )

  const updatePlan = useCallback(async (planId: string, payload: TravelPlanUpdate) => {
    try {
      setIsLoading(true)
      const updated = await updateTravelPlan(planId, payload)
      setPlan(updated)
      return updated
    } catch (err: any) {
      setError(err?.message ?? '여행 계획 업데이트에 실패했습니다.')
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const deletePlanHandler = useCallback(async (planId: string) => {
    try {
      setIsLoading(true)
      await deleteTravelPlan(planId)
      setPlan(undefined)
      setStatus(undefined)
      clearPolling()
    } catch (err: any) {
      setError(err?.message ?? '여행 계획 삭제에 실패했습니다.')
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const loadHistories = useCallback(async (page = 1, pageSize = 10) => {
    try {
      setIsLoading(true)
      const result = await listTravelPlans(page, pageSize)
      setHistories(result)
    } catch (err: any) {
      setError(err?.message ?? '여행 계획 목록을 불러오지 못했습니다.')
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const reset = useCallback(() => {
    setPlan(undefined)
    setStatus(undefined)
    setHistories(undefined)
    setError(undefined)
    clearPolling()
  }, [])

  const warnings = (() => {
    const pref = plan?.preferences as { warnings?: unknown } | undefined
    if (pref?.warnings && Array.isArray(pref.warnings)) {
      return (pref.warnings as unknown[]).filter((item): item is string => typeof item === 'string')
    }
    return []
  })()

  return {
    plan,
    status,
    histories,
    warnings,
    isLoading,
    isPolling,
    error,
    createPlan,
    refreshStatus,
    fetchPlan,
    updatePlan,
    deletePlan: deletePlanHandler,
    loadHistories,
    reset,
  }
}
