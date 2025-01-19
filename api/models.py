from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class FeedVersion(str, Enum):
    """ATF feed version enumeration."""
    V1_0 = "1.0"

class ImpactMetric(BaseModel):
    """Impact assessment metric."""
    name: str
    value: str
    description: Optional[str] = None

class ImpactAssessment(BaseModel):
    """Impact assessment details."""
    summary: str
    affected_users: str
    metrics: Optional[Dict[str, str]] = None
    risks: Optional[List[str]] = None
    mitigations: Optional[List[str]] = None

class FeedItem(BaseModel):
    """Individual feed item."""
    title: str
    link: HttpUrl
    pub_date: datetime
    description: str
    categories: List[str]
    impact_assessment: ImpactAssessment

class FeedRequest(BaseModel):
    """Request to create or update a feed."""
    title: str
    link: HttpUrl
    description: str
    items: List[FeedItem]
    version: FeedVersion = FeedVersion.V1_0

class FeedResponse(BaseModel):
    """Response containing feed details."""
    id: str
    content: str
    signature: str
    created_at: datetime
    version: FeedVersion

class ValidationError(BaseModel):
    """Validation error details."""
    code: str
    message: str
    location: Optional[str] = None

class ValidationRequest(BaseModel):
    """Request to validate a feed."""
    content: str
    signature: Optional[str] = None

class ValidationResponse(BaseModel):
    """Response containing validation results."""
    is_valid: bool
    errors: Optional[List[ValidationError]] = None

class FeedComparison(BaseModel):
    """Feed comparison results."""
    added_items: List[str]
    removed_items: List[str]
    modified_items: List[Dict]

class MetricsResponse(BaseModel):
    """Service metrics response."""
    feeds_total: int
    validations_total: int
    error_rate: float
    avg_response_time: float