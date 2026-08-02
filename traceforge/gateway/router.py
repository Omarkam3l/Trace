"""FastAPI APIRouter for TraceForge HTTP Gateway."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query, Request, Response, status
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from traceforge.export.config import ExportConfig, ExportFormat
from traceforge.service.service import TraceForgeApiService


class DiffRequest(BaseModel):
    baseline_id: str
    target_id: str


class DiffExportRequest(BaseModel):
    baseline_id: str
    target_id: str
    format: str = "json"


def get_service(request: Request) -> TraceForgeApiService:
    """Dependency injecting TraceForgeApiService from app state."""
    return request.app.state.service


router = APIRouter(prefix="/api/v1", tags=["traceforge"])


@router.get("/sessions")
def list_sessions(service: TraceForgeApiService = Depends(get_service)) -> list[dict[str, Any]]:
    """List recorded execution sessions."""
    sessions = service.list_sessions()
    return [s.model_dump(mode="json") for s in sessions]


@router.get("/sessions/{session_id}")
def get_session(session_id: str, service: TraceForgeApiService = Depends(get_service)) -> dict[str, Any]:
    """Get a recorded session by ID."""
    session = service.get_session(session_id)
    return session.model_dump(mode="json")


@router.get("/sessions/{session_id}/replay")
def replay_session(session_id: str, service: TraceForgeApiService = Depends(get_service)) -> dict[str, Any]:
    """Reconstruct a complete replay session."""
    replay = service.replay_session(session_id)
    return replay.model_dump(mode="json")


@router.post("/diff")
def compare_sessions(req: DiffRequest, service: TraceForgeApiService = Depends(get_service)) -> dict[str, Any]:
    """Compare baseline and target sessions and return ExecutionDiffReport."""
    diff = service.compare_sessions(req.baseline_id, req.target_id)
    return diff.model_dump(mode="json")


@router.get("/sessions/{session_id}/export")
def export_session(
    session_id: str,
    fmt: str = Query("json", alias="format"),
    service: TraceForgeApiService = Depends(get_service),
) -> Response:
    """Export a session artifact in JSON, Mermaid, HTML, or Markdown."""
    export_fmt = ExportFormat(fmt.lower())
    content = service.export_session(session_id, config=ExportConfig(format=export_fmt))
    return PlainTextResponse(content=content)


@router.post("/diff/export")
def export_diff(req: DiffExportRequest, service: TraceForgeApiService = Depends(get_service)) -> Response:
    """Export an execution diff report."""
    export_fmt = ExportFormat(req.format.lower())
    content = service.export_diff(req.baseline_id, req.target_id, config=ExportConfig(format=export_fmt))
    return PlainTextResponse(content=content)


@router.get("/sessions/{session_id}/visualization/graph")
def get_graph_visualization(session_id: str, service: TraceForgeApiService = Depends(get_service)) -> dict[str, Any]:
    """Get Cytoscape/D3 GraphViewModel."""
    vm = service.get_graph_visualization(session_id)
    return vm.model_dump(mode="json")


@router.get("/sessions/{session_id}/visualization/timeline")
def get_timeline_visualization(session_id: str, service: TraceForgeApiService = Depends(get_service)) -> dict[str, Any]:
    """Get TimelineViewModel."""
    vm = service.get_timeline_visualization(session_id)
    return vm.model_dump(mode="json")


@router.get("/sessions/{session_id}/visualization/flamegraph")
def get_flamegraph_visualization(session_id: str, service: TraceForgeApiService = Depends(get_service)) -> dict[str, Any]:
    """Get FlamegraphViewModel."""
    vm = service.get_flamegraph_visualization(session_id)
    return vm.model_dump(mode="json")


@router.post("/diff/visualization")
def get_diff_visualization(req: DiffRequest, service: TraceForgeApiService = Depends(get_service)) -> dict[str, Any]:
    """Get DiffViewModel."""
    vm = service.get_diff_visualization(req.baseline_id, req.target_id)
    return vm.model_dump(mode="json")
