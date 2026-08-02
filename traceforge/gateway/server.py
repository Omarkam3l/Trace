"""FastAPI application factory for TraceForge HTTP Gateway."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import FastAPI

from traceforge.gateway.exceptions import register_exception_handlers
from traceforge.gateway.router import router

if TYPE_CHECKING:
    from traceforge.service.service import TraceForgeApiService


def create_app(service: TraceForgeApiService) -> FastAPI:
    """Create and configure a production FastAPI gateway application."""
    app = FastAPI(
        title="TraceForge API Gateway",
        description="Production read-only REST API gateway for TraceForge execution tracing.",
        version="0.13.0",
    )
    app.state.service = service
    register_exception_handlers(app)
    app.include_router(router)
    return app
