"""Unit tests for RuntimeFilter wildcard include/exclude pattern matching."""

from __future__ import annotations

from traceforge.runtime.filter import RuntimeFilter


def test_runtime_filter_include_and_exclude():
    filt = RuntimeFilter(
        include=["my_app.*", "services.*"],
        exclude=["*.vendor", "site-packages.*"],
    )

    # Included modules
    assert filt.should_trace(module_name="my_app.orders", filename="orders.py", func_name="checkout")
    assert filt.should_trace(module_name="services.auth", filename="auth.py", func_name="login")

    # Excluded modules
    assert not filt.should_trace(module_name="my_app.vendor", filename="vendor.py", func_name="helper")
    assert not filt.should_trace(module_name="site-packages.requests", filename="requests.py", func_name="get")

    # Unlisted modules when include patterns are active
    assert not filt.should_trace(module_name="other_lib.core", filename="core.py", func_name="run")


def test_runtime_filter_exclude_only():
    filt = RuntimeFilter(exclude=["asyncio.*", "threading.*"])

    assert filt.should_trace(module_name="my_app.main", filename="main.py")
    assert not filt.should_trace(module_name="asyncio.tasks", filename="tasks.py")
    assert not filt.should_trace(module_name="threading", filename="threading.py")
