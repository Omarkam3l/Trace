"""ReplayValidator for validating timeline ordering, sequences, and graph integrity."""

from __future__ import annotations

from traceforge.replay.config import ReplayConfig
from traceforge.replay.exceptions import ReplayConsistencyError, ReplayValidationError
from traceforge.replay.session import ReplaySession


class ReplayValidator:
    """Validates structural consistency and sequence ordering during replay."""

    def __init__(self, config: ReplayConfig) -> None:
        self._config = config

    def validate(self, session: ReplaySession) -> None:
        """Validate ReplaySession artifacts based on configuration."""
        if self._config.validate_sequences:
            self._validate_timeline_sequences(session.timeline)

        if self._config.validate_relationships:
            self._validate_graph_relationships(session.nodes, session.relationships)

    def _validate_timeline_sequences(self, timeline: list) -> None:
        prev_seq: int | None = None
        for evt in timeline:
            if prev_seq is not None and evt.sequence < prev_seq:
                msg = f"Timeline sequence regression detected: {evt.sequence} < {prev_seq}"
                if self._config.strict:
                    raise ReplayValidationError(msg)
            prev_seq = evt.sequence

    def _validate_graph_relationships(self, nodes: list, relationships: list) -> None:
        node_ids = {n.node_id for n in nodes}
        for rel in relationships:
            if rel.source_node_id not in node_ids or rel.target_node_id not in node_ids:
                msg = f"Relationship {rel.relationship_id!r} references missing nodes"
                if self._config.strict:
                    raise ReplayConsistencyError(msg)
