'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import posthog from 'posthog-js'
import {
  signUp,
  signIn,
  signOut,
  getCurrentUser,
  onAuthStateChange,
  type SignUpData,
  type SignInData,
  type AuthUser,
} from '@/lib/auth'

/**
 * 인증 훅
 *
 * 사용자 인증 상태 관리 및 인증 관련 함수 제공
 */
export function useAuth() {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    // 초기 사용자 로드
    getCurrentUser().then((currentUser) => {
      setUser(currentUser)
      if (currentUser) {
        posthog.identify(currentUser.id, { email: currentUser.email })
      }
      setLoading(false)
    })

    // 인증 상태 변경 리스너
    const unsubscribe = onAuthStateChange((currentUser) => {
      setUser(currentUser)
      if (currentUser) {
        posthog.identify(currentUser.id, { email: currentUser.email })
      } else {
        posthog.reset()
      }
      setLoading(false)
    })

    return unsubscribe
  }, [])

  /**
   * 회원가입 핸들러
   */
  const handleSignUp = async (data: SignUpData) => {
    try {
      setLoading(true)
      const { user: newUser, error } = await signUp(data)

      if (error) {
        throw error
      }

      if (newUser) {
        setUser(newUser)
        posthog.identify(newUser.id, { email: newUser.email })
        router.push('/') // 홈으로 이동
      }

      return { user: newUser, error: null }
    } catch (error: any) {
      return { user: null, error }
    } finally {
      setLoading(false)
    }
  }

  /**
   * 로그인 핸들러
   */
  const handleSignIn = async (data: SignInData) => {
    try {
      setLoading(true)
      const { user: signedInUser, error } = await signIn(data)

      if (error) {
        throw error
      }

      if (signedInUser) {
        setUser(signedInUser)
        posthog.identify(signedInUser.id, { email: signedInUser.email })
        router.push('/') // 홈으로 이동
      }

      return { user: signedInUser, error: null }
    } catch (error: any) {
      return { user: null, error }
    } finally {
      setLoading(false)
    }
  }

  /**
   * 로그아웃 핸들러
   */
  const handleSignOut = async () => {
    try {
      setLoading(true)
      const { error } = await signOut()

      if (error) {
        throw error
      }

      setUser(null)
      posthog.reset()
      router.push('/login')

      return { error: null }
    } catch (error: any) {
      return { error }
    } finally {
      setLoading(false)
    }
  }

  return {
    user,
    loading,
    isAuthenticated: !!user,
    signUp: handleSignUp,
    signIn: handleSignIn,
    signOut: handleSignOut,
  }
}
