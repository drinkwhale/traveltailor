/**
 * PostHog 분석 유틸리티
 *
 * PostHog가 초기화되지 않았을 때 API 호출을 안전하게 처리하는 가드 함수 제공
 */

import posthog from 'posthog-js'

/**
 * PostHog가 초기화되었는지 확인
 */
function isPostHogInitialized(): boolean {
  // PostHog 인스턴스가 존재하고 _isInitialized 플래그가 true인지 확인
  return !!(posthog && (posthog as any).__loaded)
}

/**
 * 사용자 식별 (안전 버전)
 *
 * PostHog가 초기화되지 않았으면 조용히 실패
 */
export function identifyUser(userId: string, properties?: Record<string, any>): void {
  if (!isPostHogInitialized()) {
    console.debug('[PostHog] Not initialized - skipping identify')
    return
  }

  try {
    posthog.identify(userId, properties)
  } catch (error) {
    console.warn('[PostHog] Failed to identify user:', error)
  }
}

/**
 * 사용자 세션 리셋 (안전 버전)
 *
 * PostHog가 초기화되지 않았으면 조용히 실패
 */
export function resetUser(): void {
  if (!isPostHogInitialized()) {
    console.debug('[PostHog] Not initialized - skipping reset')
    return
  }

  try {
    posthog.reset()
  } catch (error) {
    console.warn('[PostHog] Failed to reset user:', error)
  }
}

/**
 * 이벤트 캡처 (안전 버전)
 *
 * PostHog가 초기화되지 않았으면 조용히 실패
 */
export function captureEvent(
  eventName: string,
  properties?: Record<string, any>
): void {
  if (!isPostHogInitialized()) {
    console.debug('[PostHog] Not initialized - skipping capture')
    return
  }

  try {
    posthog.capture(eventName, properties)
  } catch (error) {
    console.warn('[PostHog] Failed to capture event:', error)
  }
}

/**
 * 페이지뷰 캡처 (안전 버전)
 *
 * PostHog가 초기화되지 않았으면 조용히 실패
 */
export function capturePageview(): void {
  if (!isPostHogInitialized()) {
    console.debug('[PostHog] Not initialized - skipping pageview')
    return
  }

  try {
    posthog.capture('$pageview')
  } catch (error) {
    console.warn('[PostHog] Failed to capture pageview:', error)
  }
}
