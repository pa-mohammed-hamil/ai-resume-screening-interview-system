"""
Main application entry point.

AI Resume Screening & Interview System
--------------------------------------
Initializes the FastAPI application, middleware,
exception handlers, API routes, and application lifecycle.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging import setup_logging
from app.core.middleware import RequestLoggingMiddleware


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

setup_logging()


# ---------------------------------------------------------------------------
# Application Lifecycle
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle.
    """

    # Startup
    print(f"Starting {settings.APP_NAME}...")

    # Add database initialization here if required.
    # Example:
    # await database.connect()

    # Add model/service initialization here if required.
    # Example:
    # await initialize_ai_services()

    yield

    # Shutdown
    print(f"Shutting down {settings.APP_NAME}...")

    # Close database connections / resources here.
    # Example:
    # await database.disconnect()


# ---------------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "AI-powered resume screening, candidate matching, "
        "ranking, and interview platform."
    ),
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Custom Middleware
# ---------------------------------------------------------------------------

app.add_middleware(RequestLoggingMiddleware)


# ---------------------------------------------------------------------------
# Exception Handlers
# ---------------------------------------------------------------------------

@app.exception_handler(AppException)
async def app_exception_handler(
    request: Request,
    exc: AppException,
):
    """
    Handle application-specific exceptions.
    """

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
            },
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    """
    Handle unexpected application errors.
    """

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred.",
            },
        },
    )


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------

app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX,
)


# ---------------------------------------------------------------------------
# Root Endpoint - Redirect to Frontend
# ---------------------------------------------------------------------------

@app.get(
    "/",
    tags=["System"],
    summary="Redirect to frontend",
    include_in_schema=False,
)
async def root():
    """
    Redirect to the frontend index page.
    """
    # Assuming frontend is served on port 3000
    return RedirectResponse(url="http://localhost:3000/index.html")


@app.get(
    "/api",
    tags=["System"],
    summary="Application information",
)
async def api_info():
    """
    Return basic application information.
    """

    return {
        "success": True,
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
    }


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------

@app.get(
    "/health",
    tags=["System"],
    summary="Health check",
)
async def health_check():
    """
    Basic application health check.
    """

    return {
        "success": True,
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# ---------------------------------------------------------------------------
# Readiness Check
# ---------------------------------------------------------------------------

@app.get(
    "/ready",
    tags=["System"],
    summary="Readiness check",
)
async def readiness_check():
    """
    Check whether the application is ready to receive traffic.

    Database, Redis, Celery, and AI service checks can be
    added here later.
    """

    return {
        "success": True,
        "status": "ready",
    }


# ---------------------------------------------------------------------------
# Development Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
