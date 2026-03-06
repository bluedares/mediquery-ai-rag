"""
MediQuery AI - FastAPI Application
Main entry point for the API
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
from datetime import datetime

from app.config import settings
from app.utils.logger import logger
from app.models.responses import HealthResponse


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events for FastAPI application
    - Startup: Initialize services
    - Shutdown: Cleanup resources
    """
    # Startup
    logger.info(
        "🚀 Starting MediQuery AI",
        app_name=settings.app_name,
        version=settings.app_version,
        debug_mode=settings.debug_mode
    )
    
    # TODO: Initialize services
    # - Bedrock client
    # - OpenSearch client
    # - S3 client
    # - Embedding model
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down MediQuery AI")
    # TODO: Cleanup resources


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Clinical Document Intelligence Platform with Multi-Agent RAG",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug_mode else None,
    redoc_url="/redoc" if settings.debug_mode else None,
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:5174",  # Vite dev server (alternate port)
        "http://localhost:3000",  # Alternative dev port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:3000",
        "https://mediquery-frontend.onrender.com",  # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with timing"""
    start_time = time.time()
    
    # Log request
    logger.info(
        "📨 Incoming request",
        method=request.method,
        path=request.url.path,
        client=request.client.host if request.client else "unknown"
    )
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000
    
    # Log response
    logger.info(
        "📤 Response sent",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round(duration_ms, 2)
    )
    
    # Add custom headers
    response.headers["X-Process-Time"] = str(duration_ms)
    response.headers["X-Request-ID"] = str(time.time())
    
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(
        "❌ Unhandled exception",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
        exc_info=settings.include_stack_trace
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.verbose_errors else "An error occurred",
            "type": type(exc).__name__
        }
    )


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    
    Returns system status and service availability
    """
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.now(),
        services={
            "bedrock": "available",  # TODO: Check actual status
            "opensearch": "available",
            "s3": "available"
        },
        debug_mode=settings.debug_mode
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Clinical Document Intelligence Platform",
        "docs": "/docs" if settings.debug_mode else "disabled",
        "health": "/health",
        "api_prefix": settings.api_prefix
    }


# Import routers
from app.api import health, upload, query, documents, storage

# Include routers
app.include_router(health.router, prefix=settings.api_prefix, tags=["Health"])
app.include_router(upload.router, prefix=settings.api_prefix, tags=["Upload"])
app.include_router(query.router, prefix=settings.api_prefix, tags=["Query"])
app.include_router(documents.router, prefix=settings.api_prefix, tags=["Documents"])
app.include_router(storage.router, prefix=f"{settings.api_prefix}/storage", tags=["Storage"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug_mode,
        log_level=settings.log_level.value.lower()
    )
