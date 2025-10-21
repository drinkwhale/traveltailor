import { apiClient, ApiResponse, handleApiError } from '@/lib/api'
import type {
  TravelPlanCreate,
  TravelPlanDetail,
  TravelPlanStatus,
  TravelPlanSummary,
  TravelPlanUpdate,
} from '@shared-types/travel-plan'
import type { PaginatedResponse } from '@shared-types/common'

const BASE_PATH = '/v1/travel-plans'

export async function createTravelPlan(request: TravelPlanCreate): Promise<TravelPlanDetail> {
  try {
    const { data } = await apiClient.post<ApiResponse<TravelPlanDetail>>(BASE_PATH, request)
    if (!data?.data) {
      throw new Error('여행 계획 생성에 실패했습니다.')
    }
    return data.data
  } catch (error) {
    throw handleApiError(error)
  }
}

export async function getTravelPlan(planId: string): Promise<TravelPlanDetail> {
  try {
    const { data } = await apiClient.get<ApiResponse<TravelPlanDetail>>(`${BASE_PATH}/${planId}`)
    if (!data?.data) {
      throw new Error('여행 계획을 불러오지 못했습니다.')
    }
    return data.data
  } catch (error) {
    throw handleApiError(error)
  }
}

export async function getTravelPlanStatus(planId: string): Promise<TravelPlanStatus> {
  try {
    const { data } = await apiClient.get<ApiResponse<TravelPlanStatus>>(
      `${BASE_PATH}/${planId}/status`
    )
    if (!data?.data) {
      throw new Error('생성 상태를 가져오지 못했습니다.')
    }
    return data.data
  } catch (error) {
    throw handleApiError(error)
  }
}

export async function listTravelPlans(
  page = 1,
  pageSize = 10
): Promise<PaginatedResponse<TravelPlanSummary>> {
  try {
    const { data } = await apiClient.get<ApiResponse<PaginatedResponse<TravelPlanSummary>>>(
      BASE_PATH,
      {
        params: { page, page_size: pageSize },
      }
    )
    if (!data?.data) {
      throw new Error('여행 계획 목록을 가져오지 못했습니다.')
    }
    return data.data
  } catch (error) {
    throw handleApiError(error)
  }
}

export async function updateTravelPlan(
  planId: string,
  payload: TravelPlanUpdate
): Promise<TravelPlanDetail> {
  try {
    const { data } = await apiClient.patch<ApiResponse<TravelPlanDetail>>(
      `${BASE_PATH}/${planId}`,
      payload
    )
    if (!data?.data) {
      throw new Error('여행 계획 업데이트에 실패했습니다.')
    }
    return data.data
  } catch (error) {
    throw handleApiError(error)
  }
}

export async function deleteTravelPlan(planId: string): Promise<void> {
  try {
    await apiClient.delete(`${BASE_PATH}/${planId}`)
  } catch (error) {
    throw handleApiError(error)
  }
}

