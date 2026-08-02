"""Authentication middleware for FastAPI."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from traceforge.security.auth.provider import AuthProvider
from traceforge.security.exceptions import AuthenticationError


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Extracts Authorization header, validates credentials, attaches user to request state."""

    def __init__(self, app, auth_provider: AuthProvider) -> None:  # noqa: ANN001
        super().__init__(app)
        self._auth_provider = auth_provider

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
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
