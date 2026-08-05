"""Unit tests for ReplayValidator integrity and sequence checking."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from traceforge.replay.config import ReplayConfig
from traceforge.replay.exceptions import ReplayConsistencyError, ReplayValidationError
from traceforge.replay.session import ReplaySession
from traceforge.replay.validator import ReplayValidator
from traceforge.storage.records import NodeRecord, RawEventRecord, RelationshipRecord


def test_replay_validator_sequence_regression():
    now = datetime.now(timezone.utc)
    e1 = RawEventRecord(event_id="e1", timestamp=now, sequence=10, type="A", source="test")
    e2 = RawEventRecord(event_id="e2", timestamp=now, sequence=5, type="B", source="test")  # Sequence regression

    sess = ReplaySession(timeline=[e1, e2])
    validator = ReplayValidator(ReplayConfig(strict=True))

    with pytest.raises(ReplayValidationError):
        validator.validate(sess)


def test_replay_validator_missing_relationship_nodes():
    n1 = NodeRecord(
        node_id="n1",
        graph_id="g1",
        type="function",
        name="main",
        started_at=datetime.now(timezone.utc),
        status="completed",
    )
    rel = RelationshipRecord(
        relationship_id="r1", graph_id="g1", source_node_id="n1", target_node_id="missing_n2", type="parent_child"
    )

    sess = ReplaySession(nodes=[n1], relationships=[rel])
    validator = ReplayValidator(ReplayConfig(strict=True))

    with pytest.raises(ReplayConsistencyError):
        validator.validate(sess)
