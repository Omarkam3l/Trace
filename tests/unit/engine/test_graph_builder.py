"""Unit tests for GraphBuilder mutable construction and incremental DAG validation."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from traceforge.domain.enums import NodeStatus, NodeType, RelationshipType
from traceforge.domain.node import ExecutionNode
from traceforge.engine.graph_builder import GraphBuilder
from traceforge.engine.relationship_builder import RelationshipBuilder


def _make_node(node_id: str, graph_id: str = "g1") -> ExecutionNode:
    return ExecutionNode(
        node_id=node_id,
        graph_id=graph_id,
        type=NodeType.FUNCTION_CALL,
        name=f"node_{node_id}",
        started_at=datetime.now(UTC),
        status=NodeStatus.COMPLETED,
    )


def test_graph_builder_node_and_relationship_insertion():
    builder = GraphBuilder(graph_id="g1", activity_id="act1")

    n1 = _make_node("n1")
    n2 = _make_node("n2")

    builder.add_node(n1)
    builder.add_node(n2)

    rel = RelationshipBuilder.create_relationship(
        graph_id="g1", source_node_id="n1", target_node_id="n2", rel_type=RelationshipType.PARENT_CHILD
    )
    builder.add_relationship(rel)

    graph = builder.build_final_graph()
    assert graph.id == "g1"
    assert len(graph.nodes) == 2
    assert len(graph.relationships) == 1
    assert "n2" in graph.nodes["n1"].child_ids


def test_graph_builder_incremental_dag_cycle_rejection():
    builder = GraphBuilder(graph_id="g1", activity_id="act1")

    n1 = _make_node("n1")
    n2 = _make_node("n2")
    builder.add_node(n1)
    builder.add_node(n2)

    rel1 = RelationshipBuilder.create_relationship("g1", "n1", "n2")
    builder.add_relationship(rel1)

    rel_cycle = RelationshipBuilder.create_relationship("g1", "n2", "n1")

    with pytest.raises(ValueError) as exc_info:
        builder.add_relationship(rel_cycle)

    assert "cyclic relationships" in str(exc_info.value)
