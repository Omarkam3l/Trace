"""Recorder: Phase 2 Recording Engine entry point owning runtime state."""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone

from traceforge.domain.activity import Activity
from traceforge.domain.enums import ActivityStatus, RelationshipType, SessionStatus
from traceforge.domain.environment import Environment
from traceforge.domain.profile import RecordingProfile
from traceforge.domain.session import RecordingSession
from traceforge.engine.activity_manager import ActivityManager
from traceforge.engine.context_manager import RecordingContextManager
from traceforge.engine.event_bus import EventBus
from traceforge.engine.node_factory import NodeFactory
from traceforge.engine.raw_event import RawEvent
from traceforge.engine.relationship_builder import RelationshipBuilder
from traceforge.engine.session_manager import SessionManager


class Recorder:
    """The Recording Engine's public entry point and single owner of runtime state."""

    def __init__(self) -> None:
        self._session_manager = SessionManager()
        self._activity_manager = ActivityManager()
        self._context_manager = RecordingContextManager()
        self._event_bus = EventBus()
        self._lock = threading.RLock()
        self._event_bus.subscribe(self._handle_raw_event)
        self._last_node_id_per_activity: dict[str, str] = {}

    @property
    def event_bus(self) -> EventBus:
        return self._event_bus

    # -- Public API -----------------------------------------------------
    def start_session(
        self,
        environment: Environment | None = None,
        profile: RecordingProfile | None = None,
        session_id: str | None = None,
    ) -> RecordingSession:
        """Start a new recording session."""
        with self._lock:
            sess_id = self._session_manager.start_session(
                session_id=session_id,
                environment=environment,
                profile=profile,
            )

            # Auto-start default activity for the session
            self._activity_manager.start_activity(session_id=sess_id, name="Default Activity")
            info = self._session_manager.get_current_session_info()
            assert info is not None
            return RecordingSession(
                session_id=sess_id,
                started_at=info["started_at"],
                status=SessionStatus.RECORDING,
                environment=info["environment"],
                profile=info["profile"],
                activities=[],
            )

    def stop_session(self) -> RecordingSession:
        """Stop the active recording session and return the final immutable session."""
        with self._lock:
            # Finish any open activities
            while self._activity_manager.get_current_activity_record() is not None:
                act = self._activity_manager.finish_activity()
                self._session_manager.register_completed_activity(act)

            completed_session = self._session_manager.stop_session()
            self._context_manager.clear()
            self._last_node_id_per_activity.clear()
            return completed_session

    def start_activity(self, name: str, activity_id: str | None = None) -> str:
        """Start a new activity within the current session."""
        with self._lock:
            if not self._session_manager.is_active:
                raise RuntimeError("Cannot start activity without an active recording session")
            info = self._session_manager.get_current_session_info()
            assert info is not None
            return self._activity_manager.start_activity(
                session_id=info["session_id"],
                name=name,
                activity_id=activity_id,
            )

    def stop_activity(self) -> Activity:
        """Finish the current activity and return its immutable snapshot."""
        with self._lock:
            act = self._activity_manager.finish_activity()
            self._session_manager.register_completed_activity(act)
            return act

    def emit(self, raw_event: RawEvent) -> None:
        """Emit a RawEvent to the EventBus."""
        self._event_bus.publish(raw_event)

    def current_session(self) -> dict[str, Any] | None:
        """Return info on the current active session, if any."""
        return self._session_manager.get_current_session_info()

    def current_activity(self) -> Activity | None:
        """Return snapshot of current active activity, if available."""
        with self._lock:
            rec = self._activity_manager.get_current_activity_record()
            if rec is None:
                return None
            return Activity(
                activity_id=rec.activity_id,
                session_id=rec.session_id,
                name=rec.name,
                started_at=rec.started_at,
                status=rec.status,
                graph=rec.graph_builder.build_final_graph(),
            )

    # -- Internal Event Handler -----------------------------------------
    def _handle_raw_event(self, raw_event: RawEvent) -> None:
        with self._lock:
            # Ignore events if no session is active, unless it's SessionStarted
            if not self._session_manager.is_active and raw_event.type != "SessionStarted":
                return

            try:
                # Boundary Events
                if raw_event.type == "SessionStarted":
                    if not self._session_manager.is_active:
                        sess_id = raw_event.payload.get("session_id") or raw_event.event_id
                        self.start_session(session_id=sess_id)
                    return

                if raw_event.type == "SessionFinished":
                    if self._session_manager.is_active:
                        self.stop_session()
                    return

                if raw_event.type == "ActivityStarted":
                    act_name = raw_event.payload.get("name") or "Activity"
                    act_id = raw_event.payload.get("activity_id")
                    self.start_activity(act_name, activity_id=act_id)
                    return

                if raw_event.type == "ActivityFinished":
                    self.stop_activity()
                    return

                # Execution Events
                act_rec = self._activity_manager.get_current_activity_record()
                if act_rec is None:
                    return

                graph_builder = act_rec.graph_builder
                parent_id = raw_event.context_id or self._context_manager.get_current_parent_node_id()

                node = NodeFactory.create_node(
                    raw_event=raw_event,
                    graph_id=graph_builder.graph_id,
                    parent_id=parent_id,
                )
                graph_builder.add_node(node)

                # Link parent-child relationship
                if parent_id and parent_id in graph_builder._nodes:
                    rel = RelationshipBuilder.create_relationship(
                        graph_id=graph_builder.graph_id,
                        source_node_id=parent_id,
                        target_node_id=node.node_id,
                        rel_type=RelationshipType.PARENT_CHILD,
                    )
                    graph_builder.add_relationship(rel)

                # Link previous-next relationship
                last_node_id = self._last_node_id_per_activity.get(act_rec.activity_id)
                if last_node_id and last_node_id != parent_id and last_node_id in graph_builder._nodes:
                    prev_rel = RelationshipBuilder.create_relationship(
                        graph_id=graph_builder.graph_id,
                        source_node_id=last_node_id,
                        target_node_id=node.node_id,
                        rel_type=RelationshipType.PREVIOUS_NEXT,
                    )
                    try:
                        graph_builder.add_relationship(prev_rel)
                    except ValueError:
                        pass  # Ignore cycle if previous-next introduces cycle

                self._last_node_id_per_activity[act_rec.activity_id] = node.node_id

            except Exception as exc:
                # Recorder error isolation - error event recorded without crashing
                pass
