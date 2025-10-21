'use client'

import { useCallback, useEffect, useMemo, useState } from 'react'

import { FiltersBar, type HistoryFilters } from '@/components/history/FiltersBar'
import { TravelPlanCard } from '@/components/history/TravelPlanCard'
import { listTravelPlans } from '@/services/travel-plans'
import type { ApiError } from '@/lib/api'
import type { TravelPlanSummary } from '@shared-types/travel-plan'

const PAGE_SIZE = 10

export default function HistoryPage() {
  const [plans, setPlans] = useState<TravelPlanSummary[]>([])
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [isLoadingMore, setIsLoadingMore] = useState(false)
  const [error, setError] = useState<string | undefined>(undefined)
  const [filters, setFilters] = useState<HistoryFilters>({
    query: '',
    status: 'all',
    year: 'all',
    sort: 'created_desc',
  })

  const fetchPlans = useCallback(
    async (targetPage: number, { append }: { append: boolean }) => {
      if (append) {
        setIsLoadingMore(true)
      } else {
        setIsLoading(true)
      }
      setError(undefined)

      try {
        const response = await listTravelPlans(targetPage, PAGE_SIZE)
        setPage(targetPage)
        setTotal(response.total)

        setPlans((prev) => {
          if (append) {
            const merged = new Map(prev.map((plan) => [plan.id, plan] as const))
            response.items.forEach((plan) => {
              merged.set(plan.id, plan)
            })
            return Array.from(merged.values())
          }
          return response.items
        })
      } catch (err) {
        const apiError = err as ApiError
        setError(apiError.message)
      } finally {
        if (append) {
          setIsLoadingMore(false)
        }
        setIsLoading(false)
      }
    },
    []
  )

  useEffect(() => {
    void fetchPlans(1, { append: false })
  }, [fetchPlans])

  const availableYears = useMemo(() => {
    const years = new Set<number>()
    plans.forEach((plan) => {
      const year = new Date(plan.start_date).getFullYear()
      if (!Number.isNaN(year)) {
        years.add(year)
      }
    })
    return Array.from(years).sort((a, b) => b - a)
  }, [plans])

  const filteredPlans = useMemo(() => {
    const query = filters.query.trim().toLowerCase()

    const matches = plans.filter((plan) => {
      const matchesQuery =
        query.length === 0 ||
        plan.title.toLowerCase().includes(query) ||
        plan.destination.toLowerCase().includes(query)

      const matchesStatus = filters.status === 'all' || plan.status === filters.status

      const matchesYear =
        filters.year === 'all' || new Date(plan.start_date).getFullYear() === filters.year

      return matchesQuery && matchesStatus && matchesYear
    })

    const sorted = [...matches]
    sorted.sort((a, b) => {
      const startA = new Date(a.start_date).getTime()
      const startB = new Date(b.start_date).getTime()
      const createdA = new Date(a.created_at).getTime()
      const createdB = new Date(b.created_at).getTime()

      switch (filters.sort) {
        case 'created_asc':
          return createdA - createdB
        case 'start_desc':
          return startB - startA
        case 'start_asc':
          return startA - startB
        case 'created_desc':
        default:
          return createdB - createdA
      }
    })

    return sorted
  }, [plans, filters])

  const hasMore = plans.length < total

  const handleLoadMore = () => {
    if (isLoadingMore || !hasMore) return
    void fetchPlans(page + 1, { append: true })
  }

  const handleFiltersChange = (next: HistoryFilters) => {
    setFilters(next)
  }

  const handleReset = () => {
    setFilters({ query: '', status: 'all', year: 'all', sort: 'created_desc' })
  }

  const handleRetry = () => {
    void fetchPlans(1, { append: false })
  }

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-8 py-12">
      <header className="space-y-2">
        <h1 className="text-3xl font-bold text-slate-900">여행 히스토리</h1>
        <p className="text-sm text-slate-600">
          그동안 생성한 여행 일정을 확인하고, 필요한 정보를 다시 다운로드하세요.
        </p>
      </header>

      <FiltersBar
        filters={filters}
        onFiltersChange={handleFiltersChange}
        onReset={handleReset}
        availableYears={availableYears}
        isLoading={isLoading && plans.length === 0}
      />

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
          <button
            type="button"
            className="ml-3 text-xs underline underline-offset-2"
            onClick={handleRetry}
          >
            다시 시도
          </button>
        </div>
      )}

      {isLoading && plans.length === 0 ? (
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, index) => (
            <div key={index} className="h-40 animate-pulse rounded-2xl border border-slate-200 bg-white" />
          ))}
        </div>
      ) : null}

      {!isLoading && filteredPlans.length === 0 ? (
        <div className="rounded-xl border border-slate-200 bg-white p-10 text-center text-sm text-slate-500">
          조건에 맞는 여행 히스토리가 없습니다.
        </div>
      ) : null}

      <div className="space-y-4">
        {filteredPlans.map((plan) => (
          <TravelPlanCard key={plan.id} plan={plan} />
        ))}
      </div>

      {hasMore && (
        <div className="flex justify-center">
          <button
            type="button"
            disabled={isLoadingMore}
            onClick={handleLoadMore}
            className="rounded-lg border border-slate-300 px-6 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isLoadingMore ? '불러오는 중...' : '더 보기'}
          </button>
        </div>
      )}
    </div>
  )
}
