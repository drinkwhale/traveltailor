import { createClient } from '@supabase/supabase-js'

/**
 * Supabase 클라이언트 싱글톤
 *
 * 환경 변수:
 * - NEXT_PUBLIC_SUPABASE_URL: Supabase 프로젝트 URL
 * - NEXT_PUBLIC_SUPABASE_ANON_KEY: Supabase anon/public key
 */

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error(
    'Supabase 환경 변수가 설정되지 않았습니다. ' +
    'NEXT_PUBLIC_SUPABASE_URL과 NEXT_PUBLIC_SUPABASE_ANON_KEY를 확인하세요.'
  )
}

/**
 * Supabase 클라이언트 인스턴스
 * - 인증 관리
 * - 데이터베이스 쿼리
 * - 실시간 구독
 */
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
  },
})

/**
 * Supabase 타입 정의 (추후 자동 생성)
 *
 * 사용 예시:
 * ```typescript
 * import { Database } from '@/lib/supabase'
 *
 * type User = Database['public']['Tables']['users']['Row']
 * ```
 */
export type Database = {
  public: {
    Tables: {
      users: {
        Row: {
          id: string
          email: string
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          email: string
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          email?: string
          created_at?: string
          updated_at?: string
        }
      }
      // 추가 테이블 타입은 추후 정의
    }
  }
}
