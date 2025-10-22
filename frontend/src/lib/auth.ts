import { apiClient } from './api'
import { storeToken, clearToken, detectStrategy } from './token-storage'

export interface AuthUser {
  id: string
  email: string
  full_name?: string | null
  subscription_tier: string
  created_at: string
}

export interface SignUpData {
  email: string
  password: string
  full_name?: string
}

export interface SignInData {
  email: string
  password: string
}

export interface AuthResponse {
  user: AuthUser | null
  error: Error | null
}

type Listener = (user: AuthUser | null) => void

let currentUser: AuthUser | null = null
const listeners = new Set<Listener>()

function notify(user: AuthUser | null) {
  currentUser = user
  listeners.forEach((listener) => listener(user))
}

async function persistToken(accessToken: string) {
  if (detectStrategy() === 'cookie') {
    return
  }
  await storeToken(accessToken)
}

export async function signUp(payload: SignUpData): Promise<AuthResponse> {
  try {
    const { data } = await apiClient.post<{ access_token: string }>('/v1/auth/signup', payload)
    await persistToken(data.access_token)
    const user = await getCurrentUser()
    notify(user)
    return { user, error: null }
  } catch (error) {
    return { user: null, error: error as Error }
  }
}

export async function signIn(payload: SignInData): Promise<AuthResponse> {
  try {
    const { data } = await apiClient.post<{ access_token: string }>('/v1/auth/login', payload)
    await persistToken(data.access_token)
    const user = await getCurrentUser()
    notify(user)
    return { user, error: null }
  } catch (error) {
    return { user: null, error: error as Error }
  }
}

export async function signOut(): Promise<{ error: Error | null }> {
  try {
    await apiClient.post('/v1/auth/logout')
    await clearToken()
    notify(null)
    return { error: null }
  } catch (error) {
    return { error: error as Error }
  }
}

export async function getCurrentUser(): Promise<AuthUser | null> {
  try {
    const { data } = await apiClient.get<{ data: AuthUser }>('/v1/auth/me')
    const user = data?.data ?? null
    if (user) {
      notify(user)
    }
    return user
  } catch {
    notify(null)
    return null
  }
}

export function onAuthStateChange(listener: Listener) {
  listeners.add(listener)
  listener(currentUser)
  return () => listeners.delete(listener)
}
