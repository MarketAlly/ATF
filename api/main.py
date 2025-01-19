from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from pathlib import Path
from typing import List, Optional

from .models import FeedRequest, FeedResponse, ValidationRequest, ValidationResponse
from .routes import feeds, health, metrics
from ..security.security import SecurityManager

app = FastAPI(
    title="ATF Service",
    description="Algorithmic Transparency Feed Service API",
    version="1.0.0"
)

# Security setup
security = HTTPBearer()
security_manager = SecurityManager(Path("security/config.yaml"))

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
app.include_router(
    feeds.router,
    prefix="/feeds",
    tags=["feeds"],
    dependencies=[Depends(security)]
)

@app.middleware("http")
async def security_middleware(request, call_next):
    """Add security headers and handle rate limiting."""
    # Get client identifier
    client_id = request.headers.get("X-Client-ID", "anonymous")
    
    # Check rate limits
    if not security_manager.check_rate_limit(request.url.path, client_id):
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"}
        )
    
    # Process request
    response = await call_next(request)
    
    # Add security headers
    security_headers = security_manager.get_security_headers()
    for header, value in security_headers.items():
        response.headers[header] = value
    
    return response

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with audit logging."""
    security_manager.audit_log("http_error", {
        "path": request.url.path,
        "method": request.method,
        "status_code": exc.status_code,
        "detail": exc.detail
    })
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# Optional: Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logging.info("ATF Service starting up")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logging.info("ATF Service shutting down")