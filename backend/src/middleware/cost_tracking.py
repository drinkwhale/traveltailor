"""
AI Cost Tracking Middleware - AI API 비용 추적 및 예산 관리

T031c: AI 비용 추적 미들웨어 구현
- 일일 예산 $50 제한
- API 호출 비용 추적
- 예산 초과 시 경고 및 차단
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class CostTracker:
    """
    AI API 비용 추적기

    Features:
    - 일일 비용 추적
    - 예산 제한 관리
    - 비용 통계 제공
    """

    # OpenAI 가격 (2024년 기준, USD per 1K tokens)
    PRICING = {
        "gpt-4o": {"input": 0.0025, "output": 0.010},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "text-embedding-3-small": {"input": 0.00002, "output": 0.0},
        "text-embedding-3-large": {"input": 0.00013, "output": 0.0},
    }

    def __init__(self, daily_budget_usd: float = 50.0):
        """
        비용 추적기 초기화

        Args:
            daily_budget_usd: 일일 예산 (USD, 기본 $50)
        """
        self.daily_budget_usd = daily_budget_usd
        self.daily_costs: Dict[str, float] = {}  # date -> total_cost
        self.call_history: list = []  # API 호출 기록
        logger.info(f"CostTracker initialized with daily budget: ${daily_budget_usd}")

    def _get_today_key(self) -> str:
        """오늘 날짜 키 반환 (YYYY-MM-DD)"""
        return datetime.now().strftime("%Y-%m-%d")

    def get_today_cost(self) -> float:
        """
        오늘의 누적 비용 조회

        Returns:
            오늘의 총 비용 (USD)
        """
        today = self._get_today_key()
        return self.daily_costs.get(today, 0.0)

    def get_remaining_budget(self) -> float:
        """
        오늘의 남은 예산 조회

        Returns:
            남은 예산 (USD)
        """
        today_cost = self.get_today_cost()
        return max(0.0, self.daily_budget_usd - today_cost)

    def is_budget_exceeded(self) -> bool:
        """
        예산 초과 여부 확인

        Returns:
            예산 초과 시 True
        """
        return self.get_today_cost() >= self.daily_budget_usd

    def calculate_cost(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> float:
        """
        API 호출 비용 계산

        Args:
            model: 사용한 모델명
            prompt_tokens: 입력 토큰 수
            completion_tokens: 출력 토큰 수

        Returns:
            비용 (USD)
        """
        pricing = self.PRICING.get(model)

        if not pricing:
            logger.warning(f"Unknown model pricing: {model}, using gpt-4o-mini as default")
            pricing = self.PRICING["gpt-4o-mini"]

        input_cost = (prompt_tokens / 1000) * pricing["input"]
        output_cost = (completion_tokens / 1000) * pricing["output"]
        total_cost = input_cost + output_cost

        return total_cost

    def track_api_call(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        endpoint: str = "chat_completion",
    ) -> Dict[str, float]:
        """
        API 호출 추적 및 비용 기록

        Args:
            model: 사용한 모델명
            prompt_tokens: 입력 토큰 수
            completion_tokens: 출력 토큰 수
            endpoint: API 엔드포인트 이름

        Returns:
            비용 정보 딕셔너리
        """
        cost = self.calculate_cost(model, prompt_tokens, completion_tokens)
        today = self._get_today_key()

        # 일일 비용 누적
        self.daily_costs[today] = self.daily_costs.get(today, 0.0) + cost

        # 호출 기록 저장
        call_record = {
            "timestamp": datetime.now().isoformat(),
            "date": today,
            "endpoint": endpoint,
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "cost_usd": cost,
        }
        self.call_history.append(call_record)

        # 최근 1000개 기록만 유지 (메모리 관리)
        if len(self.call_history) > 1000:
            self.call_history = self.call_history[-1000:]

        logger.info(
            f"API call tracked: {endpoint} | {model} | "
            f"tokens={prompt_tokens + completion_tokens} | "
            f"cost=${cost:.4f} | "
            f"today_total=${self.daily_costs[today]:.2f}"
        )

        return {
            "cost": cost,
            "today_total": self.daily_costs[today],
            "remaining_budget": self.get_remaining_budget(),
            "budget_exceeded": self.is_budget_exceeded(),
        }

    def get_statistics(self, days: int = 7) -> Dict:
        """
        비용 통계 조회

        Args:
            days: 조회할 일수 (기본 7일)

        Returns:
            통계 딕셔너리
        """
        # 최근 N일 비용 계산
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days - 1)

        total_cost = 0.0
        daily_breakdown = {}

        current_date = start_date
        while current_date <= end_date:
            date_key = current_date.strftime("%Y-%m-%d")
            cost = self.daily_costs.get(date_key, 0.0)
            daily_breakdown[date_key] = cost
            total_cost += cost
            current_date += timedelta(days=1)

        # 호출 통계
        total_calls = len([r for r in self.call_history if r["date"] >= start_date.strftime("%Y-%m-%d")])

        return {
            "period_days": days,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "total_cost_usd": total_cost,
            "average_daily_cost_usd": total_cost / days if days > 0 else 0.0,
            "total_api_calls": total_calls,
            "daily_breakdown": daily_breakdown,
            "today": {
                "date": self._get_today_key(),
                "cost_usd": self.get_today_cost(),
                "budget_usd": self.daily_budget_usd,
                "remaining_usd": self.get_remaining_budget(),
                "budget_exceeded": self.is_budget_exceeded(),
            },
        }

    def reset_daily_costs(self) -> None:
        """일일 비용 초기화 (테스트/관리 용도)"""
        today = self._get_today_key()
        if today in self.daily_costs:
            old_cost = self.daily_costs[today]
            self.daily_costs[today] = 0.0
            logger.warning(f"Daily costs reset: {today} (was ${old_cost:.2f})")


class BudgetExceededError(Exception):
    """일일 예산 초과 예외"""
    pass


# Singleton 인스턴스
_cost_tracker: Optional[CostTracker] = None


def get_cost_tracker() -> CostTracker:
    """
    비용 추적기 싱글톤 인스턴스 가져오기

    Returns:
        CostTracker 인스턴스
    """
    global _cost_tracker

    if _cost_tracker is None:
        _cost_tracker = CostTracker()

    return _cost_tracker


@asynccontextmanager
async def track_ai_cost(
    model: str,
    endpoint: str = "unknown",
    enforce_budget: bool = True,
):
    """
    AI API 호출 비용 추적 컨텍스트 매니저

    Usage:
        async with track_ai_cost(model="gpt-4o-mini", endpoint="travel_plan"):
            response = await openai_client.create_chat_completion(...)
            # response에서 usage 정보를 추출하여 비용 기록
            yield response

    Args:
        model: 사용할 모델명
        endpoint: API 엔드포인트 이름
        enforce_budget: 예산 제한 강제 여부

    Raises:
        BudgetExceededError: 예산 초과 시 (enforce_budget=True)
    """
    tracker = get_cost_tracker()

    # 예산 체크
    if enforce_budget and tracker.is_budget_exceeded():
        remaining = tracker.get_remaining_budget()
        today_cost = tracker.get_today_cost()
        raise BudgetExceededError(
            f"Daily budget exceeded: ${today_cost:.2f} / ${tracker.daily_budget_usd:.2f} "
            f"(remaining: ${remaining:.2f})"
        )

    # API 호출 전 로그
    logger.debug(
        f"AI API call starting: {endpoint} | {model} | "
        f"budget remaining: ${tracker.get_remaining_budget():.2f}"
    )

    try:
        yield tracker  # 호출자가 tracker를 사용할 수 있도록 전달
    except Exception as e:
        logger.error(f"Error during AI API call: {e}")
        raise
    finally:
        # 호출 후 통계 로그 (실제 비용은 응답 후 track_api_call로 기록)
        logger.debug(
            f"AI API call completed: {endpoint} | "
            f"today_total=${tracker.get_today_cost():.2f}"
        )
