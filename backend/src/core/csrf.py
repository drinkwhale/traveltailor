"""
CSRF Protection - Cross-Site Request Forgery 방어

T032b: CSRF 보호 설정
- POST/PUT/DELETE 엔드포인트에 CSRF 토큰 검증
- 쿠키 기반 토큰 관리
- 예외 경로 설정 (API 키 인증 등)
"""

import logging
from typing import Optional, Set

from fastapi import Depends, HTTPException, Request
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
from pydantic import BaseModel

from ..config.settings import settings

logger = logging.getLogger(__name__)


class CsrfSettings(BaseModel):
    """CSRF 설정 모델"""

    secret_key: str = settings.SECRET_KEY
    cookie_name: str = "csrf_token"
    header_name: str = "X-CSRF-Token"
    cookie_secure: bool = settings.APP_ENV == "production"
    cookie_httponly: bool = True
    cookie_samesite: str = settings.SESSION_COOKIE_SAMESITE
    token_location: str = "header"  # or "body"


# CSRF 보호 제외 경로 (API 키 인증 등)
CSRF_EXEMPT_PATHS: Set[str] = {
    "/v1/auth/login",
    "/v1/auth/signup",
    "/v1/auth/refresh",
    "/v1/auth/logout",
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
}

# CSRF 보호 제외 메서드
CSRF_EXEMPT_METHODS: Set[str] = {
    "GET",
    "HEAD",
    "OPTIONS",
}


@CsrfProtect.load_config
def get_csrf_config():
    """
    CSRF 설정 로드

    Returns:
        CsrfSettings 인스턴스
    """
    return CsrfSettings()


def is_csrf_exempt(request: Request) -> bool:
    """
    CSRF 보호 제외 여부 확인

    Args:
        request: HTTP 요청

    Returns:
        제외 대상이면 True
    """
    # 메서드 체크
    if request.method in CSRF_EXEMPT_METHODS:
        return True

    # 경로 체크
    path = request.url.path
    if path in CSRF_EXEMPT_PATHS:
        return True

    # API 키 인증 체크 (Authorization 헤더)
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        # JWT 토큰 인증은 CSRF 공격에 면역이므로 제외
        return True

    return False


async def validate_csrf_token(request: Request, csrf_protect: CsrfProtect) -> None:
    """
    CSRF 토큰 검증

    Args:
        request: HTTP 요청
        csrf_protect: CsrfProtect 인스턴스

    Raises:
        HTTPException: CSRF 토큰 검증 실패 시
    """
    # CSRF 보호 제외 대상 체크
    if is_csrf_exempt(request):
        logger.debug(f"CSRF protection skipped for {request.method} {request.url.path}")
        return

    try:
        # CSRF 토큰 검증
        await csrf_protect.validate_csrf(request)
        logger.debug(f"CSRF token validated for {request.method} {request.url.path}")

    except CsrfProtectError as e:
        logger.warning(
            f"CSRF validation failed: {e} | "
            f"path={request.url.path} | "
            f"method={request.method} | "
            f"client={request.client.host if request.client else 'unknown'}"
        )
        raise HTTPException(
            status_code=403,
            detail="CSRF token validation failed. Please refresh the page and try again.",
        )


def generate_csrf_token(csrf_protect: CsrfProtect, request: Request) -> str:
    """
    CSRF 토큰 생성

    Args:
        csrf_protect: CsrfProtect 인스턴스
        request: HTTP 요청

    Returns:
        생성된 CSRF 토큰
    """
    try:
        token = csrf_protect.generate_csrf(request)
        logger.debug(f"CSRF token generated for {request.url.path}")
        return token

    except Exception as e:
        logger.error(f"Failed to generate CSRF token: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate CSRF token",
        )


async def csrf_protect_middleware(request: Request, call_next):
    """
    CSRF 보호 미들웨어

    Args:
        request: HTTP 요청
        call_next: 다음 미들웨어/핸들러

    Returns:
        응답
    """
    # CSRF 보호 제외 대상 체크
    if not is_csrf_exempt(request):
        # CSRF 토큰 검증은 의존성 주입으로 처리
        # 이 미들웨어에서는 로깅만 수행
        logger.debug(f"CSRF protection required for {request.method} {request.url.path}")

    response = await call_next(request)
    return response


# 의존성 주입용 CSRF 검증 함수
async def require_csrf_token(
    request: Request,
    csrf_protect: CsrfProtect = Depends(),
) -> None:
    """
    CSRF 토큰 필수 검증 (의존성 주입용)

    Usage:
        @app.post("/api/v1/items", dependencies=[Depends(require_csrf_token)])
        async def create_item(...):
            ...

    Args:
        request: HTTP 요청
        csrf_protect: CsrfProtect 인스턴스

    Raises:
        HTTPException: CSRF 토큰 검증 실패 시
    """
    await validate_csrf_token(request, csrf_protect)


class CsrfTokenResponse(BaseModel):
    """CSRF 토큰 응답 모델"""

    csrf_token: str
    token_name: str = "X-CSRF-Token"


async def get_csrf_token_endpoint(
    request: Request,
    csrf_protect: CsrfProtect = None,
) -> CsrfTokenResponse:
    """
    CSRF 토큰 발급 엔드포인트

    Usage:
        @app.get("/api/v1/csrf-token")
        async def get_csrf_token(request: Request):
            return await get_csrf_token_endpoint(request)

    Args:
        request: HTTP 요청
        csrf_protect: CsrfProtect 인스턴스

    Returns:
        CSRF 토큰 응답
    """
    if csrf_protect is None:
        csrf_protect = CsrfProtect()

    token = generate_csrf_token(csrf_protect, request)

    return CsrfTokenResponse(csrf_token=token)
