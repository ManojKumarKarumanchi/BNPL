# Environment Variables Migration

## Summary

All hardcoded values have been replaced with environment variables across the codebase. This document explains what changed and how to configure your environment.

---

## Changes Made

### 1. **FastAPI Deprecation Fixed** ✅

**File:** `backend/api/main.py`

**Issue:** FastAPI's `@app.on_event("startup")` and `@app.on_event("shutdown")` decorators are deprecated.

**Solution:** Replaced with modern `lifespan` event handler using `@asynccontextmanager`.

**Before:**
```python
@app.on_event("startup")
async def startup_event():
    # Startup code
    
@app.on_event("shutdown")
async def shutdown_event():
    # Shutdown code
```

**After:**
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    yield
    # Shutdown code

app = FastAPI(..., lifespan=lifespan)
```

---

### 2. **Backend API Configuration** (`backend/api/config.py`)

**Hardcoded → Environment Variables:**

| Setting | Old Value | New Value | Env Var |
|---------|-----------|-----------|---------|
| APP_NAME | `"GrabOn BNPL API"` | `os.getenv("APP_NAME", "GrabOn BNPL API")` | `APP_NAME` |
| APP_VERSION | `"1.0.0"` | `os.getenv("APP_VERSION", "1.0.0")` | `APP_VERSION` |
| DEBUG | `True` | `os.getenv("DEBUG", "true").lower() == "true"` | `DEBUG` |
| HOST | `"0.0.0.0"` | `os.getenv("HOST", "0.0.0.0")` | `HOST` |
| PORT | `8000` | `int(os.getenv("PORT", "8000"))` | `PORT` |
| CORS_ORIGINS | `["http://localhost:3000", ...]` | `os.getenv("CORS_ORIGINS", "...").split(",")` | `CORS_ORIGINS` |
| MCP_SERVER_URL | `"http://localhost:8001"` | `os.getenv("MCP_SERVER_URL", "http://localhost:8001")` | `MCP_SERVER_URL` |
| JWT_SECRET_KEY | `"your-secret-key..."` | `os.getenv("JWT_SECRET_KEY", "...")` | `JWT_SECRET_KEY` |
| JWT_ALGORITHM | `"HS256"` | `os.getenv("JWT_ALGORITHM", "HS256")` | `JWT_ALGORITHM` |
| JWT_EXPIRATION_HOURS | `24` | `int(os.getenv("JWT_EXPIRATION_HOURS", "24"))` | `JWT_EXPIRATION_HOURS` |
| RATE_LIMIT_PER_MINUTE | `60` | `int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))` | `RATE_LIMIT_PER_MINUTE` |
| RATE_LIMIT_PER_HOUR | `500` | `int(os.getenv("RATE_LIMIT_PER_HOUR", "500"))` | `RATE_LIMIT_PER_HOUR` |
| PAYU_SANDBOX_URL | `"https://test.payu.in"` | `os.getenv("PAYU_SANDBOX_URL", "https://test.payu.in")` | `PAYU_SANDBOX_URL` |
| PAYU_MODE | `"sandbox"` | `os.getenv("PAYU_MODE", "sandbox")` | `PAYU_MODE` |
| AI_PROVIDER | `"claude"` | `os.getenv("AI_PROVIDER", "claude")` | `AI_PROVIDER` |

**Note:** CORS_ORIGINS now supports comma-separated list via environment variable:
```bash
CORS_ORIGINS="http://localhost:3000,http://localhost:5173,https://production.com"
```

---

### 3. **PayU Client Configuration** (`backend/api/services/payu_client.py`)

**Line 30:**

**Before:**
```python
self.base_url = "https://test.payu.in"  # Hardcoded
```

**After:**
```python
self.base_url = settings.PAYU_SANDBOX_URL  # Uses environment variable
```

Now controlled by `PAYU_SANDBOX_URL` environment variable.

---

### 4. **MCP Server Configuration** (`backend/mcp-server/config.py`)

**Hardcoded → Environment Variables:**

| Setting | Old Value | New Value | Env Var |
|---------|-----------|-----------|---------|
| MCP_SERVER_NAME | `"grabon-bnpl-mcp"` | `os.getenv("MCP_SERVER_NAME", "grabon-bnpl-mcp")` | `MCP_SERVER_NAME` |
| MCP_SERVER_VERSION | `"1.0.0"` | `os.getenv("MCP_SERVER_VERSION", "1.0.0")` | `MCP_SERVER_VERSION` |
| MCP_SERVER_PORT | `8001` | `int(os.getenv("MCP_SERVER_PORT", "8001"))` | `MCP_SERVER_PORT` |
| CLAUDE_MODEL | `"claude-sonnet-4-5"` | `os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")` | `CLAUDE_MODEL` |

