"""
Prometheus metrics exporter for AI pipeline.
이 모듈은 AI 관련 서비스 호출에 대한 지표를 수집하고 `/metrics` 엔드포인트를 제공한다.
"""

from __future__ import annotations

from fastapi import APIRouter, FastAPI, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

# Prometheus Collector Registry
registry = CollectorRegistry()

# Metrics definitions
ai_requests_total = Counter(
    "ai_requests_total",
    "Total number of AI generation requests",
    ["model", "status"],
    registry=registry,
)

ai_request_latency_seconds = Histogram(
    "ai_request_latency_seconds",
    "Latency of AI generation requests",
    ["model"],
    buckets=(0.5, 1, 2, 4, 8, 16, 32),
    registry=registry,
)

ai_tokens_total = Counter(
    "ai_tokens_total",
    "Total prompt and completion tokens consumed",
    ["model", "token_type"],
    registry=registry,
)

ai_fallback_total = Counter(
    "ai_fallback_total",
    "Number of times the fallback rules fired",
    ["reason"],
    registry=registry,
)

ai_daily_budget_remaining = Gauge(
    "ai_daily_budget_remaining_usd",
    "Remaining AI budget for the current UTC day",
    registry=registry,
)

# FastAPI router for /metrics endpoint
metrics_router = APIRouter()


@metrics_router.get("/metrics", include_in_schema=False)
async def metrics_endpoint() -> Response:
    """Expose metrics for Prometheus scrapers."""
    data = generate_latest(registry)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


def observe_request(model: str, status: str, latency_seconds: float) -> None:
    """Record a completed AI request with latency."""
    ai_requests_total.labels(model=model, status=status).inc()
    ai_request_latency_seconds.labels(model=model).observe(latency_seconds)


def record_token_usage(model: str, prompt_tokens: int, completion_tokens: int) -> None:
    """Record prompt and completion token usage for a model."""
    if prompt_tokens:
        ai_tokens_total.labels(model=model, token_type="prompt").inc(prompt_tokens)
    if completion_tokens:
        ai_tokens_total.labels(model=model, token_type="completion").inc(completion_tokens)


def record_fallback(reason: str) -> None:
    """Count fallback activations by reason."""
    ai_fallback_total.labels(reason=reason).inc()


def update_daily_budget_remaining(amount_usd: float) -> None:
    """Update remaining AI budget gauge."""
    ai_daily_budget_remaining.set(amount_usd)


def register_metrics(app: FastAPI) -> None:
    """Attach the metrics router to a FastAPI application."""
    app.include_router(metrics_router)
