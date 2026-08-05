"""FastAPI application factory for TraceForge HTTP Gateway."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import FastAPI

from traceforge.gateway.exceptions import register_exception_handlers
from traceforge.gateway.router import router

if TYPE_CHECKING:
    from traceforge.service.service import TraceForgeApiService


import os
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles


def create_app(service: TraceForgeApiService) -> FastAPI:
    """Create and configure a production FastAPI gateway application."""
    app = FastAPI(
        title="TraceForge API Gateway",
        description="Production read-only REST API gateway for TraceForge execution tracing.",
        version="0.15.0",
    )
    app.state.service = service
    register_exception_handlers(app)
    app.include_router(router)

    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/", response_class=HTMLResponse)
    def index():
        index_path = os.path.join(static_dir, "index.html") if os.path.exists(static_dir) else None
        if index_path and os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                return f.read()
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>TraceForge Platform Dashboard</title>
    <style>
        body { font-family: system-ui, -apple-system, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 2rem; }
        .card { background: #1e293b; padding: 2rem; border-radius: 0.75rem; max-width: 800px; margin: 0 auto; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.5); }
        h1 { color: #38bdf8; margin-top: 0; }
        .badge { background: #0284c7; color: white; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.875rem; }
        a { color: #38bdf8; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="card">
        <h1>TraceForge Platform Dashboard <span class="badge">v0.15.0</span></h1>
        <p>Production Execution Replay & Analysis Platform running cleanly.</p>
        <h2>Available API Endpoints:</h2>
        <ul>
            <li><a href="/api/v1/sessions">GET /api/v1/sessions</a></li>
            <li><a href="/api/v1/health">GET /api/v1/health</a></li>
            <li><a href="/api/v1/status">GET /api/v1/status</a></li>
            <li><a href="/api/v1/metrics">GET /api/v1/metrics</a></li>
            <li><a href="/docs">OpenAPI Interactive Docs (/docs)</a></li>
        </ul>
    </div>
</body>
</html>"""

    return app
