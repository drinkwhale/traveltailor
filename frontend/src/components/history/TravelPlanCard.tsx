'use client'

import Link from 'next/link'
import { format } from 'date-fns'

import { PdfDownloadButton } from '@/components/exports/PdfDownloadButton'
import type { TravelPlanSummary } from '@shared-types/travel-plan'
import type { PlanStatus } from '@shared-types/enums'

interface TravelPlanCardProps {
  plan: TravelPlanSummary
}

function statusBadge(status: PlanStatus) {
  switch (status) {
    case 'completed':
      return 'bg-emerald-100 text-emerald-700 border-emerald-200'
    case 'in_progress':
      return 'bg-blue-100 text-blue-700 border-blue-200'
    case 'failed':
      return 'bg-red-100 text-red-700 border-red-200'
    case 'archived':
      return 'bg-slate-100 text-slate-600 border-slate-200'
    default:
      return 'bg-amber-100 text-amber-700 border-amber-200'
  }
}

function statusLabel(status: PlanStatus) {
  switch (status) {
    case 'completed':
      return '완료'
    case 'in_progress':
      return '진행 중'
    case 'failed':
      return '실패'
    case 'archived':
      return '보관됨'
    case 'draft':
    default:
      return '초안'
  }
}

export function TravelPlanCard({ plan }: TravelPlanCardProps) {
  const start = new Date(plan.start_date)
  const end = new Date(plan.end_date)
  const createdAt = new Date(plan.created_at)

  return (
    <article className="flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:border-indigo-200 hover:shadow">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h3 className="text-xl font-semibold text-slate-900">{plan.title}</h3>
          <p className="text-sm text-slate-600">
            {plan.destination} · {format(start, 'yyyy.MM.dd')} - {format(end, 'yyyy.MM.dd')} ({plan.total_days}일 {plan.total_nights}박)
          </p>
          <p className="text-xs text-slate-500">생성일 {format(createdAt, 'yyyy.MM.dd HH:mm')}</p>
        </div>
        <div className="flex items-center gap-3">
          <span
            className={`rounded-full border px-3 py-1 text-xs font-semibold ${statusBadge(plan.status)}`}
          >
            {statusLabel(plan.status)}
          </span>
          <span className="rounded-full bg-indigo-50 px-3 py-1 text-xs font-medium text-indigo-600">
            총 예산 {plan.budget_total.toLocaleString()} KRW
          </span>
        </div>
      </div>

      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex flex-wrap gap-2 text-xs text-slate-500">
          <span className="rounded border border-slate-200 px-2 py-1">ID: {plan.id}</span>
          <span className="rounded border border-slate-200 px-2 py-1">
            일정 길이: {plan.total_days}일 / {plan.total_nights}박
          </span>
        </div>
        <div className="flex flex-wrap gap-3">
          <Link
            href={`/plan/${plan.id}`}
            className="inline-flex items-center justify-center rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
          >
            상세 보기
          </Link>
          <PdfDownloadButton planId={plan.id} planTitle={plan.title} />
        </div>
      </div>
    </article>
  )
}
