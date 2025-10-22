'use client'

import type { ChangeEvent } from 'react'

import type { PlanStatus } from '@shared-types/enums'

export interface HistoryFilters {
  query: string
  status: PlanStatus | 'all'
  year: number | 'all'
  sort: 'created_desc' | 'created_asc' | 'start_desc' | 'start_asc'
}

interface FiltersBarProps {
  filters: HistoryFilters
  onFiltersChange: (filters: HistoryFilters) => void
  onReset: () => void
  availableYears: number[]
  isLoading?: boolean
}

const statusLabels: Record<PlanStatus, string> = {
  draft: '초안',
  in_progress: '진행 중',
  completed: '완료',
  failed: '실패',
  archived: '보관됨',
}

const sortOptions: { label: string; value: HistoryFilters['sort'] }[] = [
  { label: '최근 생성 순', value: 'created_desc' },
  { label: '오래된 생성 순', value: 'created_asc' },
  { label: '여행 시작일 최신 순', value: 'start_desc' },
  { label: '여행 시작일 오래된 순', value: 'start_asc' },
]

export function FiltersBar({ filters, onFiltersChange, onReset, availableYears, isLoading }: FiltersBarProps) {
  const handleQueryChange = (event: ChangeEvent<HTMLInputElement>) => {
    onFiltersChange({ ...filters, query: event.target.value })
  }

  const handleStatusChange = (event: ChangeEvent<HTMLSelectElement>) => {
    const value = event.target.value as PlanStatus | 'all'
    onFiltersChange({ ...filters, status: value })
  }

  const handleYearChange = (event: ChangeEvent<HTMLSelectElement>) => {
    const value = event.target.value
    onFiltersChange({ ...filters, year: value === 'all' ? 'all' : Number(value) })
  }

  const handleSortChange = (event: ChangeEvent<HTMLSelectElement>) => {
    const value = event.target.value as HistoryFilters['sort']
    onFiltersChange({ ...filters, sort: value })
  }

  return (
    <section className="flex flex-col gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm lg:flex-row lg:items-end lg:justify-between">
      <div className="flex flex-1 flex-col gap-2">
        <label className="text-xs font-medium text-slate-600" htmlFor="history-query">
          목적지 또는 제목 검색
        </label>
        <input
          id="history-query"
          type="search"
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
          placeholder="예: 도쿄, 가족"
          value={filters.query}
          onChange={handleQueryChange}
          disabled={isLoading}
        />
      </div>

      <div className="grid flex-1 grid-cols-2 gap-3 lg:flex lg:flex-none">
        <label className="flex flex-col gap-2 text-xs font-medium text-slate-600">
          상태
          <select
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
            value={filters.status}
            onChange={handleStatusChange}
            disabled={isLoading}
          >
            <option value="all">전체</option>
            {Object.entries(statusLabels).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>

        <label className="flex flex-col gap-2 text-xs font-medium text-slate-600">
          연도
          <select
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
            value={filters.year}
            onChange={handleYearChange}
            disabled={isLoading}
          >
            <option value="all">전체</option>
            {availableYears.map((year) => (
              <option key={year} value={year}>
                {year}년
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="flex flex-col gap-2 lg:w-56">
        <label className="text-xs font-medium text-slate-600" htmlFor="history-sort">
          정렬
        </label>
        <select
          id="history-sort"
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
          value={filters.sort}
          onChange={handleSortChange}
          disabled={isLoading}
        >
          {sortOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <button
          type="button"
          onClick={onReset}
          className="text-left text-xs text-slate-500 underline-offset-4 hover:underline disabled:cursor-not-allowed disabled:opacity-60"
          disabled={isLoading}
        >
          필터 초기화
        </button>
      </div>
    </section>
  )
}
