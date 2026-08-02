"""Unit tests for RecordingContextManager across nested sync, async, and thread contexts."""

from __future__ import annotations

import asyncio
import concurrent.futures

import pytest

from traceforge.engine.context_manager import RecordingContextManager


def test_nested_sync_contexts():
    manager = RecordingContextManager()
    assert manager.get_current_context_id() is None

    with manager.push_scope("ctx_outer", parent_node_id="node_root"):
        assert manager.get_current_context_id() == "ctx_outer"
        assert manager.get_current_parent_node_id() == "node_root"

        with manager.push_scope("ctx_inner", parent_node_id="node_child"):
            assert manager.get_current_context_id() == "ctx_inner"
            assert manager.get_current_parent_node_id() == "node_child"

        assert manager.get_current_context_id() == "ctx_outer"

    assert manager.get_current_context_id() is None


@pytest.mark.asyncio
async def test_async_contexts_isolation():
    manager = RecordingContextManager()
    results = {}

    async def task_worker(task_name: str):
        with manager.push_scope(f"ctx_{task_name}", parent_node_id=f"parent_{task_name}"):
            await asyncio.sleep(0.01)
            results[task_name] = (manager.get_current_context_id(), manager.get_current_parent_node_id())

    await asyncio.gather(task_worker("task_a"), task_worker("task_b"))

    assert results["task_a"] == ("ctx_task_a", "parent_task_a")
    assert results["task_b"] == ("ctx_task_b", "parent_task_b")


def test_thread_contexts_isolation():
    manager = RecordingContextManager()
    results = {}

    def thread_worker(thread_name: str):
        with manager.push_scope(f"ctx_{thread_name}", parent_node_id=f"p_{thread_name}"):
            results[thread_name] = (manager.get_current_context_id(), manager.get_current_parent_node_id())

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(thread_worker, f"t{i}") for i in range(3)]
        concurrent.futures.wait(futures)

    assert results["t0"] == ("ctx_t0", "p_t0")
    assert results["t1"] == ("ctx_t1", "p_t1")
    assert results["t2"] == ("ctx_t2", "p_t2")
