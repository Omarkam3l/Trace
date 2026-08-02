"""Unit tests for multi-threaded and asyncio runtime tracing isolation."""

from __future__ import annotations

import asyncio
import concurrent.futures

import pytest

from traceforge.engine.recorder import Recorder
from traceforge.plugins.manager import PluginManager
from traceforge.runtime.config import RuntimeConfig
from traceforge.runtime.enums import BackendType
from traceforge.runtime.plugin import PythonRuntimePlugin


def test_multithreaded_function_observation():
    recorder = Recorder()
    recorder.start_session()

    cfg = RuntimeConfig(backend=BackendType.SETPROFILE, include=["test_concurrency_and_asyncio.*"])
    plugin = PythonRuntimePlugin(config=cfg)
    manager = PluginManager(recorder=recorder)
    manager.register_plugin(plugin)
    manager.enable_plugin(plugin)

    def thread_worker(worker_id: int):
        def inner_func():
            return worker_id * 10
        return inner_func()

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(thread_worker, i) for i in range(3)]
        results = [f.result() for f in futures]

    assert results == [0, 10, 20]

    manager.disable_plugin(plugin)
    session = recorder.stop_session()
    assert session.status == session.status.COMPLETED


@pytest.mark.asyncio
async def test_asyncio_task_observation():
    recorder = Recorder()
    recorder.start_session()

    cfg = RuntimeConfig(backend=BackendType.SETPROFILE, include=["test_concurrency_and_asyncio.*"])
    plugin = PythonRuntimePlugin(config=cfg)
    manager = PluginManager(recorder=recorder)
    manager.register_plugin(plugin)
    manager.enable_plugin(plugin)

    async def async_worker(task_id: str):
        await asyncio.sleep(0.001)
        return f"done_{task_id}"

    res_a, res_b = await asyncio.gather(async_worker("a"), async_worker("b"))
    assert res_a == "done_a"
    assert res_b == "done_b"

    manager.disable_plugin(plugin)
    session = recorder.stop_session()
    assert session.status == session.status.COMPLETED
