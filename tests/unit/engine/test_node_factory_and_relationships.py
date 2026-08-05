"""Unit tests for NodeFactory and RelationshipBuilder."""

from __future__ import annotations

from datetime import datetime, timezone

from traceforge.domain.enums import NodeStatus, NodeType, RelationshipType, SourceType
from traceforge.engine.node_factory import NodeFactory
from traceforge.engine.raw_event import RawEvent
from traceforge.engine.relationship_builder import RelationshipBuilder


def test_node_factory_creation_and_mapping():
    now = datetime.now(timezone.utc)
    event = RawEvent(
        event_id="e10",
        timestamp=now,
        type="SQLQuery",
        source=SourceType.SQL_PLUGIN,
        payload={
            "name": "SELECT users",
            "duration_ms": 15.2,
            "status": "completed",
            "inputs": {"query": "SELECT * FROM users"},
        },
        metadata={"db.system": "postgresql"},
    )

    node = NodeFactory.create_node(event, graph_id="g1", parent_id="p1")

    assert node.id == "e10"
    assert node.graph_id == "g1"
    assert node.parent_id == "p1"
    assert node.type == NodeType.DATABASE_QUERY
    assert node.name == "SELECT users"
    assert node.duration_ms == 15.2
    assert node.status == NodeStatus.COMPLETED
    assert node.inputs == {"query": "SELECT * FROM users"}
    assert node.metadata.get("db.system") == "postgresql"
    assert node.source == SourceType.SQL_PLUGIN


def test_node_factory_handles_malformed_raw_event_safely():
    now = datetime.now(timezone.utc)
    # Malformed payload with invalid status type
    event = RawEvent(
        event_id="e_malformed",
        timestamp=now,
        type="HTTPRequest",
        payload={"status": 12345},  # Invalid status format
    )

    node = NodeFactory.create_node(event, graph_id="g1")

    assert node.id == "e_malformed"
    assert node.graph_id == "g1"
    assert node.type == NodeType.HTTP_REQUEST


def test_relationship_builder_creation():
    rel = RelationshipBuilder.create_relationship(
        graph_id="g1",
        source_node_id="n1",
        target_node_id="n2",
        rel_type=RelationshipType.DEPENDENCY,
    )

    assert rel.graph_id == "g1"
    assert rel.source_node_id == "n1"
    assert rel.target_node_id == "n2"
    assert rel.type == RelationshipType.DEPENDENCY
    assert rel.relationship_id is not None
