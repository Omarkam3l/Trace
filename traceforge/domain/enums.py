"""Enumerations for Phase 1.5 Execution Domain Model."""

from __future__ import annotations

from enum import StrEnum


class NodeType(StrEnum):
    """The type of atomic execution node."""

    FUNCTION_CALL = "function_call"
    HTTP_REQUEST = "http_request"
    HTTP_RESPONSE = "http_response"
    DATABASE_QUERY = "database_query"
    REDIS_OPERATION = "redis_operation"
    CACHE_LOOKUP = "cache_lookup"
    LLM_CALL = "llm_call"
    FILESYSTEM_READ = "filesystem_read"
    FILESYSTEM_WRITE = "filesystem_write"
    MESSAGE_QUEUE_PUBLISH = "message_queue_publish"
    MESSAGE_QUEUE_CONSUME = "message_queue_consume"
    EXCEPTION = "exception"
    CONDITIONAL_BRANCH = "conditional_branch"
    LOOP = "loop"
    CUSTOM_BUSINESS_STEP = "custom_business_step"
    FRAMEWORK_LIFECYCLE_HOOK = "framework_lifecycle_hook"
    RENDER = "render"
    WIDGET_BUILD = "widget_build"
    BACKGROUND_TASK = "background_task"
    THREAD_SPAWN = "thread_spawn"
    OTHER = "other"


class NodeStatus(StrEnum):
    """The status of an execution node."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ActivityStatus(StrEnum):
    """The status of an activity."""

    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SessionStatus(StrEnum):
    """The status of a recording session."""

    RECORDING = "recording"
    STOPPED = "stopped"
    COMPLETED = "completed"
    FAILED = "failed"


class RelationshipType(StrEnum):
    """The directional relationship type between execution nodes."""

    PARENT_CHILD = "parent_child"
    DEPENDENCY = "dependency"
    PREVIOUS_NEXT = "previous_next"


class SourceType(StrEnum):
    """The source runtime or plugin that emitted an execution node."""

    PYTHON_SDK = "python_sdk"
    NODE_SDK = "node_sdk"
    FASTAPI_PLUGIN = "fastapi_plugin"
    REACT_PLUGIN = "react_plugin"
    FLUTTER_PLUGIN = "flutter_plugin"
    SQL_PLUGIN = "sql_plugin"
    REDIS_PLUGIN = "redis_plugin"
    FILESYSTEM_PLUGIN = "filesystem_plugin"
    MANUAL_INSTRUMENTATION = "manual_instrumentation"
    UNKNOWN = "unknown"
