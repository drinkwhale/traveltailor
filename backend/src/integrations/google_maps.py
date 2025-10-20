"""
Google Places API 클라이언트

Google Places API를 사용하여 장소 검색, 상세 정보 조회 기능을 제공합니다.
"""

import os
from typing import List, Dict, Any, Optional
import httpx
from ..config import settings


class GoogleMapsClient:
    """Google Maps API 클라이언트"""

    def __init__(self):
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        self.base_url = "https://maps.googleapis.com/maps/api"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """HTTP 클라이언트 종료"""
        await self.client.aclose()

    async def search_places(
        self,
        query: str,
        location: Optional[str] = None,
        radius: int = 5000,
        place_type: Optional[str] = None,
        language: str = "ko",
    ) -> List[Dict[str, Any]]:
        """
        장소 검색

        Args:
            query: 검색어 (예: "도쿄 맛집", "서울 호텔")
            location: 중심 좌표 (lat,lng 형식, 예: "35.6762,139.6503")
            radius: 검색 반경 (미터 단위, 기본 5km)
            place_type: 장소 타입 (restaurant, lodging, tourist_attraction 등)
            language: 응답 언어 (기본 한국어)

        Returns:
            검색 결과 리스트
        """
        url = f"{self.base_url}/place/textsearch/json"

        params = {
            "query": query,
            "key": self.api_key,
            "language": language,
        }

        if location:
            params["location"] = location
            params["radius"] = radius

        if place_type:
            params["type"] = place_type

        response = await self.client.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        if data.get("status") != "OK":
            raise Exception(f"Google Places API Error: {data.get('status')}")

        return data.get("results", [])

    async def get_place_details(
        self,
        place_id: str,
        language: str = "ko",
        fields: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        장소 상세 정보 조회

        Args:
            place_id: Google Place ID
            language: 응답 언어 (기본 한국어)
            fields: 조회할 필드 리스트 (미지정 시 기본 필드)

        Returns:
            장소 상세 정보
        """
        url = f"{self.base_url}/place/details/json"

        # 기본 필드 설정
        if fields is None:
            fields = [
                "name",
                "formatted_address",
                "geometry",
                "rating",
                "user_ratings_total",
                "price_level",
                "opening_hours",
                "photos",
                "formatted_phone_number",
                "website",
                "types",
            ]

        params = {
            "place_id": place_id,
            "key": self.api_key,
            "language": language,
            "fields": ",".join(fields),
        }

        response = await self.client.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        if data.get("status") != "OK":
            raise Exception(f"Google Places API Error: {data.get('status')}")

        return data.get("result", {})

    async def get_photo_url(
        self,
        photo_reference: str,
        max_width: int = 800,
    ) -> str:
        """
        장소 사진 URL 생성

        Args:
            photo_reference: 사진 참조 ID
            max_width: 최대 너비 (픽셀, 최대 1600)

        Returns:
            사진 URL
        """
        return (
            f"{self.base_url}/place/photo"
            f"?maxwidth={max_width}"
            f"&photoreference={photo_reference}"
            f"&key={self.api_key}"
        )

    async def find_nearby_places(
        self,
        latitude: float,
        longitude: float,
        radius: int = 1000,
        place_type: Optional[str] = None,
        keyword: Optional[str] = None,
        language: str = "ko",
    ) -> List[Dict[str, Any]]:
        """
        주변 장소 검색 (좌표 기반)

        Args:
            latitude: 위도
            longitude: 경도
            radius: 검색 반경 (미터)
            place_type: 장소 타입
            keyword: 키워드
            language: 응답 언어

        Returns:
            주변 장소 리스트
        """
        url = f"{self.base_url}/place/nearbysearch/json"

        params = {
            "location": f"{latitude},{longitude}",
            "radius": radius,
            "key": self.api_key,
            "language": language,
        }

        if place_type:
            params["type"] = place_type

        if keyword:
            params["keyword"] = keyword

        response = await self.client.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        if data.get("status") not in ["OK", "ZERO_RESULTS"]:
            raise Exception(f"Google Places API Error: {data.get('status')}")

        return data.get("results", [])


# 싱글톤 인스턴스
_google_maps_client: Optional[GoogleMapsClient] = None


def get_google_maps_client() -> GoogleMapsClient:
    """Google Maps 클라이언트 싱글톤 인스턴스 반환"""
    global _google_maps_client
    if _google_maps_client is None:
        _google_maps_client = GoogleMapsClient()
    return _google_maps_client
