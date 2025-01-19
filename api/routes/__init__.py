"""
ATF Service API route handlers.

This package contains the route handlers for:
- Feed management
- Health checks
- Metrics collection
"""

from . import feeds
from . import health
from . import metrics

# Export all route handlers
__all__ = ['feeds', 'health', 'metrics']

# Common response codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_400_BAD_REQUEST = 400
HTTP_401_UNAUTHORIZED = 401
HTTP_403_FORBIDDEN = 403
HTTP_404_NOT_FOUND = 404
HTTP_429_TOO_MANY_REQUESTS = 429
HTTP_500_INTERNAL_SERVER_ERROR = 500

# Common error messages
ERR_RATE_LIMIT = "Rate limit exceeded"
ERR_INVALID_TOKEN = "Invalid authentication token"
ERR_FEED_NOT_FOUND = "Feed not found"
ERR_VALIDATION_FAILED = "Feed validation failed"
ERR_INVALID_SIGNATURE = "Invalid feed signature"