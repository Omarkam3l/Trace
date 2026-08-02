"""Enumerations for Phase 5 Python Runtime Plugin."""

from __future__ import annotations

from enum import StrEnum


class ProfileType(StrEnum):
    """Recording profiles defining runtime observation scope."""

    MINIMAL = "minimal"
    STANDARD = "standard"
    DEEP_DEBUG = "deep_debug"
    CUSTOM = "custom"


class BackendType(StrEnum):
    """CPython instrumentation backend types."""

    PEP669 = "pep669"
    SETPROFILE = "setprofile"
    SETTRACE = "settrace"


class RuntimeNodeType(StrEnum):
    """Execution node classifications captured by the runtime plugin."""

    FUNCTION = "function"
    METHOD = "method"
    CLASS = "class"
    MODULE = "module"
    THREAD = "thread"
    ASYNC_TASK = "async_task"
    GENERATOR = "generator"
    CONTEXT_MANAGER = "context_manager"
    IMPORT = "import"
    EXCEPTION = "exception"
    VARIABLE = "variable"
    LINE = "line"
    EXPRESSION = "expression"
