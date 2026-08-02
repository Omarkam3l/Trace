"""GraphDiffComparator for comparing execution node trees and relationships."""

from __future__ import annotations

from typing import TYPE_CHECKING

from traceforge.diff.report import NodeGraphDiff

if TYPE_CHECKING:
    from traceforge.replay.session import ReplaySession


class GraphDiffComparator:
    """Compares node graphs and relationship structures between baseline and target sessions."""

    def compare(self, baseline: ReplaySession, target: ReplaySession) -> NodeGraphDiff:
        """Compare execution node sets and relationships deterministically."""
        base_node_map = {n.name: n for n in baseline.nodes}
        target_node_map = {n.name: n for n in target.nodes}

        base_names = set(base_node_map.keys())
        target_names = set(target_node_map.keys())

        added_nodes = sorted(list(target_names - base_names))
        removed_nodes = sorted(list(base_names - target_names))
        common_nodes = base_names & target_names

        modified_nodes: list[str] = []
        for name in sorted(common_nodes):
            bn = base_node_map[name]
            tn = target_node_map[name]
            if bn.type != tn.type or bn.status != tn.status or bn.child_ids != tn.child_ids:
                modified_nodes.append(name)

        base_rel_signatures = {f"{r.source_node_id}->{r.target_node_id}:{r.type}" for r in baseline.relationships}
        target_rel_signatures = {f"{r.source_node_id}->{r.target_node_id}:{r.type}" for r in target.relationships}

        added_rels = sorted(list(target_rel_signatures - base_rel_signatures))
        removed_rels = sorted(list(base_rel_signatures - target_rel_signatures))

        return NodeGraphDiff(
            added_nodes=added_nodes,
            removed_nodes=removed_nodes,
            modified_nodes=modified_nodes,
            added_relationships=added_rels,
            removed_relationships=removed_rels,
        )
