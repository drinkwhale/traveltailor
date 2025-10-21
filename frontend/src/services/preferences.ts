import { apiClient, ApiResponse, handleApiError } from '@/lib/api'
import type {
  UserPreferenceResponse,
  UserPreferenceUpdatePayload,
} from '@shared-types/preferences'

const BASE_PATH = '/v1/preferences'

export async function getUserPreferences(): Promise<UserPreferenceResponse> {
  try {
    const { data } = await apiClient.get<ApiResponse<UserPreferenceResponse>>(BASE_PATH)
    if (!data?.data) {
      throw new Error('사용자 선호도를 불러오지 못했습니다.')
    }
    return data.data
  } catch (error) {
    throw handleApiError(error)
  }
}

export async function updateUserPreferences(
  payload: UserPreferenceUpdatePayload
): Promise<UserPreferenceResponse> {
  try {
    const { data } = await apiClient.put<ApiResponse<UserPreferenceResponse>>(BASE_PATH, payload)
    if (!data?.data) {
      throw new Error('사용자 선호도를 저장하지 못했습니다.')
    }
    return data.data
  } catch (error) {
    throw handleApiError(error)
  }
}
