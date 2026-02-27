"""
Cura3.ai — Rate Limiting Middleware
Simple in-memory rate limiter using sliding window.
"""
import time
from collections import defaultdict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimiter:
    """Sliding window rate limiter."""

    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    def _get_key(self, request: Request) -> str:
        """Get a unique key for the client."""
        # Use authorization header (user) or IP address
        auth = request.headers.get("authorization", "")
        if auth:
            return f"auth:{auth[:50]}"
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"
        return f"ip:{request.client.host if request.client else 'unknown'}"

    def is_rate_limited(self, key: str) -> bool:
        """Check if the key is rate-limited."""
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old entries
        self._requests[key] = [
            t for t in self._requests[key] if t > window_start
        ]

        if len(self._requests[key]) >= self.max_requests:
            return True

        self._requests[key].append(now)
        return False

    def get_remaining(self, key: str) -> int:
        """Get remaining requests for the key."""
        now = time.time()
        window_start = now - self.window_seconds
        active = [t for t in self._requests[key] if t > window_start]
        return max(0, self.max_requests - len(active))


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware that applies rate limiting."""

    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.limiter = RateLimiter(max_requests, window_seconds)

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks and static files
        path = request.url.path
        if path in ("/", "/health", "/docs", "/redoc", "/openapi.json"):
            return await call_next(request)

        key = self.limiter._get_key(request)

        if self.limiter.is_rate_limited(key):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
                headers={"Retry-After": str(self.limiter.window_seconds)},
            )

        response = await call_next(request)

        # Add rate limit headers
        remaining = self.limiter.get_remaining(key)
        response.headers["X-RateLimit-Limit"] = str(self.limiter.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)

        return response
