"""Regression tests: traceforge exports two unrelated classes both effectively

called "Tracer" -- traceforge.Tracer (traceforge.core.tracer.Tracer, the
primary/documented tracing API) and the class behind traceforge.trace
(traceforge.instrumentation.tracer.Tracer, a separate session/activity
recording API). Before this fix, `traceforge.trace` sat at the top level
with no naming signal that it was a different, unrelated system -- someone
reaching for "the tracer" could easily grab the wrong one.

This fix renames the top-level singleton to `instrumentation_trace` and
keeps `traceforge.trace` working as a deprecated, warning-emitting alias
rather than breaking it outright.
"""

from __future__ import annotations

import warnings

import traceforge


def test_instrumentation_trace_and_core_tracer_are_different_classes():
    """This is the underlying confusion the rename addresses -- document it

    explicitly so it can't silently regress back into looking like one unified
    API.
    """
    core_tracer = traceforge.configure(service_name="naming-test")
    assert type(core_tracer) is not type(traceforge.instrumentation_trace)  # noqa: E721
    assert type(core_tracer).__module__ == "traceforge.core.tracer"
    assert type(traceforge.instrumentation_trace).__module__ == "traceforge.instrumentation.tracer"


def test_instrumentation_trace_accessible_without_warning():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        _ = traceforge.instrumentation_trace
    assert len(w) == 0


def test_deprecated_trace_alias_still_works():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        old = traceforge.trace
    assert old is traceforge.instrumentation_trace


def test_deprecated_trace_alias_warns():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        _ = traceforge.trace
    assert any(issubclass(x.category, DeprecationWarning) for x in w)
    assert any("instrumentation_trace" in str(x.message) for x in w)


def test_unknown_top_level_attribute_still_raises_attributeerror():
    """The __getattr__ shim must not swallow genuine typos."""
    import pytest

    with pytest.raises(AttributeError):
        _ = traceforge.this_does_not_exist_and_never_will


def test_star_import_still_works():
    """Regression guard: __all__ referencing an undefined name previously

    broke `from traceforge import *` entirely (see the __version__ bug).
    Make sure the rename didn't reintroduce that class of bug.
    """
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "-c", "from traceforge import *; print(instrumentation_trace)"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
