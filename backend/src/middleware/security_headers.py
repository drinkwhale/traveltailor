"""
Security Headers Middleware - 보안 헤더 설정

T032a: 보안 헤더 미들웨어 구현
- CSP (Content Security Policy)
- X-XSS-Protection
- HSTS (HTTP Strict Transport Security)
- X-Content-Type-Options
- X-Frame-Options
"""

import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    보안 헤더 자동 추가 미들웨어

    주요 보안 헤더:
    - Content-Security-Policy: XSS 및 데이터 주입 공격 방어
    - X-XSS-Protection: 브라우저 XSS 필터 활성화
    - Strict-Transport-Security: HTTPS 강제
    - X-Content-Type-Options: MIME 타입 스니핑 방지
    - X-Frame-Options: 클릭재킹 방어
    - Referrer-Policy: Referrer 정보 제어
    - Permissions-Policy: 브라우저 기능 접근 제어
    """

    def __init__(
        self,
        app,
        enable_csp: bool = True,
        enable_hsts: bool = True,
        hsts_max_age: int = 31536000,  # 1년
    ):
        """
        보안 헤더 미들웨어 초기화

        Args:
            app: FastAPI 애플리케이션
            enable_csp: CSP 헤더 활성화 여부
            enable_hsts: HSTS 헤더 활성화 여부
            hsts_max_age: HSTS 최대 유효 기간 (초)
        """
        super().__init__(app)
        self.enable_csp = enable_csp
        self.enable_hsts = enable_hsts
        self.hsts_max_age = hsts_max_age
        logger.info(
            f"SecurityHeadersMiddleware initialized: "
            f"CSP={enable_csp}, HSTS={enable_hsts}"
        )

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """
        요청 처리 및 보안 헤더 추가

        Args:
            request: HTTP 요청
            call_next: 다음 미들웨어/핸들러

        Returns:
            보안 헤더가 추가된 응답
        """
        # 요청 처리
        response = await call_next(request)

        # 보안 헤더 추가
        self._add_security_headers(response)

        return response

    def _add_security_headers(self, response: Response) -> None:
        """
        응답에 보안 헤더 추가

        Args:
            response: HTTP 응답 객체
        """
        # X-Content-Type-Options: MIME 타입 스니핑 방지
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-Frame-Options: 클릭재킹 방어
        response.headers["X-Frame-Options"] = "DENY"

        # X-XSS-Protection: 브라우저 XSS 필터 활성화
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer-Policy: Referrer 정보 제어
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions-Policy: 브라우저 기능 접근 제어
        response.headers["Permissions-Policy"] = (
            "geolocation=(self), "
            "microphone=(), "
            "camera=(), "
            "payment=()"
        )

        # Content-Security-Policy (선택적)
        if self.enable_csp:
            csp_directives = self._build_csp_policy()
            response.headers["Content-Security-Policy"] = csp_directives

        # Strict-Transport-Security (HTTPS 환경에서만, 선택적)
        if self.enable_hsts:
            response.headers["Strict-Transport-Security"] = (
                f"max-age={self.hsts_max_age}; "
                "includeSubDomains; "
                "preload"
            )

    def _build_csp_policy(self) -> str:
        """
        Content Security Policy 정책 생성

        Returns:
            CSP 정책 문자열
        """
        # 기본 CSP 정책
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net",
            "font-src 'self' https://fonts.gstatic.com data:",
            "img-src 'self' data: https: blob:",
            "connect-src 'self' https://api.openai.com https://maps.googleapis.com https://api.mapbox.com",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "upgrade-insecure-requests",
        ]

        return "; ".join(csp_directives)


def add_security_headers_to_app(app, **kwargs):
    """
    FastAPI 앱에 보안 헤더 미들웨어 추가

    Args:
        app: FastAPI 애플리케이션
        **kwargs: SecurityHeadersMiddleware 설정
    """
    app.add_middleware(SecurityHeadersMiddleware, **kwargs)
    logger.info("Security headers middleware added to application")
