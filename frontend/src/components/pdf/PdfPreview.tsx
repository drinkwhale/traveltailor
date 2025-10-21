'use client'

import type { PdfExportPayload } from '@shared-types/pdf'

interface PdfPreviewProps {
  exportData?: PdfExportPayload
  isLoading?: boolean
  error?: string
}

export function PdfPreview({ exportData, isLoading, error }: PdfPreviewProps) {
  if (error) {
    return (
      <div className="flex h-48 items-center justify-center rounded-lg border border-red-200 bg-red-50 px-4 text-sm text-red-600">
        {error}
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex h-48 items-center justify-center rounded-lg border border-dashed border-slate-200 bg-slate-50">
        <p className="text-sm text-slate-500">PDF 미리보기를 준비하고 있습니다...</p>
      </div>
    )
  }

  if (!exportData) {
    return (
      <div className="flex h-48 items-center justify-center rounded-lg border border-dashed border-slate-200 bg-slate-50">
        <p className="text-sm text-slate-500">아직 생성된 PDF가 없습니다.</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <div className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-xs text-slate-600">
        <p className="font-medium text-slate-700">{exportData.file_name}</p>
        {exportData.expires_at ? (
          <p>유효기간: {new Date(exportData.expires_at).toLocaleString('ko-KR')}</p>
        ) : (
          <p>유효기간: 만료 없음</p>
        )}
        <a
          href={exportData.download_url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-1 inline-block text-blue-600 hover:text-blue-700"
        >
          새 창에서 열기 ↗
        </a>
      </div>

      <div className="h-[420px] overflow-hidden rounded-xl border border-slate-200 shadow-sm">
        <iframe
          src={exportData.download_url}
          title="PDF preview"
          className="h-full w-full"
        >
          이 브라우저는 PDF 미리보기를 지원하지 않습니다.
        </iframe>
      </div>
    </div>
  )
}
