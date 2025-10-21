'use client'

import type { BudgetBreakdown } from '@shared-types/travel-plan'

interface BudgetSummaryProps {
  total: number
  breakdown?: BudgetBreakdown
  perDay?: number
}

const LABELS: Record<keyof BudgetBreakdown, string> = {
  accommodation: '숙박',
  food: '식사',
  activities: '체험/관광',
  transport: '교통',
}

export function BudgetSummary({ total, breakdown, perDay }: BudgetSummaryProps) {
  const entries = breakdown
    ? (Object.entries(breakdown) as [keyof BudgetBreakdown, number][])
    : ([] as [keyof BudgetBreakdown, number][])

  return (
    <aside className="rounded-xl border border-indigo-100 bg-indigo-50 p-6 text-sm text-indigo-900">
      <h3 className="text-base font-semibold text-indigo-900">예산 요약</h3>
      <p className="mt-1 text-xs text-indigo-700">총 예산: {total.toLocaleString()}원</p>
      {perDay ? <p className="text-xs text-indigo-700">일일 권장 예산: {perDay.toLocaleString()}원</p> : null}

      {entries.length > 0 ? (
        <ul className="mt-4 space-y-2">
          {entries.map(([key, value]) => (
            <li key={key} className="flex items-center justify-between rounded-md bg-white px-3 py-2 shadow-sm">
              <span className="font-medium text-indigo-800">{LABELS[key]}</span>
              <span>{value.toLocaleString()}원</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-3 text-xs text-indigo-700">세부 배분 정보가 없습니다.</p>
      )}
    </aside>
  )
}

