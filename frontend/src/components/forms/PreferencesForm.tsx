'use client'

import { useEffect, useMemo, useState } from 'react'

import type {
  UserPreferenceResponse,
  UserPreferenceUpdatePayload,
} from '@shared-types/preferences'
import type { TravelerType } from '@shared-types/enums'

interface PreferencesFormProps {
  initialValues: UserPreferenceResponse
  onSubmit: (payload: UserPreferenceUpdatePayload) => Promise<void>
  isSubmitting?: boolean
  errorMessage?: string
}

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

const DEFAULT_FORM: UserPreferenceUpdatePayload = {
  default_budget_min: null,
  default_budget_max: null,
  preferred_traveler_types: [],
  preferred_interests: [],
  avoided_activities: [],
  dietary_restrictions: [],
  preferred_accommodation_type: [],
  mobility_considerations: null,
}

function normalizeInitial(values: UserPreferenceResponse): UserPreferenceUpdatePayload {
  return {
    default_budget_min: values.default_budget_min ?? null,
    default_budget_max: values.default_budget_max ?? null,
    preferred_traveler_types: [...(values.preferred_traveler_types ?? [])],
    preferred_interests: [...(values.preferred_interests ?? [])],
    avoided_activities: [...(values.avoided_activities ?? [])],
    dietary_restrictions: [...(values.dietary_restrictions ?? [])],
    preferred_accommodation_type: [...(values.preferred_accommodation_type ?? [])],
    mobility_considerations: values.mobility_considerations ?? null,
  }
}

