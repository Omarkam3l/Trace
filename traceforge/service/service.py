"""TraceForgeApiService unified high-level API service facade."""

from __future__ import annotations

import sqlite3
import threading
from typing import TYPE_CHECKING

from traceforge.diff.config import DiffConfig
from traceforge.diff.engine import ExecutionDiffEngine
from traceforge.export.config import ExportConfig
from traceforge.export.engine import ExportEngine
from traceforge.query.engine import QueryEngine
from traceforge.query.exceptions import NotFoundError
from traceforge.replay.config import ReplayConfig
from traceforge.replay.engine import ReplayEngine
from traceforge.service.config import ServiceConfig
from traceforge.service.exceptions import ServiceExecutionError, ServiceNotFoundError
from traceforge.visualization.config import VisualizationConfig
from traceforge.visualization.engine import VisualizationEngine

if TYPE_CHECKING:
    from traceforge.diff.report import ExecutionDiffReport
    from traceforge.query.filters import QueryFilter
    from traceforge.query.pagination import Pagination
    from traceforge.replay.session import ReplaySession
    from traceforge.storage.records import SessionRecord
    from traceforge.visualization.models import (
        DiffViewModel,
        FlamegraphViewModel,
        GraphViewModel,
        TimelineViewModel,
    )


class TraceForgeApiService:
    """Unified read-only application service facade for external clients."""

    def __init__(self, connection: sqlite3.Connection, config: ServiceConfig | None = None) -> None:
        self._conn = connection
        self._config = config or ServiceConfig()
        self._query_engine = QueryEngine(connection)
        self._replay_engine = ReplayEngine(self._query_engine)
        self._diff_engine = ExecutionDiffEngine()
        self._export_engine = ExportEngine()
        self._vis_engine = VisualizationEngine()
        self._lock = threading.RLock()

    @property
    def query_engine(self) -> QueryEngine:
        return self._query_engine

    @property
    def replay_engine(self) -> ReplayEngine:
        return self._replay_engine

    @property
    def diff_engine(self) -> ExecutionDiffEngine:
        return self._diff_engine

    @property
    def export_engine(self) -> ExportEngine:
        return self._export_engine

    @property
    def vis_engine(self) -> VisualizationEngine:
        return self._vis_engine

    def get_session(self, session_id: str) -> SessionRecord:
        """Fetch SessionRecord by ID or raise ServiceNotFoundError."""
        with self._lock:
            try:
                return self._query_engine.sessions.get_by_id(session_id)
            except NotFoundError as err:
                raise ServiceNotFoundError(f"Session {session_id!r} not found") from err
            except Exception as err:
                raise ServiceExecutionError(f"Failed to get session {session_id!r}: {err}") from err

    def list_sessions(self, filter: QueryFilter | None = None, pagination: Pagination | None = None) -> list[SessionRecord]:
        """List SessionRecords matching optional filter and pagination."""
        with self._lock:
            try:
                return self._query_engine.sessions.list(filter=filter, pagination=pagination)
            except Exception as err:
                raise ServiceExecutionError(f"Failed to list sessions: {err}") from err

    def replay_session(self, session_id: str, config: ReplayConfig | None = None) -> ReplaySession:
        """Reconstruct a complete execution session from storage."""
        with self._lock:
            try:
                return self._replay_engine.replay_session(session_id, config=config)
            except NotFoundError as err:
                raise ServiceNotFoundError(f"Session {session_id!r} not found for replay") from err
            except Exception as err:
                raise ServiceExecutionError(f"Failed to replay session {session_id!r}: {err}") from err

    def compare_sessions(self, baseline_id: str, target_id: str, config: DiffConfig | None = None) -> ExecutionDiffReport:
        """Compare baseline and target sessions and produce an ExecutionDiffReport."""
        with self._lock:
            base_replay = self.replay_session(baseline_id)
            targ_replay = self.replay_session(target_id)
            try:
                return self._diff_engine.compare(base_replay, targ_replay, config=config)
            except Exception as err:
                raise ServiceExecutionError(f"Failed to compare sessions {baseline_id!r} and {target_id!r}: {err}") from err

    def export_session(self, session_id: str, config: ExportConfig | None = None) -> str:
        """Export a ReplaySession artifact to formatted string."""
        with self._lock:
            session_replay = self.replay_session(session_id)
            try:
                return self._export_engine.export_session(session_replay, config=config)
            except Exception as err:
                raise ServiceExecutionError(f"Failed to export session {session_id!r}: {err}") from err

    def export_diff(self, baseline_id: str, target_id: str, config: ExportConfig | None = None) -> str:
        """Export an ExecutionDiffReport artifact to formatted string."""
        with self._lock:
            diff_report = self.compare_sessions(baseline_id, target_id)
            try:
                return self._export_engine.export_diff_report(diff_report, config=config)
            except Exception as err:
                raise ServiceExecutionError(f"Failed to export diff between {baseline_id!r} and {target_id!r}: {err}") from err

    def get_graph_visualization(self, session_id: str, config: VisualizationConfig | None = None) -> GraphViewModel:
        """Get Cytoscape/D3 GraphViewModel for a session."""
        with self._lock:
            session_replay = self.replay_session(session_id)
            return self._vis_engine.to_graph_model(session_replay, config=config)

    def get_timeline_visualization(self, session_id: str, config: VisualizationConfig | None = None) -> TimelineViewModel:
        """Get TimelineViewModel for a session."""
        with self._lock:
            session_replay = self.replay_session(session_id)
            return self._vis_engine.to_timeline_model(session_replay, config=config)

    def get_flamegraph_visualization(self, session_id: str, config: VisualizationConfig | None = None) -> FlamegraphViewModel:
        """Get FlamegraphViewModel for a session."""
        with self._lock:
            session_replay = self.replay_session(session_id)
            return self._vis_engine.to_flamegraph_model(session_replay, config=config)

    def get_diff_visualization(self, baseline_id: str, target_id: str, config: VisualizationConfig | None = None) -> DiffViewModel:
        """Get DiffViewModel for a session comparison."""
        with self._lock:
            diff_report = self.compare_sessions(baseline_id, target_id)
            return self._vis_engine.to_diff_model(diff_report, config=config)
