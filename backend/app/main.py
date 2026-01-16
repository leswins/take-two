from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import api_router

app = FastAPI(
    title=settings.APP_NAME,
    description="API for analyzing sports commentary transcripts to identify player sentiment and bias",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,  # Disable docs in production
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Configure CORS - use cors_origins_list for proper parsing
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "status": "healthy",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for deployment platforms."""
    from app.core.database import check_database_connection

    # Check database connectivity
    db_healthy = False
    try:
        db_healthy = check_database_connection()
    except Exception:
        pass

    # Check Redis connectivity
    redis_healthy = False
    try:
        import redis
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        redis_healthy = True
    except Exception:
        # Redis is optional - don't fail health check if unavailable
        redis_healthy = None  # Unknown/unavailable

    status = "healthy" if db_healthy else "degraded"

    return {
        "status": status,
        "database": "connected" if db_healthy else "disconnected",
        "redis": "connected" if redis_healthy else ("unavailable" if redis_healthy is None else "disconnected"),
        "version": "1.0.0",
    }
