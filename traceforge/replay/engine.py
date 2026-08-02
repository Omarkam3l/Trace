"""ReplayEngine public facade for Phase 8 Replay Engine."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from traceforge.replay.config import ReplayConfig, ReplayMode
from traceforge.replay.graph_rebuilder import GraphRebuilder
from traceforge.replay.session import ReplaySession
from traceforge.replay.snapshot_loader import SnapshotLoader
from traceforge.replay.timeline import TimelineBuilder
from traceforge.replay.validator import ReplayValidator

if TYPE_CHECKING:
    from traceforge.query.engine import QueryEngine
    from traceforge.storage.records import (
        ActivityRecord,
        GraphRecord,
        NodeRecord,
        RawEventRecord,
        RelationshipRecord,
        SnapshotRecord,
    )


class ReplayEngine:
    """Public facade for reconstructing historical execution state from storage."""

    def __init__(self, query_engine: QueryEngine) -> None:
        self._query_engine = query_engine
        self._timeline_builder = TimelineBuilder(query_engine)
        self._graph_rebuilder = GraphRebuilder(query_engine)
        self._snapshot_loader = SnapshotLoader(query_engine)
        self._lock = threading.RLock()

    def replay_session(self, session_id: str, config: ReplayConfig | None = None) -> ReplaySession:
        """Reconstruct a complete execution session from storage."""
        cfg = config or ReplayConfig()
        with self._lock:
            session_rec = self._query_engine.sessions.get_by_id(session_id)
            activities = self._query_engine.activities.list_by_session(session_id)

            graphs: list[GraphRecord] = []
            nodes: list[NodeRecord] = []
            relationships: list[RelationshipRecord] = []
            timeline: list[RawEventRecord] = []
            snapshots: list[SnapshotRecord] = []

            # 1. Rebuild Timeline if mode in (FULL, TIMELINE_ONLY)
            if cfg.mode in (ReplayMode.FULL, ReplayMode.TIMELINE_ONLY):
                timeline = self._timeline_builder.build_session_timeline(session_id)

            # 2. Rebuild Graphs, Nodes, Relationships if mode in (FULL, GRAPH_ONLY)
            if cfg.mode in (ReplayMode.FULL, ReplayMode.GRAPH_ONLY):
                for act in activities:
                    g_list, n_list, r_list = self._graph_rebuilder.rebuild_activity_graphs(act.activity_id)
                    graphs.extend(g_list)
                    nodes.extend(n_list)
                    relationships.extend(r_list)

            # 3. Load Snapshots if mode in (FULL, SNAPSHOT_ONLY)
            if cfg.mode in (ReplayMode.FULL, ReplayMode.SNAPSHOT_ONLY):
                snapshots = self._snapshot_loader.list_by_session(session_id)

            replay_res = ReplaySession(
                session=session_rec,
                activities=activities,
                graphs=graphs,
                nodes=nodes,
                relationships=relationships,
                timeline=timeline,
                snapshots=snapshots,
            )

            validator = ReplayValidator(cfg)
            validator.validate(replay_res)

            return replay_res
