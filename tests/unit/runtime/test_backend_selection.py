"""Unit tests for BackendSelector automatic resolution and explicit config overrides."""

from __future__ import annotations

import sys

from traceforge.runtime.backends.pep669 import PEP669Backend
from traceforge.runtime.backends.selector import BackendSelector
from traceforge.runtime.backends.setprofile import SetProfileBackend
from traceforge.runtime.backends.settrace import SetTraceBackend
from traceforge.runtime.config import RuntimeConfig
from traceforge.runtime.enums import BackendType, ProfileType
from traceforge.runtime.filter import RuntimeFilter


def dummy_emit(evt):
    pass


def test_explicit_backend_override():
    filt = RuntimeFilter()

    cfg_setprofile = RuntimeConfig(backend=BackendType.SETPROFILE)
    backend_sp = BackendSelector.select_backend(cfg_setprofile, dummy_emit, filt)
    assert isinstance(backend_sp, SetProfileBackend)

    cfg_settrace = RuntimeConfig(backend=BackendType.SETTRACE)
    backend_st = BackendSelector.select_backend(cfg_settrace, dummy_emit, filt)
    assert isinstance(backend_st, SetTraceBackend)


def test_deep_debug_profile_selects_settrace():
    filt = RuntimeFilter()
    cfg_deep = RuntimeConfig(profile=ProfileType.DEEP_DEBUG)
    backend = BackendSelector.select_backend(cfg_deep, dummy_emit, filt)
    assert isinstance(backend, SetTraceBackend)


def test_automatic_backend_selection_by_python_version():
    filt = RuntimeFilter()
    cfg_standard = RuntimeConfig(profile=ProfileType.STANDARD)
    backend = BackendSelector.select_backend(cfg_standard, dummy_emit, filt)

    if sys.version_info >= (3, 12) and hasattr(sys, "monitoring"):
        assert isinstance(backend, PEP669Backend)
    else:
        assert isinstance(backend, SetProfileBackend)
