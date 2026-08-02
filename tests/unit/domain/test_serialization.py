"""Unit tests for JSON serialization and deserialization of the domain model."""

from __future__ import annotations

from datetime import datetime, timezone

from traceforge.domain import (
    Activity,
    ActivityStatus,
    Environment,
    ExecutionGraph,
    ExecutionNode,
    Metadata,
    NodeStatus,
    NodeType,
    RecordingProfile,
    RecordingSession,
    Relationship,
    RelationshipType,
    SessionStatus,
    SourceType,
)


def test_recording_session_json_roundtrip():
    now = datetime.now(timezone.utc)
    env = Environment(os="Linux x86_64", python_version="3.12.0", variables={"STAGE": "prod"})
    profile = RecordingProfile(name="standard", max_payload_bytes=50000)

    n1 = ExecutionNode(
        node_id="n1",
        graph_id="g1",
        type=NodeType.HTTP_REQUEST,
        name="GET /api/v1/products",
        started_at=now,
        status=NodeStatus.COMPLETED,
        source=SourceType.FASTAPI_PLUGIN,
    )

    n2 = ExecutionNode(
        node_id="n2",
        graph_id="g1",
        type=NodeType.DATABASE_QUERY,
        name="SELECT * FROM products",
        started_at=now,
        status=NodeStatus.COMPLETED,
        metadata=Metadata(attributes={"db.statement": "SELECT * FROM products", "db.rows": 15}),
        source=SourceType.SQL_PLUGIN,
    )

    rel = Relationship(
        relationship_id="r1",
        graph_id="g1",
        source_node_id="n1",
        target_node_id="n2",
        type=RelationshipType.PARENT_CHILD,
    )

    graph = ExecutionGraph(
        graph_id="g1",
        activity_id="act_search",
        nodes={"n1": n1, "n2": n2},
        relationships=[rel],
    )

    activity = Activity(
        activity_id="act_search",
        session_id="sess_100",
        name="Product Search",
        started_at=now,
        status=ActivityStatus.COMPLETED,
        graph=graph,
    )

    session = RecordingSession(
        session_id="sess_100",
        started_at=now,
        status=SessionStatus.COMPLETED,
        environment=env,
        profile=profile,
        activities=[activity],
    )

    # 1. Serialize to JSON
    json_str = session.model_dump_json()
    assert isinstance(json_str, str)
    assert "sess_100" in json_str
    assert "Product Search" in json_str
    assert "SELECT * FROM products" in json_str

    # 2. Deserialize back from JSON
    restored = RecordingSession.model_validate_json(json_str)

    assert restored.id == session.id
    assert restored.environment.os == session.environment.os
    assert len(restored.activities) == 1
    assert restored.activities[0].name == "Product Search"

    restored_graph = restored.activities[0].graph
    assert len(restored_graph.nodes) == 2
    assert restored_graph.nodes["n2"].metadata.get("db.rows") == 15
    assert len(restored_graph.relationships) == 1
    assert restored_graph.relationships[0].source_node_id == "n1"
    assert restored_graph.relationships[0].target_node_id == "n2"
