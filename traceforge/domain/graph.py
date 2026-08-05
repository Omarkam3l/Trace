"""ExecutionGraph domain entity model."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from traceforge.domain.node import ExecutionNode, Relationship


class ExecutionGraph(BaseModel):
    """Immutable Directed Acyclic Graph (DAG) representing activity execution."""

    model_config = ConfigDict(frozen=True)

    graph_id: str
    activity_id: str
    nodes: dict[str, ExecutionNode] = Field(default_factory=dict)
    relationships: list[Relationship] = Field(default_factory=list)

    @property
    def id(self) -> str:
        return self.graph_id

    @model_validator(mode="after")
    def validate_graph_integrity(self) -> ExecutionGraph:
        node_ids = set(self.nodes.keys())

        # 1. Validate graph_id consistency and node existence
        for node_id, node in self.nodes.items():
            if node.graph_id != self.graph_id:
                raise ValueError(
                    f"ExecutionNode {node_id!r} graph_id {node.graph_id!r} does not match ExecutionGraph graph_id {self.graph_id!r}"
                )

        for rel in self.relationships:
            if rel.graph_id != self.graph_id:
                raise ValueError(
                    f"Relationship {rel.relationship_id!r} graph_id {rel.graph_id!r} does not match ExecutionGraph graph_id {self.graph_id!r}"
                )
            if rel.source_node_id not in node_ids:
                raise ValueError(
                    f"Relationship {rel.relationship_id!r} references non-existent source node {rel.source_node_id!r}"
                )
            if rel.target_node_id not in node_ids:
                raise ValueError(
                    f"Relationship {rel.relationship_id!r} references non-existent target node {rel.target_node_id!r}"
                )

        # 2. Enforce Directed Acyclic Graph (DAG) - prevent cycles
        if not node_ids:
            return self

        adj: dict[str, list[str]] = {nid: [] for nid in node_ids}
        in_degree: dict[str, int] = {nid: 0 for nid in node_ids}

        for rel in self.relationships:
            adj[rel.source_node_id].append(rel.target_node_id)
            in_degree[rel.target_node_id] += 1

        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        visited_count = 0

        while queue:
            curr = queue.pop(0)
            visited_count += 1
            for nxt in adj[curr]:
                in_degree[nxt] -= 1
                if in_degree[nxt] == 0:
                    queue.append(nxt)

        if visited_count < len(node_ids):
            raise ValueError("ExecutionGraph contains cyclic relationships")

        return self
