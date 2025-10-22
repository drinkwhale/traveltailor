"""
AI TravelTailor Backend - FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config.settings import settings
from .config.database import init_db, close_db
from .api.v1 import auth, exports, preferences, recommendations, travel_plans
from .metrics.ai_pipeline import register_metrics
from .services.pdf import shutdown_pdf_renderer


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await init_db()
    yield
    # Shutdown
    await shutdown_pdf_renderer()
    await close_db()


# Application metadata
app = FastAPI(
    title="AI TravelTailor API",
    description="개인 맞춤형 여행 설계 서비스 - AI 기반 여행 일정 자동 생성",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
