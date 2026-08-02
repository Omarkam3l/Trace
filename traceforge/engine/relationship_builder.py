"""RelationshipBuilder for creating graph relationships."""

from __future__ import annotations

import uuid

from traceforge.domain.enums import RelationshipType
from traceforge.domain.node import Relationship


class RelationshipBuilder:
    """Creates Relationship value objects."""

    @staticmethod
    def create_relationship(
        graph_id: str,
        source_node_id: str,
        target_node_id: str,
        rel_type: RelationshipType = RelationshipType.PARENT_CHILD,
        relationship_id: str | None = None,
    ) -> Relationship:
        if relationship_id is None:
            rel_key = f"{graph_id}:{source_node_id}:{target_node_id}:{rel_type}"
            rel_id = f"rel_{uuid.uuid5(uuid.NAMESPACE_DNS, rel_key).hex[:16]}"
        else:
            rel_id = relationship_id

        return Relationship(
            relationship_id=rel_id,
            graph_id=graph_id,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            type=rel_type,
        )
