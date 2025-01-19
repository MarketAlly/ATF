from fastapi import APIRouter
from typing import Dict

router = APIRouter()

@router.get("")
async def health_check() -> Dict[str, str]:
    """Basic health check endpoint."""
    return {"status": "healthy"}

@router.get("/ready")
async def readiness_check() -> Dict[str, str]:
    """Readiness check endpoint."""
    # Add actual dependency checks here
    return {"status": "ready"}

@router.get("/live")
async def liveness_check() -> Dict[str, str]:
    """Liveness check endpoint."""
    return {"status": "alive"}