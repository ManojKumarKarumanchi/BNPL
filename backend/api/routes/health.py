"""Health check routes."""

from fastapi import APIRouter
from api.schemas.response_schemas import HealthResponse
from api.config import settings

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns:
        Service health status
    """
    # Simple health check - could add DB connectivity check later
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        mcp_server="connected"
    )


@router.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }
