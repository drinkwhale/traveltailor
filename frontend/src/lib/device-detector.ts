'use client'

export type DeviceType = 'ios' | 'android' | 'desktop'

function getUserAgent(): string {
  if (typeof window === 'undefined') return ''
  return window.navigator.userAgent || ''
}

export function detectDevice(): DeviceType {
  const ua = getUserAgent().toLowerCase()
  if (/iphone|ipad|ipod/.test(ua)) {
    return 'ios'
  }
  if (/android/.test(ua)) {
    return 'android'
  }
  return 'desktop'
}

export function isMobileDevice(): boolean {
  const type = detectDevice()
  return type === 'ios' || type === 'android'
}
