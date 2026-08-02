"""HTTP Gateway Layer exception handlers for FastAPI."""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from traceforge.service.exceptions import ApiServiceError, ServiceNotFoundError


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers on FastAPI application instance."""

    @app.exception_handler(ServiceNotFoundError)
    async def not_found_handler(request: Request, exc: ServiceNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc), "error_type": "NotFoundError"},
        )

    @app.exception_handler(ApiServiceError)
    async def api_service_error_handler(request: Request, exc: ApiServiceError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc), "error_type": "ApiServiceError"},
        )
