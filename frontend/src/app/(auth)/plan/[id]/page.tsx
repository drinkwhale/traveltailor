'use client'

import { useEffect, useMemo, useState } from 'react'
import { useRouter } from 'next/navigation'

import { BudgetSummary } from '@/components/budget/BudgetSummary'
import { DailyTimeline } from '@/components/timeline/DailyTimeline'
import { ProgressIndicator } from '@/components/ui/ProgressIndicator'
import { ExportButtons } from '@/components/map/ExportButtons'
import { RouteMap } from '@/components/map/RouteMap'
import { useMapExport } from '@/hooks/useMapExport'
import { useTravelPlan } from '@/hooks/useTravelPlan'

interface PlanDetailPageProps {
  params: {
    id: string
  }
}

export default function PlanDetailPage({ params }: PlanDetailPageProps) {
  const router = useRouter()
  const { plan, status, warnings, isLoading, error, fetchPlan } = useTravelPlan()
  const { data: mapExport, days: mapDays, isLoading: isMapLoading, error: mapError } = useMapExport(
    plan?.id
  )
  const [selectedDayIndex, setSelectedDayIndex] = useState(0)

  useEffect(() => {
    if (!params.id) {
      router.push('/plan')
      return
    }
    fetchPlan(params.id).catch(() => undefined)
  }, [params.id, fetchPlan, router])

  useEffect(() => {
    if (!mapDays.length) {
      setSelectedDayIndex(0)
      return
    }
    setSelectedDayIndex((prev) => {
      if (prev >= mapDays.length) {
        return mapDays.length - 1
      }
      return prev
    })
  }, [mapDays])

  const selectedDay = useMemo(() => mapDays[selectedDayIndex], [mapDays, selectedDayIndex])

  if (isLoading && !plan) {
    return (
      <div className="mx-auto max-w-4xl space-y-4 py-16">
        <ProgressIndicator isLoading status={status} />
        <p className="text-center text-sm text-slate-600">여행 일정을 불러오는 중입니다...</p>
      </div>
    )
  }

  if (error && !plan) {
    return (
      <div className="mx-auto max-w-4xl py-16">
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      </div>
    )
  }

  if (!plan) {
    return null
  }

  const renderMapSection = () => {
    if (isMapLoading) {
      return (
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm text-slate-600">지도를 불러오는 중입니다...</p>
        </section>
      )
    }

    if (mapError) {
      return (
        <section className="rounded-2xl border border-amber-200 bg-amber-50 p-6 text-sm text-amber-800">
          지도 정보를 가져오지 못했습니다. 잠시 후 다시 시도해주세요.
        </section>
      )
    }

    if (!mapExport || !selectedDay) {
      return null
    }

    return (
      <section className="flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">지도에서 일정 살펴보기</h2>
            <p className="text-sm text-slate-500">
              방문 장소와 이동 경로를 한 눈에 확인하고, 외부 지도 앱으로 내보낼 수 있습니다.
            </p>
          </div>
          <ExportButtons day={selectedDay} />
        </div>

        <div className="flex flex-wrap gap-2">
          {mapDays.map((day, index) => {
            const isActive = index === selectedDayIndex
            return (
              <button
                key={day.day_number}
                type="button"
                onClick={() => setSelectedDayIndex(index)}
                className={`rounded-full px-3 py-1 text-xs font-medium ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'bg-slate-100 text-slate-600 hover:bg-blue-50 hover:text-blue-700'
                }`}
              >
                Day {day.day_number}
              </button>
            )
          })}
        </div>

        <RouteMap bounds={mapExport.bounds} day={selectedDay} />
      </section>
    )
  }

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-8 py-12">
      <section className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">{plan.title}</h1>
            <p className="text-sm text-slate-600">
              {plan.destination}, {plan.country}
            </p>
            <p className="mt-1 text-xs text-slate-500">
              {plan.start_date} ~ {plan.end_date} · {plan.total_days}일({plan.total_nights}박)
            </p>
          </div>
          <div className="w-full max-w-sm">
            <ProgressIndicator status={status} isLoading={isLoading} />
          </div>
        </div>

        {warnings.length > 0 && (
          <div className="mt-4 space-y-1 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
            <p className="font-medium">생성 시 주의사항</p>
            <ul className="list-disc space-y-1 pl-5">
              {warnings.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        )}
      </section>

      {renderMapSection()}

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
    </div>
  )
}
