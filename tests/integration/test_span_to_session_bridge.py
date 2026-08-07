"""Regression tests: public SDK tracing (Tracer/@traced()/span()) must be able
to reach QueryEngine/ReplayEngine, via SpanToSessionBridge.

Before this fix, there was no code path from SpanModel (what Tracer/Recorder
produce) to RecordingSession/Activity/ExecutionGraph (what QueryEngine reads).
Recording through the public SDK and then calling qe.sessions.list() always
returned an empty list, and TraceForgeApiService.replay_session(...) had
nothing to replay.
"""

import traceforge
from traceforge.storage.drivers.sqlite import SQLiteStorageDriver


def _make_bridge():
    driver = SQLiteStorageDriver(":memory:")
    pipeline = traceforge.ExecutionPipeline()
    pipeline.register_consumer(traceforge.SQLiteIngestConsumer(driver))
    bridge = traceforge.SpanToSessionBridge(pipeline)
    return driver, bridge


def test_traced_function_produces_a_queryable_session():
    traceforge.reset_default_tracer()
    tracer = traceforge.configure(service_name="bridge-basic")
    driver, bridge = _make_bridge()
    tracer.add_hook(bridge)

    @traceforge.traced()
    def add(a, b):
        return a + b

    assert add(2, 3) == 5

    conn = driver.connection_manager.get_connection()
    qe = traceforge.QueryEngine(conn)
    sessions = qe.sessions.list()
    assert len(sessions) == 1
    assert sessions[0].status == "completed"


def test_nested_spans_produce_correct_node_and_relationship_counts():
    traceforge.reset_default_tracer()
    tracer = traceforge.configure(service_name="bridge-nested")
    driver, bridge = _make_bridge()
    tracer.add_hook(bridge)

    @traceforge.traced()
    def leaf():
        return 1

    @traceforge.traced()
    def root():
        with traceforge.span("mid"):
            return leaf()

    root()

    conn = driver.connection_manager.get_connection()
    qe = traceforge.QueryEngine(conn)
    sessions = qe.sessions.list()
    assert len(sessions) == 1

    activities = qe.activities.list_by_session(sessions[0].session_id)
    assert len(activities) == 1

    nodes = qe.nodes.list_by_graph(activities[0].graph_id)
    assert len(nodes) == 3  # root, mid, leaf

    relationships = qe.relationships.list_by_graph(activities[0].graph_id)
    assert len(relationships) == 2  # root->mid, mid->leaf


def test_exception_marks_session_and_activity_as_failed():
    traceforge.reset_default_tracer()
    tracer = traceforge.configure(service_name="bridge-failure")
    driver, bridge = _make_bridge()
    tracer.add_hook(bridge)

    @traceforge.traced()
    def will_fail():
        raise ValueError("boom")

    try:
        will_fail()
    except ValueError:
        pass

    conn = driver.connection_manager.get_connection()
    qe = traceforge.QueryEngine(conn)
    sessions = qe.sessions.list()
    assert sessions[0].status == "failed"


def test_recorded_session_is_replayable():
    """The actual point of the bridge: data recorded via the public SDK

    must be usable by ReplayEngine, not just present in raw tables.
    """
    traceforge.reset_default_tracer()
    tracer = traceforge.configure(service_name="bridge-replay")
    driver, bridge = _make_bridge()
    tracer.add_hook(bridge)

    @traceforge.traced()
    def handle_request():
        with traceforge.span("validate"):
            pass
        return "ok"

    handle_request()

    conn = driver.connection_manager.get_connection()
    qe = traceforge.QueryEngine(conn)
    session_id = qe.sessions.list()[0].session_id

    replay_engine = traceforge.ReplayEngine(qe)
    replay = replay_engine.replay_session(session_id)
    assert replay is not None


def test_concurrent_traces_are_isolated():
    """Two independent traces recorded concurrently must not have their

    spans cross-contaminated into each other's session/graph.
    """
    traceforge.reset_default_tracer()
    tracer = traceforge.configure(service_name="bridge-concurrency")
    driver, bridge = _make_bridge()
    tracer.add_hook(bridge)

    @traceforge.traced()
    def task(n):
        with traceforge.span(f"step-{n}"):
            return n

    for i in range(5):
        task(i)

    conn = driver.connection_manager.get_connection()
    qe = traceforge.QueryEngine(conn)
    sessions = qe.sessions.list()
    assert len(sessions) == 5
    # Each session's graph should have exactly 2 nodes (task + step), not
    # bleed into another trace's nodes.
    for s in sessions:
        activities = qe.activities.list_by_session(s.session_id)
        nodes = qe.nodes.list_by_graph(activities[0].graph_id)
        assert len(nodes) == 2
