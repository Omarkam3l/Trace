"""Standalone live trace-viewer dashboard app — reserved for a future release.

This is planned to be a separate, richer FastAPI + React application with
real-time push via WebSocketExporter. Per the current SDK-core milestone,
that standalone app is explicitly out of scope, so this package ships only
as a placeholder. See docs/roadmap.md.

This is NOT the only dashboard TraceForge has. A working, lighter-weight
trace viewer already exists today: `GET /dashboard` on the HTTP gateway
(`traceforge server`), served from `traceforge/gateway/static/index.html`.
It lists recorded sessions with live polling, renders a flamegraph per
session, and surfaces exception details for failed traces -- no dependency
on this package. If you're looking for "the dashboard," that one is real
and running; this package is reserved for a future, separate, more
ambitious standalone app.
"""
