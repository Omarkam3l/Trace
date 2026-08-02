"""GraphRebuilder for reconstructing execution graphs and node hierarchies."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from traceforge.query.engine import QueryEngine
    from traceforge.storage.records.graph_record import GraphRecord
    from traceforge.storage.records.node_record import NodeRecord
    from traceforge.storage.records.relationship_record import RelationshipRecord


class GraphRebuilder:
    """Reconstructs execution graphs, nodes, relationships, and hierarchy trees from storage."""

    def __init__(self, query_engine: QueryEngine) -> None:
        self._query_engine = query_engine

    def rebuild_activity_graphs(self, activity_id: str) -> tuple[list[GraphRecord], list[NodeRecord], list[RelationshipRecord]]:
        """Reconstruct graphs, nodes, and relationships for an activity_id."""
        graphs = self._query_engine.graphs.list_by_activity(activity_id)
        all_nodes: list[NodeRecord] = []
        all_rels: list[RelationshipRecord] = []

        for graph in graphs:
            nodes = self._query_engine.nodes.list_by_graph(graph.graph_id)
            rels = self._query_engine.relationships.list_by_graph(graph.graph_id)
            all_nodes.extend(nodes)
            all_rels.extend(rels)

        return graphs, all_nodes, all_rels
