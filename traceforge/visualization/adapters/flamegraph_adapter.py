"""FlamegraphAdapter converting node execution spans to FlamegraphViewModel."""

from __future__ import annotations

from typing import TYPE_CHECKING

from traceforge.visualization.models.flamegraph import FlamegraphSpanModel, FlamegraphViewModel

if TYPE_CHECKING:
    from traceforge.replay.session import ReplaySession
    from traceforge.visualization.config import VisualizationConfig


class FlamegraphAdapter:
    """Transforms node execution spans into hierarchical flamegraph stacks."""

    def adapt(self, session: ReplaySession, config: VisualizationConfig) -> FlamegraphViewModel:
        """Convert session nodes into a FlamegraphViewModel."""
        if not session.nodes:
            return FlamegraphViewModel(root=None)

        # Build node tree starting from root nodes (no parent)
        nodes_by_id = {n.node_id: n for n in session.nodes}
        root_nodes = [n for n in session.nodes if not n.parent_id]

        def build_span_tree(node) -> FlamegraphSpanModel:
            children_models: list[FlamegraphSpanModel] = []
            for child_id in node.child_ids:
                if child_id in nodes_by_id:
                    children_models.append(build_span_tree(nodes_by_id[child_id]))

            return FlamegraphSpanModel(
                name=node.name,
                value=node.duration_ms or 0.0,
                children=children_models,
            )

        if root_nodes:
            root_span = build_span_tree(root_nodes[0])
            return FlamegraphViewModel(root=root_span)

        # Fallback if no root node explicit parent ID
        fallback_span = build_span_tree(session.nodes[0])
        return FlamegraphViewModel(root=fallback_span)
