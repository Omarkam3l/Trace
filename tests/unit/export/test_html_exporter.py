"""Unit tests for HtmlExporter."""

from __future__ import annotations

from datetime import UTC, datetime

from traceforge.export.config import ExportConfig
from traceforge.export.exporters.html_exporter import HtmlExporter
from traceforge.replay.session import ReplaySession
from traceforge.storage.records import SessionRecord


def test_html_exporter():
    now = datetime.now(UTC)
    sess_rec = SessionRecord(
        session_id="s1",
        started_at=now,
        status="completed",
        environment_os="win32",
        environment_python="3.13",
        profile_name="standard",
    )
    session = ReplaySession(session=sess_rec)

    exporter = HtmlExporter()
    html = exporter.export_session(session, ExportConfig())
    assert "<!DOCTYPE html>" in html
    assert "TraceForge Execution Report: s1" in html
