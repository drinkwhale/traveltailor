'use client'

import { useCallback } from 'react'

import { cn } from '@/lib/utils'
import { usePdfExport } from '@/hooks/usePdfExport'
import type { PdfExportPayload } from '@shared-types/pdf'

interface PdfDownloadButtonProps {
  planId: string
  planTitle?: string
  className?: string
  onGenerated?: (payload: PdfExportPayload) => void
  onError?: (message: string) => void
  onGeneratingChange?: (isGenerating: boolean) => void
}

export function PdfDownloadButton({
  planId,
  planTitle,
  className,
  onGenerated,
  onError,
  onGeneratingChange,
}: PdfDownloadButtonProps) {
  const { exportData, isGenerating, error, generate } = usePdfExport({ planId })

  const handleClick = useCallback(async () => {
    onGeneratingChange?.(true)
    try {
      const result = await generate()
      if (typeof window !== 'undefined') {
        window.open(result.download_url, '_blank', 'noopener,noreferrer')
      }
      onGenerated?.(result)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'PDF 생성에 실패했습니다.'
      onError?.(message)
    } finally {
      onGeneratingChange?.(false)
    }
  }, [generate, onGenerated, onError, onGeneratingChange])

  return (
    <div className={cn('flex flex-col gap-2', className)}>
      <button
        type="button"
        disabled={isGenerating}
        onClick={handleClick}
        className={cn(
          'inline-flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500 disabled:cursor-not-allowed disabled:bg-blue-200',
        )}
      >
        {isGenerating ? (
          <svg
            className="h-4 w-4 animate-spin text-white"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            role="img"
            aria-hidden
          >
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
            />
          </svg>
        ) : (
          <span role="img" aria-hidden>
            📄
          </span>
        )}
        {isGenerating ? 'PDF 생성 중...' : 'PDF 다운로드'}
      </button>

      {planTitle && !isGenerating && !exportData && !error && (
        <p className="text-xs text-slate-500">
          현재 일정(<span className="font-semibold">{planTitle}</span>)을 PDF로 저장할 수 있습니다.
        </p>
      )}

      {exportData && (
        <p className="text-xs text-slate-500">
          최근 생성된 파일: <span className="font-semibold">{exportData.file_name}</span>
          {exportData.expires_at ? ` · 유효기간 ${new Date(exportData.expires_at).toLocaleString('ko-KR')}` : ''}
        </p>
      )}

      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  )
}
