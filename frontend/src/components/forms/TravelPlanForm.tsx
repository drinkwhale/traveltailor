'use client'

import { useMemo, useState } from 'react'

import type { TravelPlanCreate, TravelPlanDetail, TravelerType } from '@shared-types/travel-plan'

const travelerTypeOptions: { label: string; value: TravelerType }[] = [
  { label: '커플', value: 'couple' },
  { label: '가족', value: 'family' },
  { label: '혼자', value: 'solo' },
  { label: '친구와', value: 'friends' },
]

const interestOptions = [
  { label: '맛집', value: 'food' },
  { label: '문화', value: 'culture' },
  { label: '자연', value: 'nature' },
  { label: '쇼핑', value: 'shopping' },
  { label: '야경', value: 'nightlife' },
  { label: '액티비티', value: 'activity' },
]

interface TravelPlanFormProps {
  onSubmit: (payload: TravelPlanCreate) => Promise<TravelPlanDetail>
  isSubmitting?: boolean
  errorMessage?: string
  warnings?: string[]
}

const initialFormState: TravelPlanCreate = {
  title: '',
  destination: '',
  country: 'Japan',
  start_date: '',
  end_date: '',
  budget_total: 800000,
  traveler_type: 'couple',
  traveler_count: 2,
  preferences: {
    interests: ['food', 'culture'],
    must_have: [],
    avoid: [],
    dietary_restrictions: [],
    pace: 'normal',
    notes: '',
  },
}

