"""Unit tests for ExecutionGraph and DAG cycle validation."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from traceforge.domain import (
    ExecutionGraph,
    ExecutionNode,
    NodeStatus,
    NodeType,
    Relationship,
    RelationshipType,
)


def _make_node(node_id: str, name: str = "node") -> ExecutionNode:
    return ExecutionNode(
        node_id=node_id,
        graph_id="g1",
        type=NodeType.FUNCTION_CALL,
        name=name,
        started_at=datetime.now(UTC),
        status=NodeStatus.COMPLETED,
    )


def test_valid_dag_execution_graph():
    n1 = _make_node("n1", "root")
    n2 = _make_node("n2", "child1")
    n3 = _make_node("n3", "child2")

    rel1 = Relationship(
        relationship_id="r1",
        graph_id="g1",
        source_node_id="n1",
        target_node_id="n2",
        type=RelationshipType.PARENT_CHILD,
    )
    rel2 = Relationship(
        relationship_id="r2",
        graph_id="g1",
        source_node_id="n2",
        target_node_id="n3",
        type=RelationshipType.PARENT_CHILD,
    )

    graph = ExecutionGraph(
        graph_id="g1",
        activity_id="a1",
        nodes={"n1": n1, "n2": n2, "n3": n3},
        relationships=[rel1, rel2],
    )

    assert graph.id == "g1"
    assert graph.activity_id == "a1"
    assert len(graph.nodes) == 3
    assert len(graph.relationships) == 2


def test_graph_rejects_missing_node_references():
    n1 = _make_node("n1")
    rel = Relationship(
        relationship_id="r1",
        graph_id="g1",
        source_node_id="n1",
        target_node_id="non_existent",
        type=RelationshipType.PARENT_CHILD,
    )

    with pytest.raises(ValidationError) as exc_info:
        ExecutionGraph(
            graph_id="g1",
            activity_id="a1",
            nodes={"n1": n1},
            relationships=[rel],
        )

    assert "references non-existent target node" in str(exc_info.value)


def test_graph_rejects_cyclic_relationships():
    n1 = _make_node("n1")
    n2 = _make_node("n2")
    n3 = _make_node("n3")

    # n1 -> n2 -> n3 -> n1 (Cycle)
    rel1 = Relationship(relationship_id="r1", graph_id="g1", source_node_id="n1", target_node_id="n2")
    rel2 = Relationship(relationship_id="r2", graph_id="g1", source_node_id="n2", target_node_id="n3")
    rel3 = Relationship(relationship_id="r3", graph_id="g1", source_node_id="n3", target_node_id="n1")

    with pytest.raises(ValidationError) as exc_info:
        ExecutionGraph(
            graph_id="g1",
            activity_id="a1",
            nodes={"n1": n1, "n2": n2, "n3": n3},
            relationships=[rel1, rel2, rel3],
        )

    assert "cyclic relationships" in str(exc_info.value)
