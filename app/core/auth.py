"""
API Key authentication module for securing API endpoints.
"""
import os
import secrets
from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader, APIKeyQuery
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import hashlib

from app.core.database import get_db
from app.core.logging import get_logger

logger = get_logger(__name__)

# API Key configuration
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)


class APIKeyManager:
    """Manages API keys for authentication."""
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate a new API key."""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash an API key for secure storage."""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    @staticmethod
    def verify_api_key(api_key: str, hashed_key: str) -> bool:
        """Verify an API key against its hash."""
        return APIKeyManager.hash_api_key(api_key) == hashed_key


async def get_api_key(
    api_key_header: str = Security(api_key_header),
    api_key_query: str = Security(api_key_query),
) -> str:
    """
    Validate API key from header or query parameter.
    
    Priority:
    1. Header (X-API-Key)
    2. Query parameter (api_key)
    
    Returns:
        str: The validated API key
        
    Raises:
        HTTPException: If no valid API key is provided
    """
    # Check header first
    if api_key_header:
        return await validate_api_key(api_key_header)
    
    # Check query parameter
    if api_key_query:
        return await validate_api_key(api_key_query)
    
    # No API key provided
    logger.warning("No API key provided in request")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="API key required. Please provide it in the X-API-Key header or api_key query parameter.",
    )


async def validate_api_key(api_key: str) -> str:
    """
    Validate the provided API key.
    
    For now, this checks against environment variables.
    In production, this should check against a database of valid API keys.
    
    Args:
        api_key: The API key to validate
        
    Returns:
        str: The validated API key
        
    Raises:
        HTTPException: If the API key is invalid
    """
    # Get valid API keys from environment
    valid_api_keys = []
    
    # Check for a master API key in environment
    master_key = os.getenv("MASTER_API_KEY")
    if master_key:
        valid_api_keys.append(master_key)
    
    # Check for additional API keys (comma-separated)
    additional_keys = os.getenv("API_KEYS", "").split(",")
    valid_api_keys.extend([key.strip() for key in additional_keys if key.strip()])
    
    # In development, allow a default key if no keys are configured
    if not valid_api_keys and os.getenv("ENVIRONMENT", "development") == "development":
        logger.warning("No API keys configured, using default development key")
        valid_api_keys.append("development-api-key-please-change-in-production")
    
    # Validate the provided key
    if api_key in valid_api_keys:
        logger.info(f"Valid API key used: {api_key[:8]}...")
        return api_key
    
    logger.warning(f"Invalid API key attempted: {api_key[:8]}...")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key",
    )


class RateLimiter:
    """Simple in-memory rate limiter for API keys."""
    
    def __init__(self):
        self.requests = {}
        self.window_size = timedelta(minutes=1)
        self.max_requests = 100
    
    def check_rate_limit(self, api_key: str) -> bool:
        """
        Check if the API key has exceeded the rate limit.
        
        Args:
            api_key: The API key to check
            
        Returns:
            bool: True if within rate limit, False if exceeded
        """
        now = datetime.now()
        
        # Clean up old entries
        self._cleanup_old_entries(now)
        
        # Check current request count
        if api_key not in self.requests:
            self.requests[api_key] = []
        
        # Count requests in the current window
        request_count = len(self.requests[api_key])
        
        if request_count >= self.max_requests:
            return False
        
        # Add current request
        self.requests[api_key].append(now)
        return True
    
    def _cleanup_old_entries(self, now: datetime):
        """Remove entries older than the window size."""
        cutoff_time = now - self.window_size
        
        for api_key in list(self.requests.keys()):
            self.requests[api_key] = [
                timestamp for timestamp in self.requests[api_key]
                if timestamp > cutoff_time
            ]
            
            # Remove empty entries
            if not self.requests[api_key]:
                del self.requests[api_key]


# Global rate limiter instance
rate_limiter = RateLimiter()


async def get_api_key_with_rate_limit(
    api_key: str = Security(get_api_key),
) -> str:
    """
    Get API key with rate limiting.
    
    Args:
        api_key: The API key from the security dependency
        
    Returns:
        str: The validated API key
        
    Raises:
        HTTPException: If rate limit is exceeded
    """
    if not rate_limiter.check_rate_limit(api_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
        )
    
    return api_key


# Optional: Dependency for endpoints that require specific permissions
async def require_admin_key(api_key: str = Security(get_api_key)) -> str:
    """
    Require an admin API key for sensitive operations.
    
    Args:
        api_key: The API key from the security dependency
        
    Returns:
        str: The validated admin API key
        
    Raises:
        HTTPException: If the API key doesn't have admin permissions
    """
    admin_keys = os.getenv("ADMIN_API_KEYS", "").split(",")
    admin_keys = [key.strip() for key in admin_keys if key.strip()]
    
    if api_key not in admin_keys:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    
    return api_key