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

# Add MCP server to Python path (needed for direct tool imports)
mcp_server_dir = backend_dir / "mcp-server"
if str(mcp_server_dir) not in sys.path:
    sys.path.insert(0, str(mcp_server_dir))

# CRITICAL: Set absolute database path BEFORE importing MCP tools
# The MCP server tools need to know where the SQLite database is located
db_path = backend_dir / "synthetic-data-gen" / "output" / "grabon_bnpl.db"
os.environ['DATABASE_PATH'] = str(db_path.absolute())
print(f"[DB] Database path configured: {os.environ['DATABASE_PATH']}")

# Now we can import with absolute imports
from api.config import settings
import uvicorn

if __name__ == "__main__":
    print("=" * 80)
    print("[API] Starting GrabOn BNPL API Server")
    print("=" * 80)
    print(f"[API] Backend directory: {backend_dir}")
    print(f"[API] Python path configured for absolute imports")
    print("=" * 80 + "\n")

    uvicorn.run(
        "api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
