"""Unit tests for traceforge.core.context."""

from __future__ import annotations

from traceforge.core.context import ContextManager, ExecutionContext


def test_default_context_is_empty():
    ctx = ContextManager.get_current()
    assert ctx.is_empty()


def test_set_and_get_current():
    new_ctx = ExecutionContext(trace_id="t1", span_id="s1")
    token = ContextManager.set_current(new_ctx)
    try:
        assert ContextManager.get_current() == new_ctx
    finally:
        ContextManager.reset(token)


def test_reset_restores_previous_context():
    ctx1 = ExecutionContext(trace_id="t1", span_id="s1")
    token1 = ContextManager.set_current(ctx1)
    ctx2 = ExecutionContext(trace_id="t2", span_id="s2")
    token2 = ContextManager.set_current(ctx2)

    ContextManager.reset(token2)
    assert ContextManager.get_current() == ctx1

    ContextManager.reset(token1)
    assert ContextManager.get_current().is_empty()


async def test_context_is_isolated_across_asyncio_tasks():
    import asyncio

    results = {}

    async def worker(name: str, trace_id: str):
        token = ContextManager.set_current(ExecutionContext(trace_id=trace_id))
        await asyncio.sleep(0.01)
        results[name] = ContextManager.get_current().trace_id
        ContextManager.reset(token)

    await asyncio.gather(worker("a", "trace-a"), worker("b", "trace-b"))
    assert results == {"a": "trace-a", "b": "trace-b"}


def test_context_is_isolated_across_threads():
    import threading

    results = {}

    def worker(name: str, trace_id: str):
        token = ContextManager.set_current(ExecutionContext(trace_id=trace_id))
        results[name] = ContextManager.get_current().trace_id
        ContextManager.reset(token)

    threads = [threading.Thread(target=worker, args=(f"t{i}", f"trace-{i}")) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert results == {f"t{i}": f"trace-{i}" for i in range(5)}
