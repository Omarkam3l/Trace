"""GraphBuilder: manages live graph construction and incremental DAG validation."""

from __future__ import annotations

import threading

from traceforge.domain.graph import ExecutionGraph
from traceforge.domain.node import ExecutionNode, Relationship


class GraphBuilder:
    """Mutable builder for constructing an activity's execution graph during recording."""

    def __init__(self, graph_id: str, activity_id: str) -> None:
        self._graph_id = graph_id
        self._activity_id = activity_id
        self._nodes: dict[str, ExecutionNode] = {}
        self._relationships: list[Relationship] = []
        self._lock = threading.RLock()

    @property
    def graph_id(self) -> str:
        return self._graph_id

    @property
    def activity_id(self) -> str:
        return self._activity_id

    def add_node(self, node: ExecutionNode) -> None:
        with self._lock:
            if node.graph_id != self._graph_id:
                raise ValueError(
                    f"Node graph_id {node.graph_id!r} does not match GraphBuilder graph_id {self._graph_id!r}"
                )
            self._nodes[node.node_id] = node

    def add_relationship(self, relationship: Relationship) -> None:
        with self._lock:
            if relationship.graph_id != self._graph_id:
                raise ValueError(
                    f"Relationship graph_id {relationship.graph_id!r} does not match GraphBuilder graph_id {self._graph_id!r}"
                )
            if relationship.source_node_id not in self._nodes:
                raise ValueError(f"Source node {relationship.source_node_id!r} not found in graph")
            if relationship.target_node_id not in self._nodes:
                raise ValueError(f"Target node {relationship.target_node_id!r} not found in graph")

            # Check incremental cycle before adding
            temp_relationships = [*self._relationships, relationship]
            # Construct candidate graph to test DAG property
            ExecutionGraph(
                graph_id=self._graph_id,
                activity_id=self._activity_id,
                nodes=self._nodes,
                relationships=temp_relationships,
            )
            self._relationships.append(relationship)

            # Update parent child_ids if PARENT_CHILD
            if relationship.type == relationship.type.PARENT_CHILD:
                parent_node = self._nodes[relationship.source_node_id]
                if relationship.target_node_id not in parent_node.child_ids:
                    updated_children = [*parent_node.child_ids, relationship.target_node_id]
                    self._nodes[relationship.source_node_id] = parent_node.model_copy(
                        update={"child_ids": updated_children}
                    )

    def get_node(self, node_id: str) -> ExecutionNode | None:
        with self._lock:
            return self._nodes.get(node_id)

    def build_final_graph(self) -> ExecutionGraph:
        with self._lock:
            return ExecutionGraph(
                graph_id=self._graph_id,
                activity_id=self._activity_id,
                nodes=dict(self._nodes),
                relationships=list(self._relationships),
            )
