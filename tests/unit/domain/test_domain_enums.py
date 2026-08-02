"""Unit tests for Phase 1.5 domain enumerations."""

from __future__ import annotations

from traceforge.domain.enums import (
    ActivityStatus,
    NodeStatus,
    NodeType,
    RelationshipType,
    SessionStatus,
    SourceType,
)


def test_node_type_values():
    assert NodeType.FUNCTION_CALL == "function_call"
    assert NodeType.HTTP_REQUEST == "http_request"
    assert NodeType.DATABASE_QUERY == "database_query"
    assert NodeType.OTHER == "other"


def test_node_status_values():
    assert NodeStatus.PENDING == "pending"
    assert NodeStatus.RUNNING == "running"
    assert NodeStatus.COMPLETED == "completed"
    assert NodeStatus.FAILED == "failed"
    assert NodeStatus.CANCELLED == "cancelled"


def test_activity_status_values():
    assert ActivityStatus.ACTIVE == "active"
    assert ActivityStatus.COMPLETED == "completed"
    assert ActivityStatus.FAILED == "failed"
    assert ActivityStatus.CANCELLED == "cancelled"


def test_session_status_values():
    assert SessionStatus.RECORDING == "recording"
    assert SessionStatus.STOPPED == "stopped"
    assert SessionStatus.COMPLETED == "completed"
    assert SessionStatus.FAILED == "failed"


def test_relationship_type_values():
    assert RelationshipType.PARENT_CHILD == "parent_child"
    assert RelationshipType.DEPENDENCY == "dependency"
    assert RelationshipType.PREVIOUS_NEXT == "previous_next"


def test_source_type_values():
    assert SourceType.PYTHON_SDK == "python_sdk"
    assert SourceType.FASTAPI_PLUGIN == "fastapi_plugin"
    assert SourceType.MANUAL_INSTRUMENTATION == "manual_instrumentation"
