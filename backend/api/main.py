"""
GrabOn BNPL FastAPI Server
Production-grade REST API for BNPL checkout integration.

Usage:
    uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from config import settings
from routes import checkout, health

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="GrabOn BNPL Credit Eligibility API - Powered by Poonawalla Fincorp",
    docs_url="/docs",
    redoc_url="/redoc"
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


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    print("=" * 80)
    print(f"{settings.APP_NAME} v{settings.APP_VERSION}")
    print("=" * 80)
    print(f"Server: http://{settings.HOST}:{settings.PORT}")
    print(f"Docs: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"MCP Server: {settings.MCP_SERVER_URL}")
    print("=" * 80)
    print("\nEndpoints:")
    print("  POST /api/checkout/eligibility - Check BNPL eligibility")
    print("  GET  /health - Health check")
    print("  GET  /docs - API documentation")
    print("\nReady to accept requests!")
    print("=" * 80 + "\n")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    from services.mcp_client import get_mcp_client
    mcp = get_mcp_client()
    await mcp.close()
    print("\nServer shutdown complete.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
