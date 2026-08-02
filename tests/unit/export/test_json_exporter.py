"""Unit tests for JsonExporter."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from traceforge.export.config import ExportConfig
from traceforge.export.exporters.json_exporter import JsonExporter
from traceforge.replay.session import ReplaySession
from traceforge.storage.records import SessionRecord


def test_json_exporter():
    now = datetime.now(timezone.utc)
    sess_rec = SessionRecord(session_id="s1", started_at=now, status="completed", environment_os="win32", environment_python="3.13", profile_name="standard")
    session = ReplaySession(session=sess_rec)

    exporter = JsonExporter()
    out = exporter.export_session(session, ExportConfig(pretty_print=True))

    data = json.loads(out)
    assert data["session"]["session_id"] == "s1"
