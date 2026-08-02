"""GraphAdapter converting ReplaySession nodes and relationships to GraphViewModel."""

from __future__ import annotations

from typing import TYPE_CHECKING

from traceforge.visualization.models.graph import EdgeViewModel, GraphViewModel, NodeViewModel

if TYPE_CHECKING:
    from traceforge.replay.session import ReplaySession
    from traceforge.visualization.config import VisualizationConfig


class GraphAdapter:
    """Transforms ReplaySession nodes and relationships into frontend graph models."""

    def adapt(self, session: ReplaySession, config: VisualizationConfig) -> GraphViewModel:
        """Convert session nodes and relationships into GraphViewModel."""
        nodes = [
            NodeViewModel(
                id=n.node_id,
                label=n.name,
                type=n.type,
                status=n.status,
                duration_ms=n.duration_ms,
            )
            for n in session.nodes
        ]

        edges = [
            EdgeViewModel(
                id=r.relationship_id,
                source=r.source_node_id,
                target=r.target_node_id,
                label=r.type,
            )
            for r in session.relationships
        ]

        return GraphViewModel(nodes=nodes, edges=edges)
