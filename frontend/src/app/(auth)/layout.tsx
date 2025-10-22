import Link from 'next/link'
import { ReactNode } from 'react'

/**
 * 인증된 사용자 전용 레이아웃
 * 로그인이 필요한 페이지들을 위한 레이아웃
 */
export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더/네비게이션 바 */}
      <header className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">
              AI TravelTailor
            </h1>
            <nav className="flex gap-4 text-sm text-slate-600">
              <Link href="/create" className="hover:text-indigo-600">
                일정 생성
              </Link>
              <Link href="/history" className="hover:text-indigo-600">
                여행 히스토리
              </Link>
              <Link href="/preferences" className="hover:text-indigo-600">
                선호도 설정
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* 메인 콘텐츠 */}
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  )
}
