"""Unit tests for Phase 6.1 Storage Record models."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from traceforge.storage.records.activity_record import ActivityRecord
from traceforge.storage.records.graph_record import GraphRecord
from traceforge.storage.records.node_record import NodeRecord
from traceforge.storage.records.raw_event_record import RawEventRecord
from traceforge.storage.records.relationship_record import RelationshipRecord
from traceforge.storage.records.session_record import SessionRecord
from traceforge.storage.records.snapshot_record import SnapshotRecord


def test_storage_records_creation_and_immutability():
    now = datetime.now(timezone.utc)

    s_rec = SessionRecord(
        session_id="s1",
        started_at=now,
        status="completed",
        environment_os="win32",
        environment_python="3.13",
        profile_name="standard",
    )
    assert s_rec.session_id == "s1"
    with pytest.raises(Exception):
        s_rec.session_id = "mutated"

    a_rec = ActivityRecord(
        activity_id="act1",
        session_id="s1",
        name="Checkout",
        started_at=now,
        status="completed",
        graph_id="g1",
    )
    assert a_rec.activity_id == "act1"

    g_rec = GraphRecord(graph_id="g1", activity_id="act1", node_ids=["n1"], relationship_ids=["r1"])
    assert g_rec.graph_id == "g1"

    n_rec = NodeRecord(
        node_id="n1",
        graph_id="g1",
        type="function",
        name="validate",
        started_at=now,
        status="completed",
    )
    assert n_rec.node_id == "n1"

    r_rec = RelationshipRecord(
        relationship_id="r1",
        graph_id="g1",
        source_node_id="n1",
        target_node_id="n2",
        type="parent_child",
    )
    assert r_rec.relationship_id == "r1"

    evt_rec = RawEventRecord(
        event_id="e1",
        timestamp=now,
        sequence=1,
        type="FunctionEntered",
        source="python_sdk",
    )
    assert evt_rec.event_id == "e1"

    snap_rec = SnapshotRecord(
        snapshot_id="snap1",
        session_id="s1",
        timestamp=now,
        nodes_count=10,
    )
    assert snap_rec.snapshot_id == "snap1"
