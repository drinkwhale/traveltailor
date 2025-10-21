import { apiClient, ApiResponse, handleApiError } from '@/lib/api'
import type { MapExportResponse } from '@shared-types/map'

const EXPORTS_PATH = '/v1/exports'

export async function getMapExport(planId: string): Promise<MapExportResponse> {
  try {
    const { data } = await apiClient.get<ApiResponse<MapExportResponse>>(
      `${EXPORTS_PATH}/map/${planId}`
    )
    if (!data?.data) {
      throw new Error('지도 데이터를 불러오지 못했습니다.')
    }
    return data.data
  } catch (error) {
    throw handleApiError(error)
  }
}
