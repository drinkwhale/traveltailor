import { apiClient, ApiResponse, handleApiError } from '@/lib/api'
import type {
  FlightRecommendations,
  AccommodationRecommendations,
} from '@shared-types/recommendations'

const BASE_PATH = '/v1/recommendations'

export async function getFlightRecommendations(planId: string): Promise<FlightRecommendations> {
  try {
    const { data } = await apiClient.get<ApiResponse<FlightRecommendations>>(
      `${BASE_PATH}/flights/${planId}`
    )
    if (!data?.data) {
      throw new Error('항공편 추천을 불러오지 못했습니다.')
    }
    return data.data
  } catch (error) {
    throw handleApiError(error)
  }
}

export async function getAccommodationRecommendations(
  planId: string
): Promise<AccommodationRecommendations> {
  try {
    const { data } = await apiClient.get<ApiResponse<AccommodationRecommendations>>(
      `${BASE_PATH}/accommodations/${planId}`
    )
    if (!data?.data) {
      throw new Error('숙박 추천을 불러오지 못했습니다.')
    }
    return data.data
  } catch (error) {
    throw handleApiError(error)
  }
}
