"""Unit tests for MarkdownExporter."""

from __future__ import annotations

from datetime import datetime, timezone

from traceforge.export.config import ExportConfig
from traceforge.export.exporters.markdown_exporter import MarkdownExporter
from traceforge.replay.session import ReplaySession
from traceforge.storage.records import SessionRecord


def test_markdown_exporter():
    now = datetime.now(timezone.utc)
    sess_rec = SessionRecord(
        session_id="s1",
        started_at=now,
        status="completed",
        environment_os="win32",
        environment_python="3.13",
        profile_name="standard",
    )
    session = ReplaySession(session=sess_rec)

    exporter = MarkdownExporter()
    md = exporter.export_session(session, ExportConfig())
    assert "# TraceForge Replay Session: `s1`" in md
