"""Unit tests for ExportEngine workflow and format routing."""

from __future__ import annotations

from datetime import datetime, timezone

from traceforge.export.config import ExportConfig, ExportFormat
from traceforge.export.engine import ExportEngine
from traceforge.replay.session import ReplaySession
from traceforge.storage.records import NodeRecord, SessionRecord


def test_export_engine_session_export():
    now = datetime.now(timezone.utc)
    sess_rec = SessionRecord(
        session_id="s1",
        started_at=now,
        status="completed",
        environment_os="win32",
        environment_python="3.13",
        profile_name="standard",
    )
    n1 = NodeRecord(node_id="n1", graph_id="g1", type="function", name="main", started_at=now, status="completed")

    session = ReplaySession(session=sess_rec, nodes=[n1])
    engine = ExportEngine()

    json_res = engine.export_session(session, ExportConfig(format=ExportFormat.JSON))
    assert '"session_id": "s1"' in json_res

    mermaid_res = engine.export_session(session, ExportConfig(format=ExportFormat.MERMAID))
    assert "flowchart TD" in mermaid_res
    assert 'n1["main (function)"]' in mermaid_res

    html_res = engine.export_session(session, ExportConfig(format=ExportFormat.HTML))
    assert "<!DOCTYPE html>" in html_res
    assert "s1" in html_res

    md_res = engine.export_session(session, ExportConfig(format=ExportFormat.MARKDOWN))
    assert "# TraceForge Replay Session: `s1`" in md_res
