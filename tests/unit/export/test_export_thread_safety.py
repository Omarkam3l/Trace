"""Unit tests for multi-threaded concurrent ExportEngine operations."""

from __future__ import annotations

import concurrent.futures
from datetime import datetime, timezone

from traceforge.export.engine import ExportEngine
from traceforge.replay.session import ReplaySession
from traceforge.storage.records import SessionRecord


def test_concurrent_export_engine_exports():
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

    engine = ExportEngine()

    def worker_export(worker_id: int):
        res = engine.export_session(session)
        assert '"session_id": "s1"' in res

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(worker_export, i) for i in range(10)]
        concurrent.futures.wait(futures)
