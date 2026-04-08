"""
GrabOn BNPL API Server Launcher
Properly sets up Python path and starts the FastAPI server.

Usage:
    python run.py
"""

import sys
import os
from pathlib import Path

# Add backend directory to Python path for absolute imports
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Now we can import with absolute imports
from api.config import settings
import uvicorn

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 Starting GrabOn BNPL API Server")
    print("=" * 80)
    print(f"📁 Backend directory: {backend_dir}")
    print(f"🐍 Python path configured for absolute imports")
    print("=" * 80 + "\n")

    uvicorn.run(
        "api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
