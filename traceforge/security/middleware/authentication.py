"""Authentication middleware for FastAPI."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from traceforge.security.auth.provider import AuthProvider
from traceforge.security.exceptions import AuthenticationError

# Endpoints that must stay reachable without credentials — orchestrators,
# load balancers, and monitoring tools hit these before any auth is set up.
DEFAULT_EXEMPT_PATHS: frozenset[str] = frozenset(
    {
        "/health",
        "/ready",
        "/version",
        "/metrics",
        "/api/v1/health",
        "/api/v1/ready",
        "/api/v1/status",
        "/api/v1/metrics",
        "/",
        "/dashboard",
        "/docs",
        "/openapi.json",
    }
)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Extracts Authorization header, validates credentials, attaches user to request state."""

    def __init__(
        self,
        app,
        auth_provider: AuthProvider,
        exempt_paths: frozenset[str] = DEFAULT_EXEMPT_PATHS,
    ) -> None:
        super().__init__(app)
        self._auth_provider = auth_provider
        self._exempt_paths = exempt_paths

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in self._exempt_paths or request.url.path.startswith("/static"):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(
                status_code=401,
                content={"error": {"type": "AuthenticationError", "message": "Missing Authorization header"}},
            )

        try:
            user = self._auth_provider.authenticate(auth_header)
        except AuthenticationError as exc:
            return JSONResponse(
                status_code=401,
                content={"error": {"type": "AuthenticationError", "message": str(exc)}},
            )

        request.state.user = user
        return await call_next(request)
