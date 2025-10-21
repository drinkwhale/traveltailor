'use client'

import Link from 'next/link'

import { TravelPlanForm } from '@/components/forms/TravelPlanForm'
import { DailyTimeline } from '@/components/timeline/DailyTimeline'
import { ProgressIndicator } from '@/components/ui/ProgressIndicator'
import { BudgetSummary } from '@/components/budget/BudgetSummary'
import { useTravelPlan } from '@/hooks/useTravelPlan'

export default function CreatePlanPage() {
  const { plan, status, warnings, isLoading, error, createPlan, reset } = useTravelPlan()

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-10 py-12">
      <header className="space-y-2">
        <h1 className="text-3xl font-bold text-slate-900">AI 여행 일정 생성</h1>
        <p className="text-sm text-slate-600">
          여행 정보를 입력하면 TravelTailor가 숙소, 맛집, 관광지, 동선까지 포함한 맞춤 일정을 만들어드립니다.
        </p>
      </header>

      <TravelPlanForm
        onSubmit={createPlan}
        isSubmitting={isLoading}
        errorMessage={error}
        warnings={warnings}
      />

      {plan ? (
        <section className="space-y-6 rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
          <div className="flex flex-col gap-4 border-b border-slate-100 pb-6 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <h2 className="text-2xl font-semibold text-slate-900">생성된 여행 일정</h2>
              <p className="text-sm text-slate-600">
                {plan.destination}, {plan.country} · {plan.start_date} ~ {plan.end_date}
              </p>
            </div>
            <div className="flex items-center gap-3">
              <ProgressIndicator status={status} isLoading={isLoading} />
              <button
                type="button"
                className="rounded-lg border border-slate-300 px-4 py-2 text-sm text-slate-600 hover:bg-slate-50"
                onClick={reset}
              >
                새로 생성하기
              </button>
              <Link
                href={`/plan/${plan.id}`}
                className="rounded-lg bg-indigo-600 px-5 py-2 text-sm font-semibold text-white hover:bg-indigo-700"
              >
                상세 보기
              </Link>
            </div>
          </div>

          <div className="grid gap-6 lg:grid-cols-[260px,1fr]">
            <BudgetSummary
              total={plan.budget_total}
              breakdown={plan.budget_breakdown}
              perDay={plan.budget_breakdown ? Math.round(plan.budget_total / plan.total_days) : undefined}
            />

            <div className="space-y-6">
              {plan.daily_itineraries.map((itinerary) => (
                <DailyTimeline key={itinerary.id} itinerary={itinerary} />
              ))}
            </div>
          </div>
        </section>
      ) : null}
    </div>
  )
}

