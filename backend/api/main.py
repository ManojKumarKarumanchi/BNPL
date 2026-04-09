"""
GrabOn BNPL FastAPI Server
Production-grade REST API for BNPL checkout integration.

Usage:
    # From backend directory (RECOMMENDED):
    python run.py

    # OR using uvicorn directly:
    cd backend && uvicorn api.main:app --reload --port 8000

    # OR using start.bat:
    cd backend/api && start.bat
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.config import settings
from api.routes import checkout, health
import sys
from pathlib import Path

# Add backend root to path for shared_logging import
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

from shared_logging import setup_logging, log_section_separator

# Initialize centralized logger for API server
logger = setup_logging("api-server", level="INFO")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for startup and shutdown.
    Replaces deprecated @app.on_event decorators.
    """
    # Startup
    log_section_separator(logger, "API SERVER STARTUP")
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Server: http://{settings.HOST}:{settings.PORT}")
    logger.info(f"Docs: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info(f"MCP Server: {settings.MCP_SERVER_URL}")
    logger.info(f"PayU Mode: {'MOCK' if settings.PAYU_MERCHANT_KEY == 'gtKFFx' else 'REAL SANDBOX'}")
    logger.info("")
    logger.info("Endpoints:")
    logger.info("  POST /api/checkout/eligibility - Check BNPL eligibility")
    logger.info("  GET  /health - Health check")
    logger.info("  GET  /docs - API documentation")
    logger.info("")
    logger.info("[READY] Server ready to accept requests")
    log_section_separator(logger, "")

    yield

    # Shutdown
    log_section_separator(logger, "API SERVER SHUTDOWN")
    from api.services.mcp_client import get_mcp_client
    mcp = get_mcp_client()
    await mcp.close()
    logger.info("[SHUTDOWN] MCP client closed")
    logger.info("[SHUTDOWN] API server shutdown complete")
    print("\nServer shutdown complete.")


# Initialize FastAPI app with lifespan handler
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="GrabOn BNPL Credit Eligibility API - Powered by Poonawalla Fincorp",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health.router)
app.include_router(checkout.router, prefix="/api")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle uncaught exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


if __name__ == "__main__":
    print("[WARNING] Direct execution not recommended!")
    print("Please use: cd backend && python run.py")
    print("Or run: cd backend && uvicorn api.main:app --reload")
    import sys
    sys.exit(1)
