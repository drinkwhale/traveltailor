import type { Metadata } from 'next'
import './globals.css'
import { AppProviders } from '@/components/providers/AppProviders'

export const metadata: Metadata = {
  title: 'AI TravelTailor - 개인 맞춤형 여행 설계',
  description: 'AI가 생성하는 최적화된 여행 일정',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko">
      <body className="antialiased">
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  )
}
