"""
AI 서비스 모듈

OpenAI 및 LangChain을 사용한 AI 기반 여행 계획 서비스
"""

from typing import Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from ...config import settings


class AIClient:
    """AI 클라이언트 (OpenAI + LangChain)"""

    def __init__(self):
        """AI 클라이언트 초기화"""
        self.model_name = settings.OPENAI_MODEL or "gpt-4o-mini"
        self.temperature = 0.7
        self.max_tokens = 4000

        # LangChain ChatOpenAI 초기화
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            openai_api_key=settings.OPENAI_API_KEY,
        )

    async def generate_text(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        텍스트 생성

        Args:
            prompt: 사용자 프롬프트
            system_message: 시스템 메시지 (역할 정의)
            temperature: 생성 온도 (0.0 ~ 1.0)

        Returns:
            생성된 텍스트
        """
        messages = []

        if system_message:
            messages.append(SystemMessage(content=system_message))

        messages.append(HumanMessage(content=prompt))

        # 온도 설정이 있으면 임시 LLM 생성
        if temperature is not None:
            llm = ChatOpenAI(
                model=self.model_name,
                temperature=temperature,
                max_tokens=self.max_tokens,
                openai_api_key=settings.OPENAI_API_KEY,
            )
        else:
            llm = self.llm

        # LangChain invoke 호출
        response = await llm.ainvoke(messages)

        return response.content

    async def analyze_user_preferences(self, user_input: str) -> dict:
        """
        사용자 입력에서 여행 선호도 추출

        Args:
            user_input: 사용자 입력 텍스트

        Returns:
            추출된 선호도 정보
        """
        system_message = """
당신은 여행 계획 전문가입니다.
사용자의 입력에서 다음 정보를 추출하여 JSON 형식으로 반환하세요:
- travel_style: 여행 스타일 (relaxed, moderate, packed)
- interests: 관심사 리스트 (문화, 음식, 자연, 쇼핑, 액티비티 등)
- budget_preference: 예산 선호도 (budget, moderate, luxury)
- pace: 여행 페이스 (slow, normal, fast)

JSON 형식만 반환하고 다른 설명은 포함하지 마세요.
        """

        response = await self.generate_text(
            prompt=user_input,
            system_message=system_message,
            temperature=0.3,  # 낮은 온도로 일관성 있는 분석
        )

        # JSON 파싱 (실제로는 더 robust한 파싱 필요)
        import json

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # 파싱 실패 시 기본값 반환
            return {
                "travel_style": "moderate",
                "interests": ["문화", "음식"],
                "budget_preference": "moderate",
                "pace": "normal",
            }

    async def generate_itinerary_suggestions(
        self,
        destination: str,
        duration_days: int,
        preferences: dict,
    ) -> str:
        """
        여행 일정 제안 생성

        Args:
            destination: 목적지
            duration_days: 여행 일수
            preferences: 사용자 선호도

        Returns:
            일정 제안 텍스트
        """
        system_message = """
당신은 전문 여행 계획가입니다.
사용자의 선호도에 맞춰 최적의 여행 일정을 제안하세요.
각 일자별로 시간대별 활동을 포함하고, 이동 경로도 고려하세요.
        """

        prompt = f"""
목적지: {destination}
여행 기간: {duration_days}일
여행 스타일: {preferences.get('travel_style', 'moderate')}
관심사: {', '.join(preferences.get('interests', []))}
예산: {preferences.get('budget_preference', 'moderate')}

위 정보를 바탕으로 상세한 일정을 작성해주세요.
        """

        return await self.generate_text(
            prompt=prompt,
            system_message=system_message,
            temperature=0.8,  # 창의적인 제안을 위해 높은 온도
        )


# 싱글톤 인스턴스
_ai_client: Optional[AIClient] = None


def get_ai_client() -> AIClient:
    """AI 클라이언트 싱글톤 인스턴스 반환"""
    global _ai_client
    if _ai_client is None:
        _ai_client = AIClient()
    return _ai_client
