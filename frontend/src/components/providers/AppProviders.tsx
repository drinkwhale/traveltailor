'use client'

import { useEffect } from 'react'
import * as Sentry from '@sentry/browser'

import { NetworkStatusBanner } from '@/components/NetworkStatusBanner'

interface Props {
  children: React.ReactNode
}

const SENTRY_DSN = process.env.NEXT_PUBLIC_SENTRY_DSN
// PostHog는 현재 Node.js 모듈 충돌로 인해 비활성화됨
// const POSTHOG_KEY = process.env.NEXT_PUBLIC_POSTHOG_KEY
// const POSTHOG_HOST = process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://app.posthog.com'

export function AppProviders({ children }: Props) {
  useEffect(() => {
    // Service Worker 등록
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker
        .register('/sw.js')
        .catch((error) => console.error('Service worker registration failed', error))
    }

    // Sentry 초기화
    if (SENTRY_DSN) {
      Sentry.init({
        dsn: SENTRY_DSN,
        tracesSampleRate: 0.1,
      })
    }

    // TODO: PostHog 재활성화 필요 (현재 Node.js 모듈 충돌로 인해 비활성화)
    // PostHog를 dynamic import로 로드 (Node.js 모듈 오류 방지)
    // if (POSTHOG_KEY && typeof window !== 'undefined') {
    //   import('posthog-js')
    //     .then((posthogModule) => {
    //       const posthog = posthogModule.default
    //       posthog.init(POSTHOG_KEY, {
    //         api_host: POSTHOG_HOST,
    //         capture_pageleave: true,
    //         persistence: 'localStorage+cookie',
    //       })
    //     })
    //     .catch((error) => {
    //       console.error('PostHog initialization failed:', error)
    //     })
    // }

    // PostHog shutdown은 언마운트 시 호출
    // return () => {
    //   if (typeof window !== 'undefined') {
    //     import('posthog-js')
    //       .then((posthogModule) => {
    //         posthogModule.default.shutdown()
    //       })
    //       .catch(() => {
    //         // Ignore shutdown errors
    //       })
    //   }
    // }
  }, [])

  return (
    <>
      {children}
      <NetworkStatusBanner />
    </>
  )
}
