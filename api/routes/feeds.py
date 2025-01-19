from fastapi import APIRouter, HTTPException, Security, Depends
from fastapi.security import HTTPBearer
from typing import List, Optional
import uuid
from datetime import datetime

from ..models import (
    FeedRequest,
    FeedResponse,
    ValidationRequest,
    ValidationResponse,
    FeedComparison
)
from ...tools.feed_generator import ATFGenerator
from ...tools.validator import ATFValidator
from ...tools.feed_manager import FeedManager
from ...security.security import SecurityManager

router = APIRouter()
security = HTTPBearer()

@router.post("/", response_model=FeedResponse)
async def create_feed(request: FeedRequest):
    """Create a new ATF feed."""
    try:
        # Generate feed
        generator = ATFGenerator()
        feed_content = generator.create_feed(
            title=request.title,
            link=str(request.link),
            description=request.description
        )
        
        # Add items
        for item in request.items:
            generator.add_item(feed_content, item)
        
        # Sign feed
        security_manager = SecurityManager("security/config.yaml")
        signature = security_manager.sign_feed(str(feed_content))
        
        return FeedResponse(
            id=str(uuid.uuid4()),
            content=str(feed_content),
            signature=signature,
            created_at=datetime.utcnow(),
            version=request.version
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/validate", response_model=ValidationResponse)
async def validate_feed(request: ValidationRequest):
    """Validate an ATF feed."""
    try:
        validator = ATFValidator("schema/atf-1.0.xsd")
        errors = validator.validate_feed(request.content)
        
        if request.signature:
            security_manager = SecurityManager("security/config.yaml")
            if not security_manager.verify_feed(request.content, request.signature):
                errors.append("Invalid feed signature")
        
        return ValidationResponse(
            is_valid=len(errors) == 0,
            errors=[{"code": "VALIDATION_ERROR", "message": err} for err in errors]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/compare", response_model=FeedComparison)
async def compare_feeds(feed1: str, feed2: str):
    """Compare two ATF feeds."""
    try:
        manager = FeedManager("workspace")
        comparison = manager.compare_feeds(feed1, feed2)
        return comparison
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{feed_id}", response_model=FeedResponse)
async def get_feed(feed_id: str):
    """Retrieve a specific feed."""
    # Implementation would typically fetch from storage
    raise HTTPException(status_code=404, detail="Feed not found")

@router.put("/{feed_id}", response_model=FeedResponse)
async def update_feed(feed_id: str, request: FeedRequest):
    """Update an existing feed."""
    # Implementation would typically update in storage
    raise HTTPException(status_code=404, detail="Feed not found")

@router.delete("/{feed_id}")
async def delete_feed(feed_id: str):
    """Delete a feed."""
    # Implementation would typically delete from storage
    raise HTTPException(status_code=404, detail="Feed not found")