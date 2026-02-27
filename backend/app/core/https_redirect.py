"""
Cura3.ai — HTTPS Redirect Middleware
Enforces HTTPS in production by redirecting HTTP requests to HTTPS.
Respects the X-Forwarded-Proto header set by Azure / load balancers.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """
    Redirect all HTTP requests to HTTPS in production.
    Checks the X-Forwarded-Proto header (set by reverse proxies / Azure)
    and the actual request scheme.
    """

    # Paths exempt from redirect (health checks, etc.)
    _EXEMPT_PATHS = frozenset({"/health", "/", "/docs", "/openapi.json"})

    async def dispatch(self, request: Request, call_next):
        # Determine the actual scheme (behind a proxy, X-Forwarded-Proto is set)
        proto = request.headers.get("x-forwarded-proto", request.url.scheme)

        if proto == "http" and request.url.path not in self._EXEMPT_PATHS:
            # Build HTTPS URL
            https_url = str(request.url).replace("http://", "https://", 1)
            return RedirectResponse(url=https_url, status_code=301)

        return await call_next(request)
