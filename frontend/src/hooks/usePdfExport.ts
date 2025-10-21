'use client'

import { useCallback, useState } from 'react'

import { requestPdfExport } from '@/services/exports'
import type { PdfExportPayload } from '@shared-types/pdf'

interface UsePdfExportOptions {
  planId?: string
}

interface UsePdfExportResult {
  exportData?: PdfExportPayload
  isGenerating: boolean
  error?: string
  generate: (overridePlanId?: string) => Promise<PdfExportPayload>
  reset: () => void
}

export function usePdfExport(options: UsePdfExportOptions = {}): UsePdfExportResult {
  const { planId } = options
  const [exportData, setExportData] = useState<PdfExportPayload | undefined>(undefined)
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | undefined>(undefined)

  const generate = useCallback(
    async (overridePlanId?: string) => {
      const targetPlanId = overridePlanId ?? planId
      if (!targetPlanId) {
        const message = '여행 계획 ID가 필요합니다.'
        setError(message)
        throw new Error(message)
      }

      try {
        setIsGenerating(true)
        setError(undefined)
        const result = await requestPdfExport(targetPlanId)
        setExportData(result)
        return result
      } catch (err: any) {
        const message = err?.message ?? 'PDF를 생성하지 못했습니다. 잠시 후 다시 시도해주세요.'
        setError(message)
        throw new Error(message)
      } finally {
        setIsGenerating(false)
      }
    },
    [planId]
  )

  const reset = useCallback(() => {
    setExportData(undefined)
    setError(undefined)
  }, [])

  return {
    exportData,
    isGenerating,
    error,
    generate,
    reset,
  }
}
