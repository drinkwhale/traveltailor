"""
OpenAI API client with timeout, retry logic, and error handling.

T031a: OpenAI API 타임아웃 및 Retry 로직 구현
- 60초 타임아웃 설정
- tenacity를 사용한 자동 재시도 (지수 백오프)
- API 오류에 대한 강건한 처리
"""

import logging
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI, OpenAIError, RateLimitError, APITimeoutError, APIConnectionError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from src.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class OpenAIClientError(Exception):
    """OpenAI 클라이언트 커스텀 예외"""
    pass


class OpenAIClient:
    """
    OpenAI API 클라이언트 with timeout and retry logic.

    Features:
    - 60초 타임아웃 설정
    - 자동 재시도 (최대 3회, 지수 백오프)
    - Rate limit 처리
    - 연결 오류 처리
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: float = 60.0,
        max_retries: int = 3,
    ):
        """
        OpenAI 클라이언트 초기화

        Args:
            api_key: OpenAI API 키 (None이면 설정에서 가져옴)
            timeout: API 호출 타임아웃 (초 단위, 기본 60초)
            max_retries: 최대 재시도 횟수 (기본 3회)
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.timeout = timeout
        self.max_retries = max_retries

        if not self.api_key:
            raise OpenAIClientError("OpenAI API key is required")

        self.client = AsyncOpenAI(
            api_key=self.api_key,
            timeout=self.timeout,
        )

        logger.info(
            f"OpenAI client initialized with timeout={timeout}s, max_retries={max_retries}"
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((RateLimitError, APITimeoutError, APIConnectionError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def create_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Chat completion 생성 with retry logic

        Args:
            messages: 대화 메시지 리스트
            model: 사용할 모델 (기본: gpt-4o-mini)
            temperature: 생성 온도 (0.0-2.0)
            max_tokens: 최대 토큰 수
            **kwargs: 추가 OpenAI API 파라미터

        Returns:
            API 응답 딕셔너리

        Raises:
            OpenAIClientError: API 호출 실패 시
        """
        try:
            logger.debug(
                f"Creating chat completion: model={model}, "
                f"messages_count={len(messages)}, temperature={temperature}"
            )

            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            logger.debug(f"Chat completion successful: {response.usage}")

            return {
                "content": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                "finish_reason": response.choices[0].finish_reason,
            }

        except RateLimitError as e:
            logger.warning(f"Rate limit exceeded: {e}")
            raise  # tenacity가 재시도 처리

        except APITimeoutError as e:
            logger.warning(f"API timeout after {self.timeout}s: {e}")
            raise  # tenacity가 재시도 처리

        except APIConnectionError as e:
            logger.warning(f"API connection error: {e}")
            raise  # tenacity가 재시도 처리

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise OpenAIClientError(f"OpenAI API error: {str(e)}") from e

        except Exception as e:
            logger.error(f"Unexpected error in chat completion: {e}")
            raise OpenAIClientError(f"Unexpected error: {str(e)}") from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((RateLimitError, APITimeoutError, APIConnectionError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def create_embedding(
        self,
        text: str,
        model: str = "text-embedding-3-small",
    ) -> List[float]:
        """
        텍스트 임베딩 생성 with retry logic

        Args:
            text: 임베딩할 텍스트
            model: 임베딩 모델 (기본: text-embedding-3-small)

        Returns:
            임베딩 벡터 (float 리스트)

        Raises:
            OpenAIClientError: API 호출 실패 시
        """
        try:
            logger.debug(f"Creating embedding: model={model}, text_length={len(text)}")

            response = await self.client.embeddings.create(
                model=model,
                input=text,
            )

            logger.debug(f"Embedding successful: {response.usage}")

            return response.data[0].embedding

        except (RateLimitError, APITimeoutError, APIConnectionError) as e:
            logger.warning(f"Retriable error in embedding: {e}")
            raise  # tenacity가 재시도 처리

        except OpenAIError as e:
            logger.error(f"OpenAI API error in embedding: {e}")
            raise OpenAIClientError(f"OpenAI API error: {str(e)}") from e

        except Exception as e:
            logger.error(f"Unexpected error in embedding: {e}")
            raise OpenAIClientError(f"Unexpected error: {str(e)}") from e

    async def estimate_tokens(self, text: str, model: str = "gpt-4") -> int:
        """
        텍스트의 예상 토큰 수 계산

        Args:
            text: 토큰 수를 계산할 텍스트
            model: 토큰 계산에 사용할 모델

        Returns:
            예상 토큰 수
        """
        try:
            import tiktoken

            encoding = tiktoken.encoding_for_model(model)
            tokens = encoding.encode(text)
            return len(tokens)

        except Exception as e:
            logger.warning(f"Token estimation failed: {e}, using rough estimate")
            # Fallback: 대략 4자당 1토큰으로 추정
            return len(text) // 4


# Singleton 인스턴스
_openai_client: Optional[OpenAIClient] = None


def get_openai_client() -> OpenAIClient:
    """
    OpenAI 클라이언트 싱글톤 인스턴스 가져오기

    Returns:
        OpenAIClient 인스턴스
    """
    global _openai_client

    if _openai_client is None:
        _openai_client = OpenAIClient()

    return _openai_client


async def cleanup_openai_client() -> None:
    """OpenAI 클라이언트 정리 (앱 종료 시 호출)"""
    global _openai_client

    if _openai_client is not None:
        await _openai_client.client.close()
        _openai_client = None
        logger.info("OpenAI client cleaned up")