export function PreferencesForm({ initialValues, onSubmit, isSubmitting, errorMessage }: PreferencesFormProps) {
  const [formState, setFormState] = useState<UserPreferenceUpdatePayload>(normalizeInitial(initialValues))
  const [localError, setLocalError] = useState<string | null>(null)

  useEffect(() => {
    setFormState(normalizeInitial(initialValues))
  }, [initialValues])

  const travelerTypeSet = useMemo(() => new Set(formState.preferred_traveler_types), [formState])
  const interestSet = useMemo(() => new Set(formState.preferred_interests), [formState])

  const handleToggleTravelerType = (value: TravelerType) => {
    setFormState((prev) => {
      const next = new Set(prev.preferred_traveler_types)
      if (next.has(value)) {
        next.delete(value)
      } else {
        next.add(value)
      }
      return { ...prev, preferred_traveler_types: Array.from(next) }
    })
  }

  const handleToggleInterest = (value: string) => {
    setFormState((prev) => {
      const next = new Set(prev.preferred_interests)
      if (next.has(value)) {
        next.delete(value)
      } else {
        next.add(value)
      }
      return { ...prev, preferred_interests: Array.from(next) }
    })
  }

  const handleCommaSeparatedChange = (field: keyof UserPreferenceUpdatePayload, value: string) => {
    const items = value
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean)
    setFormState((prev) => ({
      ...prev,
      [field]: items,
    }))
  }

  const handleNumberChange = (field: keyof UserPreferenceUpdatePayload, value: string) => {
    const parsed = value === '' ? null : Number(value)
    if (Number.isNaN(parsed as number)) {
      return
    }
    setFormState((prev) => ({ ...prev, [field]: parsed }))
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (isSubmitting) return

    if (
      formState.default_budget_min !== null &&
      formState.default_budget_max !== null &&
      formState.default_budget_min > formState.default_budget_max
    ) {
      setLocalError('최소 예산이 최대 예산보다 클 수 없습니다.')
      return
    }

    setLocalError(null)
    try {
      const payload: UserPreferenceUpdatePayload = {
        ...DEFAULT_FORM,
        ...formState,
        preferred_traveler_types: [...formState.preferred_traveler_types],
        preferred_interests: [...formState.preferred_interests],
        avoided_activities: [...formState.avoided_activities],
        dietary_restrictions: [...formState.dietary_restrictions],
        preferred_accommodation_type: [...formState.preferred_accommodation_type],
        mobility_considerations: formState.mobility_considerations ?? null,
      }
      await onSubmit(payload)
    } catch (error) {
      setLocalError((error as Error).message)
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-8 rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
    >
      <div>
        <h2 className="text-xl font-semibold text-slate-900">선호도 기본값 설정</h2>
        <p className="mt-1 text-sm text-slate-600">
          TravelTailor가 다음 여행 계획을 생성할 때 참고할 기본 선호도를 관리합니다.
        </p>
      </div>

      <section className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <label className="flex flex-col gap-2">
          <span className="text-sm font-medium text-slate-700">최소 예산 (KRW)</span>
          <input
            type="number"
            min={0}
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
            value={formState.default_budget_min ?? ''}
            onChange={(event) => handleNumberChange('default_budget_min', event.target.value)}
            placeholder="예: 500000"
          />
        </label>

        <label className="flex flex-col gap-2">
          <span className="text-sm font-medium text-slate-700">최대 예산 (KRW)</span>
          <input
            type="number"
            min={0}
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
            value={formState.default_budget_max ?? ''}
            onChange={(event) => handleNumberChange('default_budget_max', event.target.value)}
            placeholder="예: 1500000"
          />
        </label>
      </section>

      <section className="space-y-4">
        <h3 className="text-lg font-semibold text-slate-900">동행자 유형</h3>
        <div className="flex flex-wrap gap-2">
          {travelerTypeOptions.map((option) => {
            const selected = travelerTypeSet.has(option.value)
            return (
              <button
                key={option.value}
                type="button"
                className={`rounded-full border px-3 py-1 text-sm transition ${
                  selected
                    ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                    : 'border-slate-300 text-slate-600 hover:border-indigo-400 hover:text-indigo-600'
                }`}
                onClick={() => handleToggleTravelerType(option.value)}
              >
                {option.label}
              </button>
            )
          })}
        </div>
      </section>

      <section className="space-y-4">
        <h3 className="text-lg font-semibold text-slate-900">관심사</h3>
        <div className="flex flex-wrap gap-2">
          {interestOptions.map((interest) => {
            const selected = interestSet.has(interest.value)
            return (
              <button
                key={interest.value}
                type="button"
                className={`rounded-full border px-3 py-1 text-sm transition ${
                  selected
                    ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                    : 'border-slate-300 text-slate-600 hover:border-indigo-400 hover:text-indigo-600'
                }`}
                onClick={() => handleToggleInterest(interest.value)}
              >
                #{interest.label}
              </button>
            )
          })}
        </div>
      </section>

      <section className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <label className="flex flex-col gap-2">
          <span className="text-sm font-medium text-slate-700">피하고 싶은 활동</span>
          <textarea
            className="min-h-[100px] rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
            placeholder="예: 장시간 이동, 박물관"
            value={formState.avoided_activities.join(', ')}
            onChange={(event) => handleCommaSeparatedChange('avoided_activities', event.target.value)}
          />
        </label>

        <label className="flex flex-col gap-2">
          <span className="text-sm font-medium text-slate-700">식이 제한 사항</span>
          <textarea
            className="min-h-[100px] rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
            placeholder="예: 채식주의, 글루텐 프리"
            value={formState.dietary_restrictions.join(', ')}
            onChange={(event) => handleCommaSeparatedChange('dietary_restrictions', event.target.value)}
          />
        </label>
      </section>

      <section className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <label className="flex flex-col gap-2">
          <span className="text-sm font-medium text-slate-700">선호 숙박 스타일</span>
          <textarea
            className="min-h-[100px] rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
            placeholder="예: 부티크 호텔, 온천 료칸"
            value={formState.preferred_accommodation_type.join(', ')}
            onChange={(event) =>
              handleCommaSeparatedChange('preferred_accommodation_type', event.target.value)
            }
          />
        </label>

        <label className="flex flex-col gap-2">
          <span className="text-sm font-medium text-slate-700">이동/체력 고려 사항</span>
          <textarea
            className="min-h-[100px] rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
            placeholder="예: 휠체어 접근 가능 장소 선호"
            value={formState.mobility_considerations ?? ''}
            onChange={(event) =>
              setFormState((prev) => ({ ...prev, mobility_considerations: event.target.value || null }))
            }
          />
        </label>
      </section>

      {(initialValues.preferred_pace || initialValues.recent_notes) && (
        <section className="rounded-lg border border-indigo-100 bg-indigo-50 p-4 text-sm text-indigo-900">
          <p className="font-medium">최근 여행 기록에서 감지한 정보</p>
          <ul className="mt-2 space-y-1">
            {initialValues.preferred_pace ? <li>선호 이동 속도: {initialValues.preferred_pace}</li> : null}
            {initialValues.recent_notes ? <li>메모: {initialValues.recent_notes}</li> : null}
            {initialValues.last_budget_total ? (
              <li>마지막 여행 예산: {initialValues.last_budget_total.toLocaleString()} KRW</li>
            ) : null}
          </ul>
        </section>
      )}

      {(localError || errorMessage) && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {localError || errorMessage}
        </div>
      )}

      <div className="flex justify-end gap-3">
        <button
          type="button"
          className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          onClick={() => {
            setFormState(normalizeInitial(initialValues))
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
          {isSubmitting ? '저장 중...' : '선호도 저장'}
        </button>
      </div>
    </form>
  )
}
