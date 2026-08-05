"""Integration and determinism tests for Phase 2 Recording Engine."""

from __future__ import annotations

import asyncio
import concurrent.futures
from datetime import UTC, datetime

import pytest

from traceforge.domain.enums import SessionStatus
from traceforge.engine.raw_event import RawEvent
from traceforge.engine.recorder import Recorder


def test_full_recording_session_and_activity_lifecycle(frozen_clock):
    recorder = Recorder()

    session = recorder.start_session()
    assert recorder.current_session() is not None
    assert session.status == SessionStatus.RECORDING

    recorder.start_activity("User Checkout")
    assert recorder.current_activity().name == "User Checkout"

    t0 = frozen_clock.now()
    e1 = RawEvent(event_id="e1", timestamp=t0, sequence=1, type="FunctionEntered", payload={"name": "validate_cart"})
    e2 = RawEvent(event_id="e2", timestamp=t0, sequence=2, type="SQLQuery", payload={"name": "SELECT cart"})

    recorder.emit(e1)
    recorder.emit(e2)

    completed_activity = recorder.stop_activity()
    assert completed_activity.name == "User Checkout"
    assert len(completed_activity.graph.nodes) >= 2

    completed_session = recorder.stop_session()
    assert completed_session.status == SessionStatus.COMPLETED
    assert len(completed_session.activities) >= 1


def test_replay_determinism():
    """Verifies that the exact same ordered RawEvents generate identical Execution Graphs."""
    t0 = datetime.now(UTC)

    raw_events = [
        RawEvent(
            event_id="e_start",
            timestamp=t0,
            sequence=1,
            type="ActivityStarted",
            payload={"name": "Search", "activity_id": "act_search"},
        ),
        RawEvent(event_id="e1", timestamp=t0, sequence=2, type="HTTPRequest", payload={"name": "GET /search"}),
        RawEvent(event_id="e2", timestamp=t0, sequence=3, type="SQLQuery", payload={"name": "SELECT * FROM items"}),
        RawEvent(event_id="e_finish", timestamp=t0, sequence=4, type="ActivityFinished"),
    ]

    def run_replay():
        recorder = Recorder()
        recorder.start_session(session_id="sess_fixed")
        for evt in raw_events:
            recorder.emit(evt)
        return recorder.stop_session()

    session1 = run_replay()
    session2 = run_replay()

    graph1_json = session1.activities[0].graph.model_dump_json()
    graph2_json = session2.activities[0].graph.model_dump_json()

    assert graph1_json == graph2_json  # Exact graph replay determinism


def test_concurrent_event_emission_and_thread_safety():
    recorder = Recorder()
    recorder.start_session()

    def emit_worker(worker_index: int):
        t0 = datetime.now(UTC)
        for i in range(10):
            evt = RawEvent(
                event_id=f"evt_w{worker_index}_{i}",
                timestamp=t0,
                sequence=i,
                type="FunctionEntered",
                payload={"name": f"func_{worker_index}_{i}"},
            )
            recorder.emit(evt)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(emit_worker, w) for w in range(5)]
        concurrent.futures.wait(futures)

    session = recorder.stop_session()
    total_nodes = sum(len(act.graph.nodes) for act in session.activities)
    assert total_nodes == 50  # 5 workers * 10 events


@pytest.mark.asyncio
async def test_async_event_emission():
    recorder = Recorder()
    recorder.start_session()

    async def async_worker(name: str):
        t0 = datetime.now(UTC)
        for i in range(5):
            evt = RawEvent(
                event_id=f"async_{name}_{i}",
                timestamp=t0,
                sequence=i,
                type="HTTPRequest",
                payload={"name": f"GET /{name}/{i}"},
            )
            recorder.emit(evt)
            await asyncio.sleep(0.001)

    await asyncio.gather(async_worker("task1"), async_worker("task2"))

    session = recorder.stop_session()
    total_nodes = sum(len(act.graph.nodes) for act in session.activities)
    assert total_nodes == 10


def test_malformed_event_resilience():
    recorder = Recorder()
    recorder.start_session()

    # Normal event
    recorder.emit(RawEvent(event_id="e1", timestamp=datetime.now(UTC), type="HTTPRequest"))

    # Malformed event with problematic payload
    recorder.emit(RawEvent(event_id="e_bad", timestamp=datetime.now(UTC), type="Custom", payload={"status": 99999}))

    # Normal event after malformed event
    recorder.emit(RawEvent(event_id="e2", timestamp=datetime.now(UTC), type="SQLQuery"))

    session = recorder.stop_session()
    assert len(session.activities) >= 1
    graph = session.activities[0].graph
    assert "e1" in graph.nodes
    assert "e_bad" in graph.nodes
    assert "e2" in graph.nodes
