"""Unit tests for ExecutionNode and Relationship entities."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from traceforge.domain import (
    ExecutionNode,
    Metadata,
    NodeStatus,
    NodeType,
    Relationship,
    RelationshipType,
    SourceType,
)


def test_execution_node_creation_and_immutability():
    now = datetime.now(timezone.utc)
    node = ExecutionNode(
        node_id="n1",
        graph_id="g1",
        type=NodeType.FUNCTION_CALL,
        name="validate_user",
        started_at=now,
        finished_at=now,
        duration_ms=12.5,
        status=NodeStatus.COMPLETED,
        inputs={"user_id": 42},
        outputs={"valid": True},
        metadata=Metadata(attributes={"db.name": "users_db"}),
        tags={"auth", "critical"},
        source=SourceType.PYTHON_SDK,
    )

    assert node.id == "n1"
    assert node.node_id == "n1"
    assert node.graph_id == "g1"
    assert node.type == NodeType.FUNCTION_CALL
    assert node.name == "validate_user"
    assert node.duration_ms == 12.5
    assert node.inputs == {"user_id": 42}
    assert node.metadata.get("db.name") == "users_db"
    assert "auth" in node.tags

    with pytest.raises(ValidationError):
        node.name = "mutated_name"  # Immutability enforcement


def test_relationship_validations():
    rel = Relationship(
        relationship_id="r1",
        graph_id="g1",
        source_node_id="n1",
        target_node_id="n2",
        type=RelationshipType.PARENT_CHILD,
    )

    assert rel.id == "r1"
    assert rel.source_node_id == "n1"
    assert rel.target_node_id == "n2"

    # Self loops are forbidden
    with pytest.raises(ValidationError):
        Relationship(
            relationship_id="r2",
            graph_id="g1",
            source_node_id="n1",
            target_node_id="n1",
            type=RelationshipType.PARENT_CHILD,
        )
