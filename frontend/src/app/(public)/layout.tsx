import { ReactNode } from 'react'

/**
 * 공개 페이지 레이아웃
 * 로그인, 회원가입 등 인증이 필요 없는 페이지들을 위한 레이아웃
 */
export default function PublicLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {children}
    </div>
  )
}
