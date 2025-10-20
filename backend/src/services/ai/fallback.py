"""
AI Fallback Mechanism - 규칙 기반 백업 시스템

T031b: AI Fallback 메커니즘 구현
- OpenAI API 장애 시 규칙 기반 응답 제공
- 기본적인 여행 일정 생성 로직
- 사용자에게 명확한 피드백 제공
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class FallbackTravelPlanner:
    """
    규칙 기반 여행 계획 생성기

    AI API가 실패할 때 기본적인 여행 일정을 생성합니다.
    완벽하지는 않지만 사용자에게 최소한의 서비스를 제공합니다.
    """

    # 목적지별 인기 장소 (하드코딩 - 실제로는 DB나 외부 API에서 가져와야 함)
    POPULAR_PLACES = {
        "도쿄": {
            "관광": ["센소지", "메이지 신궁", "도쿄 타워", "아사쿠사", "시부야"],
            "맛집": ["스시 잔마이", "이치란 라멘", "규카츠 모토무라", "츠키지 시장"],
            "숙박": ["신주쿠", "시부야", "우에노", "아사쿠사"],
        },
        "오사카": {
            "관광": ["오사카성", "도톤보리", "우메다 스카이 빌딩", "신사이바시"],
            "맛집": ["오코노미야키", "타코야키", "쿠시카츠", "라멘"],
            "숙박": ["난바", "우메다", "신오사카"],
        },
        "서울": {
            "관광": ["경복궁", "남산타워", "명동", "홍대", "강남"],
            "맛집": ["삼겹살", "비빔밥", "냉면", "치킨", "한정식"],
            "숙박": ["명동", "강남", "홍대", "이태원"],
        },
        # 더 많은 도시 추가 가능
    }

    # 시간대별 기본 활동
    DEFAULT_ACTIVITIES = {
        "morning": {"start": "09:00", "duration": 2, "type": "관광"},
        "lunch": {"start": "12:00", "duration": 1.5, "type": "식사"},
        "afternoon": {"start": "14:00", "duration": 3, "type": "관광"},
        "dinner": {"start": "18:00", "duration": 1.5, "type": "식사"},
        "evening": {"start": "20:00", "duration": 2, "type": "관광"},
    }

    def __init__(self) -> None:
        """Fallback planner 초기화"""
        self.is_fallback = True
        logger.info("FallbackTravelPlanner initialized")

    async def generate_travel_plan(
        self,
        destination: str,
        start_date: datetime,
        end_date: datetime,
        budget: int,
        travelers: int = 1,
        preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        규칙 기반 여행 계획 생성

        Args:
            destination: 목적지
            start_date: 여행 시작일
            end_date: 여행 종료일
            budget: 총 예산 (원)
            travelers: 여행자 수
            preferences: 사용자 선호도

        Returns:
            기본 여행 계획 딕셔너리
        """
        logger.warning(
            f"Using fallback travel planner for {destination} "
            f"({start_date.date()} ~ {end_date.date()})"
        )

        days = (end_date - start_date).days + 1
        daily_budget = budget // days if days > 0 else budget

        # 일일 일정 생성
        daily_itineraries = []
        current_date = start_date

        for day_number in range(1, days + 1):
            daily_plan = self._generate_daily_plan(
                destination=destination,
                date=current_date,
                day_number=day_number,
                daily_budget=daily_budget,
                preferences=preferences,
            )
            daily_itineraries.append(daily_plan)
            current_date += timedelta(days=1)

        return {
            "destination": destination,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days,
            "budget": budget,
            "travelers": travelers,
            "daily_itineraries": daily_itineraries,
            "is_fallback": True,
            "warning": "⚠️ AI 서비스가 일시적으로 사용 불가능하여 기본 일정을 생성했습니다. "
            "나중에 다시 시도하시면 더 맞춤화된 일정을 받으실 수 있습니다.",
        }

    def _generate_daily_plan(
        self,
        destination: str,
        date: datetime,
        day_number: int,
        daily_budget: int,
        preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        하루 일정 생성

        Args:
            destination: 목적지
            date: 날짜
            day_number: 일차
            daily_budget: 하루 예산
            preferences: 사용자 선호도

        Returns:
            하루 일정 딕셔너리
        """
        places = self._get_places_for_destination(destination, preferences)

        activities = []
        activity_index = 0

        for time_slot, config in self.DEFAULT_ACTIVITIES.items():
            if activity_index >= len(places):
                activity_index = 0  # 장소 부족하면 순환

            place = places[activity_index]
            activity = {
                "time": config["start"],
                "duration": config["duration"],
                "type": config["type"],
                "place": place,
                "estimated_cost": self._estimate_activity_cost(
                    config["type"], daily_budget
                ),
            }
            activities.append(activity)
            activity_index += 1

        return {
            "day": day_number,
            "date": date.isoformat(),
            "activities": activities,
            "daily_budget": daily_budget,
        }

    def _get_places_for_destination(
        self, destination: str, preferences: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        목적지에 맞는 장소 리스트 가져오기

        Args:
            destination: 목적지
            preferences: 사용자 선호도

        Returns:
            장소 이름 리스트
        """
        # 목적지에 해당하는 인기 장소 가져오기
        places_dict = self.POPULAR_PLACES.get(destination, {})

        all_places = []
        for category, places in places_dict.items():
            all_places.extend(places)

        if not all_places:
            # 등록되지 않은 도시는 기본 활동 제공
            all_places = [
                f"{destination} 중심가",
                f"{destination} 시장",
                f"{destination} 박물관",
                f"{destination} 공원",
                "현지 맛집",
            ]

        return all_places

    def _estimate_activity_cost(self, activity_type: str, daily_budget: int) -> int:
        """
        활동 유형별 예상 비용 계산

        Args:
            activity_type: 활동 유형 (관광/식사 등)
            daily_budget: 하루 예산

        Returns:
            예상 비용 (원)
        """
        cost_ratios = {
            "관광": 0.2,  # 예산의 20%
            "식사": 0.25,  # 예산의 25%
            "교통": 0.1,  # 예산의 10%
            "기타": 0.15,  # 예산의 15%
        }

        ratio = cost_ratios.get(activity_type, 0.15)
        return int(daily_budget * ratio)

    async def get_place_recommendations(
        self,
        destination: str,
        category: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        장소 추천 (규칙 기반)

        Args:
            destination: 목적지
            category: 카테고리 (관광/맛집/숙박)
            limit: 추천 개수

        Returns:
            추천 장소 리스트
        """
        logger.warning(f"Using fallback place recommendations for {destination}/{category}")

        places_dict = self.POPULAR_PLACES.get(destination, {})
        places = places_dict.get(category, [])

        recommendations = []
        for i, place_name in enumerate(places[:limit]):
            recommendations.append(
                {
                    "name": place_name,
                    "category": category,
                    "rating": 4.0,  # 기본 평점
                    "description": f"{destination}의 인기 {category} 장소",
                    "is_fallback": True,
                }
            )

        if not recommendations:
            # 카테고리에 맞는 장소가 없으면 기본값 제공
            recommendations.append(
                {
                    "name": f"{destination} 추천 장소",
                    "category": category,
                    "rating": 3.5,
                    "description": "AI 서비스 일시 중단으로 기본 추천을 제공합니다",
                    "is_fallback": True,
                }
            )

        return recommendations


# Singleton 인스턴스
_fallback_planner: Optional[FallbackTravelPlanner] = None


def get_fallback_planner() -> FallbackTravelPlanner:
    """
    Fallback planner 싱글톤 인스턴스 가져오기

    Returns:
        FallbackTravelPlanner 인스턴스
    """
    global _fallback_planner

    if _fallback_planner is None:
        _fallback_planner = FallbackTravelPlanner()

    return _fallback_planner