export function TravelPlanForm({ onSubmit, isSubmitting, errorMessage, warnings = [] }: TravelPlanFormProps) {
  const [formState, setFormState] = useState<TravelPlanCreate>(initialFormState)
  const [localError, setLocalError] = useState<string | null>(null)

  const minEndDate = useMemo(() => {
    if (!formState.start_date) return ''
    const start = new Date(formState.start_date)
    start.setDate(start.getDate() + 1)
    return start.toISOString().split('T')[0]
  }, [formState.start_date])

  const handleChange = (field: keyof TravelPlanCreate, value: any) => {
    setFormState((prev) => ({ ...prev, [field]: value }))
  }

  const handlePreferenceChange = (field: keyof TravelPlanCreate['preferences'], value: any) => {
    setFormState((prev) => ({
      ...prev,
      preferences: {
        ...prev.preferences,
        [field]: value,
      },
    }))
  }

  const handleInterestToggle = (value: string) => {
    const current = new Set(formState.preferences.interests)
    if (current.has(value)) {
      current.delete(value)
    } else {
      current.add(value)
    }
    handlePreferenceChange('interests', Array.from(current))
  }

  const validate = () => {
    if (!formState.destination.trim() || !formState.country.trim()) {
      setLocalError('목적지와 국가를 입력해주세요.')
      return false
    }
    if (!formState.start_date || !formState.end_date) {
      setLocalError('여행 시작일과 종료일을 입력해주세요.')
      return false
    }
    if (new Date(formState.end_date) < new Date(formState.start_date)) {
      setLocalError('종료일은 시작일 이후여야 합니다.')
      return false
    }
    if (formState.budget_total <= 0) {
      setLocalError('총 예산은 0보다 커야 합니다.')
      return false
    }
    setLocalError(null)
    return true
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (isSubmitting) return
    if (!validate()) return

    const payload: TravelPlanCreate = {
      ...formState,
      preferences: {
        ...formState.preferences,
        must_have: formState.preferences.must_have.filter(Boolean),
        avoid: formState.preferences.avoid.filter(Boolean),
        dietary_restrictions: formState.preferences.dietary_restrictions.filter(Boolean),
      },
    }

    try {
      await onSubmit(payload)
    } catch (error: any) {
      setLocalError(error?.message ?? '여행 계획 생성에 실패했습니다.')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-8 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">여행 조건 입력</h2>
        <p className="mt-1 text-sm text-slate-600">목적지와 예산을 입력하면 AI가 맞춤 일정을 제안합니다.</p>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <label className="flex flex-col gap-2">
          <span className="text-sm font-medium text-slate-700">목적지</span>
          <input
            type="text"
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
            placeholder="예: 도쿄"
            value={formState.destination}
            onChange={(e) => handleChange('destination', e.target.value)}
            required
          />
        </label>

        <label className="flex flex-col gap-2">
          <span className="text-sm font-medium text-slate-700">국가</span>
          <input
            type="text"
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
            placeholder="예: Japan"
            value={formState.country}
            onChange={(e) => handleChange('country', e.target.value)}
            required
          />
        </label>

        <label className="flex flex-col gap-2">
          <span className="text-sm font-medium text-slate-700">여행 시작일</span>
          <input
            type="date"
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
            value={formState.start_date}
            onChange={(e) => handleChange('start_date', e.target.value)}
            required
          />
        </label>

        <label className="flex flex-col gap-2">
          <span className="text-sm font-medium text-slate-700">여행 종료일</span>
          <input
            type="date"
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
            value={formState.end_date}
            min={minEndDate}
            onChange={(e) => handleChange('end_date', e.target.value)}
            required
          />
        </label>

        <label className="flex flex-col gap-2">
          <span className="text-sm font-medium text-slate-700">총 예산 (KRW)</span>
          <input
            type="number"
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
            min={100000}
            step={50000}
            value={formState.budget_total}
            onChange={(e) => handleChange('budget_total', Number(e.target.value))}
            required
          />
        </label>

        <div className="grid grid-cols-2 gap-4">
          <label className="flex flex-col gap-2">
            <span className="text-sm font-medium text-slate-700">여행 유형</span>
            <select
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
              value={formState.traveler_type}
              onChange={(e) => handleChange('traveler_type', e.target.value as TravelerType)}
            >
              {travelerTypeOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>

          <label className="flex flex-col gap-2">
            <span className="text-sm font-medium text-slate-700">인원수</span>
            <input
              type="number"
              min={1}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
              value={formState.traveler_count}
              onChange={(e) => handleChange('traveler_count', Number(e.target.value))}
            />
          </label>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-slate-900">관심사 & 선호도</h3>
        <div className="flex flex-wrap gap-2">
          {interestOptions.map((interest) => {
            const selected = formState.preferences.interests.includes(interest.value)
            return (
              <button
                key={interest.value}
                type="button"
                className={`rounded-full border px-3 py-1 text-sm transition ${
                  selected
                    ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                    : 'border-slate-300 text-slate-600 hover:border-indigo-400 hover:text-indigo-600'
                }`}
                onClick={() => handleInterestToggle(interest.value)}
              >
                #{interest.label}
              </button>
            )
          })}
        </div>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <label className="flex flex-col gap-2">
            <span className="text-sm font-medium text-slate-700">꼭 포함하고 싶은 요소</span>
            <textarea
              className="min-h-[80px] rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
              placeholder="예: 디즈니랜드, 스시 오마카세"
              value={formState.preferences.must_have.join(', ')}
              onChange={(e) =>
                handlePreferenceChange(
                  'must_have',
                  e.target.value.split(',').map((item) => item.trim())
                )
              }
            />
          </label>

          <label className="flex flex-col gap-2">
            <span className="text-sm font-medium text-slate-700">피하고 싶은 요소</span>
            <textarea
              className="min-h-[80px] rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
              placeholder="예: 박물관, 장시간 이동"
              value={formState.preferences.avoid.join(', ')}
              onChange={(e) =>
                handlePreferenceChange(
                  'avoid',
                  e.target.value.split(',').map((item) => item.trim())
                )
              }
            />
          </label>
        </div>

        <label className="flex flex-col gap-2">
          <span className="text-sm font-medium text-slate-700">추가 메모</span>
          <textarea
            className="min-h-[80px] rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
            placeholder="특별히 고려해야 할 사항을 작성해주세요."
            value={formState.preferences.notes ?? ''}
            onChange={(e) => handlePreferenceChange('notes', e.target.value)}
          />
        </label>
      </div>

      {(localError || errorMessage) && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {localError || errorMessage}
        </div>
      )}

      {warnings.length > 0 && (
        <div className="space-y-2 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          <p className="font-medium">주의사항</p>
          <ul className="list-disc space-y-1 pl-5">
            {warnings.map((warning) => (
              <li key={warning}>{warning}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="flex justify-end gap-3">
        <button
          type="button"
          className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          onClick={() => {
            setFormState(initialFormState)
            setLocalError(null)
          }}
        >
          초기화
        </button>

        <button
          type="submit"
          disabled={isSubmitting}
          className="rounded-lg bg-indigo-600 px-5 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:bg-indigo-300"
        >
          {isSubmitting ? '생성 중...' : '여행 일정 생성하기'}
        </button>
      </div>
    </form>
  )
}

