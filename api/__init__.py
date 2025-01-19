"""
ATF (Algorithmic Transparency Feed) Service API.

This package provides the REST API for managing, validating,
and serving Algorithmic Transparency Feeds.
"""

__version__ = "1.0.0"
__author__ = "ATF Team"

from .models import (
    FeedRequest,
    FeedResponse,
    ValidationRequest,
    ValidationResponse,
    FeedComparison,
    MetricsResponse,
    ImpactAssessment
)

# Version compatibility check
import sys
if sys.version_info < (3, 8):
    raise RuntimeError("ATF Service requires Python 3.8 or higher")