**Already using environment variables (no change needed):**
- `DATABASE_PATH` ✅
- `AI_PROVIDER` ✅
- `ANTHROPIC_API_KEY` ✅
- `AZURE_AI_PROJECT_ENDPOINT` ✅
- `AZURE_AI_MODEL_DEPLOYMENT_NAME` ✅
- `AZURE_API_KEY` ✅
- `AZURE_API_VERSION` ✅
- `LOG_LEVEL` ✅
- `LOG_FILE` ✅

---

### 5. **Synthetic Data Generator Configuration** (`backend/synthetic-data-gen/config.py`)

**Line 204:**

**Before:**
```python
DB_PATH = "C:/Users/ManojKumarKarumanchi/local/BNPL/backend/synthetic-data-gen/output/grabon_bnpl.db"
```

**After:**
```python
import os
from pathlib import Path

DB_PATH = os.getenv(
    "DATABASE_PATH",
    str(Path(__file__).parent / "output" / "grabon_bnpl.db")
)
```

Now uses relative path by default and can be overridden with `DATABASE_PATH` environment variable.

---

### 6. **Frontend Configuration** (`frontend/src/services/api.js`)

**Already using environment variables correctly:**

```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
```

**Environment Variables:**
- `VITE_API_BASE_URL` - Backend API URL
- `VITE_SHOW_PERSONA_SWITCHER` - Show/hide debug persona switcher

---

## Environment Files Created

### 1. **Backend** (`backend/.env.example`)

Created comprehensive `.env.example` file with all environment variables documented.

**Usage:**
```bash
cd backend
cp .env.example .env
# Edit .env with your values
```

### 2. **Frontend** (`frontend/.env`)

Already documented in `frontend/README.md`. Create `.env` file:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_SHOW_PERSONA_SWITCHER=false
```

---

## Configuration Guide

### Development Setup

1. **Backend Configuration:**
   ```bash
   cd backend
   cp .env.example .env
   ```

2. **Edit `backend/.env`:**
   - Set `DEBUG=true`
   - Set `ANTHROPIC_API_KEY` if using Claude
   - Keep `PAYU_ENABLED=false` for development

3. **Frontend Configuration:**
   ```bash
   cd frontend
   # Create .env file
   echo "VITE_API_BASE_URL=http://localhost:8000" > .env
   echo "VITE_SHOW_PERSONA_SWITCHER=true" >> .env
   ```

### Production Setup

1. **Backend `.env`:**
   ```bash
   DEBUG=false
   HOST=0.0.0.0
   PORT=8000
   CORS_ORIGINS=https://your-production-domain.com
   JWT_SECRET_KEY=<generate-strong-random-key>
   ANTHROPIC_API_KEY=<your-production-key>
   PAYU_ENABLED=true
   PAYU_MERCHANT_KEY=<production-merchant-key>
   PAYU_MERCHANT_SALT=<production-merchant-salt>
   PAYU_MODE=production
   PAYU_SANDBOX_URL=https://secure.payu.in
   ```

2. **Frontend `.env`:**
   ```bash
   VITE_API_BASE_URL=https://api.your-production-domain.com
   VITE_SHOW_PERSONA_SWITCHER=false
   ```

---

## Testing Changes

### 1. **FastAPI Lifespan**

Start the backend and verify no deprecation warnings:

```bash
cd backend
python run.py
```

**Expected output:**
```
================================================================================
GrabOn BNPL API v1.0.0
================================================================================
Server: http://0.0.0.0:8000
Docs: http://0.0.0.0:8000/docs
MCP Server: http://localhost:8001
================================================================================

