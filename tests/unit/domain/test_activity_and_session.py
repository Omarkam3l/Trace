"""Unit tests for Activity and RecordingSession models."""

from __future__ import annotations

from datetime import UTC, datetime

from traceforge.domain import (
    Activity,
    ActivityStatus,
    Environment,
    ExecutionGraph,
    ExecutionNode,
    NodeStatus,
    NodeType,
    RecordingProfile,
    RecordingSession,
    SessionStatus,
)


def test_activity_and_recording_session_creation():
    now = datetime.now(UTC)
    env = Environment(os="Windows 11", python_version="3.13.3", environment_name="testing")
    profile = RecordingProfile(name="forensic", sampling_rate=1.0)

    node = ExecutionNode(
        node_id="n1",
        graph_id="g1",
        type=NodeType.HTTP_REQUEST,
        name="POST /login",
        started_at=now,
        status=NodeStatus.COMPLETED,
    )

    graph = ExecutionGraph(
        graph_id="g1",
        activity_id="act1",
        nodes={"n1": node},
        relationships=[],
    )

    activity = Activity(
        activity_id="act1",
        session_id="sess1",
        name="User Login",
        started_at=now,
        status=ActivityStatus.COMPLETED,
        graph=graph,
    )

    session = RecordingSession(
        session_id="sess1",
        started_at=now,
        status=SessionStatus.COMPLETED,
        environment=env,
        profile=profile,
        activities=[activity],
    )

    assert session.id == "sess1"
    assert session.environment.os == "Windows 11"
    assert session.profile.name == "forensic"
    assert len(session.activities) == 1

    act = session.activities[0]
    assert act.id == "act1"
    assert act.session_id == "sess1"
    assert act.name == "User Login"
    assert act.graph.id == "g1"
    assert act.graph.activity_id == "act1"
    assert len(act.graph.nodes) == 1
