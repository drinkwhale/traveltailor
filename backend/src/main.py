"""
AI TravelTailor Backend - FastAPI Application Entry Point

This module wires cross-cutting concerns such as security hardening, rate
limiting, monitoring and observability tooling around the FastAPI application.
"""

from __future__ import annotations

import logging
import re
from contextlib import asynccontextmanager
from time import perf_counter
from typing import Iterable

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from posthog import Posthog
from sentry_sdk.integrations.fastapi import FastApiIntegration
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from .api.dependencies import limiter
from .api.v1 import auth, exports, preferences, recommendations, travel_plans
from .config.database import close_db  # init_db temporarily disabled
from .config.settings import settings
from .core.cache import close_redis_client
from .core.csrf import CsrfTokenResponse, get_csrf_token_endpoint
from .metrics.ai_pipeline import record_api_request, register_metrics
from .middleware.security_headers import add_security_headers_to_app
from .services.pdf import shutdown_pdf_renderer

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Third-party instrumentation
# ------------------------------------------------------------------------------

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=settings.SENTRY_SAMPLE_RATE,
        integrations=[FastApiIntegration()],
    )
    logger.info("Sentry SDK initialised")

_path_param_regex = re.compile(r"/[0-9a-fA-F-]{6,}")


def _normalise_route(path: str) -> str:
    """Replace UUIDs/IDs with :param so Prometheus label cardinality stays low."""
    return _path_param_regex.sub("/:param", path)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    posthog_client: Posthog | None = None
    # Temporarily disabled due to pgbouncer prepared statement issue
    # TODO: Re-enable after fixing database pooler configuration
    # await init_db()
    if settings.POSTHOG_API_KEY:
        posthog_client = Posthog(api_key=settings.POSTHOG_API_KEY, host=settings.POSTHOG_HOST)
        app.state.posthog = posthog_client
        logger.info("PostHog analytics client initialised")

    yield
    # Shutdown
    if hasattr(app.state, "posthog"):
        try:
            app.state.posthog.flush()
            app.state.posthog.shutdown()
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to shut down PostHog cleanly: %s", exc)

    await shutdown_pdf_renderer()
    await close_redis_client()
    await close_db()


# Application metadata
openapi_tags = [
    {
        "name": "Authentication",
        "description": "사용자 인증, 세션 쿠키 발급 및 토큰 관리",
    },
    {
        "name": "Travel Plans",
        "description": "여행 일정 생성, 조회, 수정 API",
    },
    {
        "name": "Exports",
        "description": "PDF, 지도 데이터 등 여행 결과물 다운로드",
    },
    {
        "name": "Preferences",
        "description": "선호도 학습 및 자동 업데이트",
    },
    {
        "name": "Recommendations",
        "description": "AI 추천 결과 및 통합 데이터",
    },
]

app = FastAPI(
    title="AI TravelTailor API",
    description="개인 맞춤형 여행 설계 서비스 - AI 기반 여행 일정 자동 생성",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    openapi_tags=openapi_tags,
)

# CORS configuration
allowed_origins: Iterable[str] = (origin for origin in settings.ALLOWED_ORIGINS if origin != "*")
sanitised_origins = list(allowed_origins)
if not sanitised_origins:
    sanitised_origins = ["http://localhost:3000"]
    logger.warning("No explicit ALLOWED_ORIGINS configured; falling back to %s", sanitised_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=sanitised_origins,
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"],
    expose_headers=["X-RateLimit-Remaining", "X-Response-Time-ms"],
)

add_security_headers_to_app(
    app,
    enable_csp=True,
    enable_hsts=settings.APP_ENV == "production",
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Return a JSON payload when rate limits trigger."""
    retry_after = (getattr(exc, "headers", None) or {}).get("Retry-After", "60")
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "detail": "요청 한도를 초과했습니다. 잠시 후 다시 시도하세요.",
            "retry_after": retry_after,
        },
        headers={"Retry-After": retry_after},
    )


app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.middleware("http")
async def response_time_monitor(request: Request, call_next):
    """Measure response latency and push metrics/headers."""
    start = perf_counter()
    response = await call_next(request)
    elapsed = perf_counter() - start
    response.headers["X-Response-Time-ms"] = f"{elapsed * 1000:.2f}"

    if settings.METRICS_ENABLED:
        route = _normalise_route(request.url.path)
        record_api_request(request.method, route, response.status_code, elapsed)

    if elapsed > 0.2:
        logger.warning(
            "Slow response detected: %s %s took %.3fs",
            request.method,
            request.url.path,
            elapsed,
        )

    return response

# Register routers
app.include_router(auth.router, prefix="/v1")
app.include_router(travel_plans.router, prefix="/v1")
app.include_router(exports.router, prefix="/v1")
app.include_router(recommendations.router, prefix="/v1")
app.include_router(preferences.router, prefix="/v1")

if settings.METRICS_ENABLED:
    register_metrics(app)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI TravelTailor API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "ai_service": "not_configured",  # Will be updated after AI setup
    }


@app.get("/v1/csrf-token", response_model=CsrfTokenResponse, tags=["Authentication"])
async def issue_csrf_token(request: Request) -> CsrfTokenResponse:
    """Expose CSRF token for httpOnly session flows."""
    return await get_csrf_token_endpoint(request)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
