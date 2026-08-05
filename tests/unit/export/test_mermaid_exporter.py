"""Unit tests for MermaidExporter."""

from __future__ import annotations

from datetime import datetime, timezone

from traceforge.export.config import ExportConfig
from traceforge.export.exporters.mermaid_exporter import MermaidExporter
from traceforge.replay.session import ReplaySession
from traceforge.storage.records import NodeRecord, RelationshipRecord, SessionRecord


def test_mermaid_exporter():
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
    n2 = NodeRecord(node_id="n2", graph_id="g1", type="function", name="helper", started_at=now, status="completed")
    rel = RelationshipRecord(
        relationship_id="r1", graph_id="g1", source_node_id="n1", target_node_id="n2", type="parent_child"
    )

    session = ReplaySession(session=sess_rec, nodes=[n1, n2], relationships=[rel])
    exporter = MermaidExporter()

    mermaid = exporter.export_session(session, ExportConfig())
    assert "flowchart TD" in mermaid
    assert "n1 -->|parent_child| n2" in mermaid
