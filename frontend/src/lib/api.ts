import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios'
import { supabase } from './supabase'

/**
 * API 클라이언트 설정
 *
 * 백엔드 FastAPI 서버와 통신하기 위한 Axios 인스턴스
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/**
 * Axios 인스턴스 생성
 */
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30초 타임아웃
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * Request Interceptor
 * - 인증 토큰 자동 추가
 */
apiClient.interceptors.request.use(
  async (config) => {
    // Supabase 세션에서 JWT 토큰 가져오기
    const {
      data: { session },
    } = await supabase.auth.getSession()

    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

/**
 * Response Interceptor
 * - 에러 핸들링
 * - 토큰 갱신 (401 에러 처리)
 */
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & {
      _retry?: boolean
    }

    // 401 에러이고 재시도하지 않았다면
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        // 토큰 갱신 시도
        const {
          data: { session },
          error: _refreshError,
        } = await supabase.auth.refreshSession()

        if (_refreshError || !session) {
          // 토큰 갱신 실패 시 로그아웃
          await supabase.auth.signOut()
          window.location.href = '/login'
          return Promise.reject(error)
        }

        // 새 토큰으로 원래 요청 재시도
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${session.access_token}`
        }

        return apiClient(originalRequest)
      } catch (_refreshError) {
        // 갱신 실패
        await supabase.auth.signOut()
        window.location.href = '/login'
        return Promise.reject(error)
      }
    }

    return Promise.reject(error)
  }
)

/**
 * API 에러 타입
 */
export interface ApiError {
  message: string
  detail?: string
  statusCode?: number
}

/**
 * API 에러 핸들러
 */
export function handleApiError(error: unknown): ApiError {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ detail?: string; message?: string }>

    return {
      message: axiosError.response?.data?.message || error.message,
      detail: axiosError.response?.data?.detail,
      statusCode: axiosError.response?.status,
    }
  }

  return {
    message: error instanceof Error ? error.message : '알 수 없는 에러가 발생했습니다.',
  }
}

/**
 * API 응답 타입 (백엔드와 일치)
 */
export interface ApiResponse<T> {
  data?: T
  message?: string
  error?: string
}
