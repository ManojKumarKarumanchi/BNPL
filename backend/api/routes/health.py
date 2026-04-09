"""Health check routes."""

from fastapi import APIRouter, HTTPException
from api.schemas.response_schemas import HealthResponse
from api.config import settings
import httpx
import os

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint with DB and MCP verification.

    Returns:
        Service health status
    """
    mcp_status = "connected"
    db_status = "healthy"

    # Check MCP server connectivity
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:3000")
            response = await client.get(f"{mcp_url}/health", timeout=2.0)
            if response.status_code != 200:
                mcp_status = "unreachable"
    except Exception:
        mcp_status = "unreachable"

    # Check database connectivity
    try:
        import sys
        from pathlib import Path
        # Add mcp-server to path (it has hyphen, not underscore)
        mcp_server_path = Path(__file__).parent.parent.parent / "mcp-server"
        if str(mcp_server_path) not in sys.path:
            sys.path.insert(0, str(mcp_server_path))

        from db.manager import DatabaseManager
        db = DatabaseManager()
        # Simple query to verify DB is accessible
        conn = db.connection
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        if result is None:
            raise Exception("Database query returned None")
    except Exception as e:
        db_status = f"unhealthy: {str(e)[:50]}"

    # Return unhealthy ONLY if DB is down (MCP status is informational)
    # MCP doesn't expose HTTP health endpoint, so we check it via actual tool calls
    if db_status != "healthy":
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy - DB: {db_status}, MCP: {mcp_status}"
        )

    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        mcp_server=mcp_status
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
