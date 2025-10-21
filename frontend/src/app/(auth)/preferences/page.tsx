'use client'

import { format } from 'date-fns'

import { PreferencesForm } from '@/components/forms/PreferencesForm'
import { usePreferences } from '@/hooks/usePreferences'

export default function PreferencesPage() {
  const { preferences, isLoading, isSaving, error, savePreferences, fetchPreferences } = usePreferences()

  const handleSubmit = async (payload: Parameters<typeof savePreferences>[0]) => {
    await savePreferences(payload)
  }

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-8 py-12">
      <header className="space-y-2">
        <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">여행 선호도 관리</h1>
            <p className="text-sm text-slate-600">
              TravelTailor가 다음 여행을 설계할 때 기본값으로 사용할 선호도를 설정하세요.
            </p>
          </div>
          {preferences.updated_at ? (
            <p className="text-xs text-slate-500">
              마지막 업데이트: {format(new Date(preferences.updated_at), 'yyyy-MM-dd HH:mm')}
            </p>
          ) : null}
        </div>
      </header>

      {isLoading ? (
        <div className="animate-pulse space-y-4 rounded-xl border border-slate-200 bg-white p-6">
          <div className="h-6 w-48 rounded bg-slate-200" />
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div className="h-24 rounded bg-slate-200" />
            <div className="h-24 rounded bg-slate-200" />
          </div>
          <div className="h-36 rounded bg-slate-200" />
        </div>
      ) : (
        <PreferencesForm
          initialValues={preferences}
          onSubmit={handleSubmit}
          isSubmitting={isSaving}
          errorMessage={error}
        />
      )}

      {!isLoading && (
        <div className="flex justify-end">
          <button
            type="button"
            onClick={() => fetchPreferences()}
            className="text-sm text-slate-500 underline-offset-4 hover:underline"
          >
            최신 정보로 새로고침
          </button>
        </div>
      )}
    </div>
  )
}