Endpoints:
  POST /api/checkout/eligibility - Check BNPL eligibility
  GET  /health - Health check
  GET  /docs - API documentation

Ready to accept requests!
================================================================================
```

**No warnings about deprecated `on_event`** ✅

### 2. **Environment Variables**

Test environment variable overrides:

```bash
# Test custom port
PORT=9000 python run.py

# Test custom MCP server URL
MCP_SERVER_URL=http://localhost:9001 python run.py

# Test custom CORS origins
CORS_ORIGINS="http://localhost:3000,https://myapp.com" python run.py
```

### 3. **Database Path**

Test custom database path:

```bash
# In synthetic-data-gen
DATABASE_PATH=/tmp/test.db python main.py

# In MCP server
DATABASE_PATH=/tmp/test.db python server.py
```

---

## Migration Checklist

- [x] Replace `@app.on_event` with `lifespan` in FastAPI
- [x] Move all hardcoded values in `backend/api/config.py` to environment variables
- [x] Fix hardcoded PayU URL in `payu_client.py`
- [x] Move MCP server hardcoded values to environment variables
- [x] Fix absolute database path in synthetic-data-gen
- [x] Create `backend/.env.example` with all variables documented
- [x] Document frontend environment variables (already in README)
- [x] Test all changes work with defaults
- [x] Test environment variable overrides work

---

## Environment Variable Reference

### Backend API (`backend/api/.env`)

```bash
# Server
APP_NAME=GrabOn BNPL API
APP_VERSION=1.0.0
DEBUG=true
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# MCP
MCP_SERVER_URL=http://localhost:8001

# Security
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=500

# PayU
PAYU_ENABLED=false
PAYU_SANDBOX_URL=https://test.payu.in
PAYU_MERCHANT_KEY=gtKFFx
PAYU_MERCHANT_SALT=4R38IvwiV57FwVpsgOvTXBdLE4tHUXFW
PAYU_MODE=sandbox
API_BASE_URL=http://localhost:8000

# AI
AI_PROVIDER=claude
ANTHROPIC_API_KEY=your_key_here
CLAUDE_MODEL=claude-sonnet-4-5
```

### MCP Server (`backend/mcp-server/.env`)

```bash
# MCP Server
MCP_SERVER_NAME=grabon-bnpl-mcp
MCP_SERVER_VERSION=1.0.0
MCP_SERVER_PORT=8001

# Database
DATABASE_PATH=../synthetic-data-gen/output/grabon_bnpl.db

# AI
AI_PROVIDER=claude
ANTHROPIC_API_KEY=your_key_here
CLAUDE_MODEL=claude-sonnet-4-5

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/mcp-server.log
```

### Frontend (`frontend/.env`)

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_SHOW_PERSONA_SWITCHER=false
```

---

## Benefits of This Migration

1. **Security:** Sensitive values (API keys, secrets) not hardcoded
2. **Flexibility:** Easy to change configuration per environment
3. **12-Factor App:** Follows best practices for cloud deployment
4. **Team Collaboration:** Each developer can have their own `.env` without conflicts
5. **Production Ready:** Can deploy to different environments with same code
6. **No Deprecation Warnings:** Modern FastAPI lifespan event handlers

---

## Troubleshooting

### Issue: "Environment variable not loaded"

**Solution:** Ensure `.env` file is in the correct directory:
- Backend API: `backend/.env` OR `backend/api/.env`
- MCP Server: `backend/mcp-server/.env`
- Frontend: `frontend/.env`

### Issue: "CORS error in browser"

**Solution:** Update `CORS_ORIGINS` in `backend/.env`:
```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Issue: "MCP server not found"

**Solution:** Ensure `MCP_SERVER_URL` matches where MCP server is running:
```bash
# In backend/.env
MCP_SERVER_URL=http://localhost:8001
```

---

## Next Steps

1. Create `.env` files based on `.env.example`
2. Test the application with environment variables
3. For production: Generate strong `JWT_SECRET_KEY` and set proper API keys
4. Deploy with environment-specific configuration

