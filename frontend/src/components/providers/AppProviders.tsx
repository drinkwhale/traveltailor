'use client'

import { useEffect } from 'react'
import posthog from 'posthog-js'
import * as Sentry from '@sentry/browser'

import { NetworkStatusBanner } from '@/components/NetworkStatusBanner'

interface Props {
  children: React.ReactNode
}

const SENTRY_DSN = process.env.NEXT_PUBLIC_SENTRY_DSN
const POSTHOG_KEY = process.env.NEXT_PUBLIC_POSTHOG_KEY
const POSTHOG_HOST = process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://app.posthog.com'

export function AppProviders({ children }: Props) {
  useEffect(() => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker
        .register('/sw.js')
        .catch((error) => console.error('Service worker registration failed', error))
    }

    if (SENTRY_DSN) {
      Sentry.init({
        dsn: SENTRY_DSN,
        tracesSampleRate: 0.1,
      })
    }

    if (POSTHOG_KEY) {
      posthog.init(POSTHOG_KEY, {
        api_host: POSTHOG_HOST,
        capture_pageleave: true,
        persistence: 'localStorage+cookie',
      })
    }

    return () => {
      posthog.shutdown()
    }
  }, [])

  return (
    <>
      {children}
      <NetworkStatusBanner />
    </>
  )
}
