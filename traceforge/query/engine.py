"""QueryEngine: public read facade for Phase 7 Query Engine."""

from __future__ import annotations

import sqlite3
import threading
from typing import TYPE_CHECKING, Any

from traceforge.query.exceptions import InvalidQueryError
from traceforge.query.queries import (
    ActivityQuery,
    GraphQuery,
    NodeQuery,
    RawEventQuery,
    RelationshipQuery,
    SessionQuery,
)
from traceforge.query.repositories.activity_repository import ActivityRepository
from traceforge.query.repositories.graph_repository import GraphRepository
from traceforge.query.repositories.node_repository import NodeRepository
from traceforge.query.repositories.raw_event_repository import RawEventRepository
from traceforge.query.repositories.relationship_repository import RelationshipRepository
from traceforge.query.repositories.session_repository import SessionRepository

if TYPE_CHECKING:
    from traceforge.storage.records import (
        ActivityRecord,
        GraphRecord,
        NodeRecord,
        RawEventRecord,
        RelationshipRecord,
        SessionRecord,
    )


class QueryEngine:
    """Read facade executing immutable query objects and graph traversal over storage repositories."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection
        self._session_repo = SessionRepository(connection)
        self._activity_repo = ActivityRepository(connection)
        self._graph_repo = GraphRepository(connection)
        self._node_repo = NodeRepository(connection)
        self._rel_repo = RelationshipRepository(connection)
        self._raw_event_repo = RawEventRepository(connection)
        self._lock = threading.RLock()

    @property
    def sessions(self) -> SessionRepository:
        return self._session_repo

    @property
    def activities(self) -> ActivityRepository:
        return self._activity_repo

    @property
    def graphs(self) -> GraphRepository:
        return self._graph_repo

    @property
    def nodes(self) -> NodeRepository:
        return self._node_repo

    @property
    def relationships(self) -> RelationshipRepository:
        return self._rel_repo

    @property
    def raw_events(self) -> RawEventRepository:
        return self._raw_event_repo

    def execute_session_query(self, query: SessionQuery) -> list[SessionRecord]:
        """Execute a SessionQuery."""
        with self._lock:
            if query.session_id:
                return [self._session_repo.get_by_id(query.session_id)]
            return self._session_repo.list(filter=query.filter, pagination=query.pagination)

    def execute_activity_query(self, query: ActivityQuery) -> list[ActivityRecord]:
        """Execute an ActivityQuery."""
        with self._lock:
            if query.activity_id:
                return [self._activity_repo.get_by_id(query.activity_id)]
            if query.session_id:
                return self._activity_repo.list_by_session(query.session_id, pagination=query.pagination)
            raise InvalidQueryError("ActivityQuery requires activity_id or session_id")

    def execute_graph_query(self, query: GraphQuery) -> list[GraphRecord]:
        """Execute a GraphQuery."""
        with self._lock:
            if query.graph_id:
                return [self._graph_repo.get_by_id(query.graph_id)]
            if query.activity_id:
                return self._graph_repo.list_by_activity(query.activity_id)
            raise InvalidQueryError("GraphQuery requires graph_id or activity_id")

    def execute_node_query(self, query: NodeQuery) -> list[NodeRecord]:
        """Execute a NodeQuery."""
        with self._lock:
            if query.node_id:
                return [self._node_repo.get_by_id(query.node_id)]
            if query.graph_id:
                return self._node_repo.list_by_graph(query.graph_id, pagination=query.pagination)
            raise InvalidQueryError("NodeQuery requires node_id or graph_id")

    def execute_relationship_query(self, query: RelationshipQuery) -> list[RelationshipRecord]:
        """Execute a RelationshipQuery."""
        with self._lock:
            if query.graph_id:
                if query.source_node_id:
                    return self._rel_repo.list_outgoing(query.source_node_id, query.graph_id)
                if query.target_node_id:
                    return self._rel_repo.list_incoming(query.target_node_id, query.graph_id)
                return self._rel_repo.list_by_graph(query.graph_id)
            raise InvalidQueryError("RelationshipQuery requires graph_id")

    def execute_raw_event_query(self, query: RawEventQuery) -> list[RawEventRecord]:
        """Execute a RawEventQuery."""
        with self._lock:
            if query.session_id:
                return self._raw_event_repo.list_by_session(query.session_id, pagination=query.pagination)
            if query.activity_id:
                return self._raw_event_repo.list_by_activity(query.activity_id, pagination=query.pagination)
            return self._raw_event_repo.list_all(pagination=query.pagination)
