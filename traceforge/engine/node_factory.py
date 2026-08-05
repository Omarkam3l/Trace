"""NodeFactory: transforms RawEvents into immutable ExecutionNodes."""

from __future__ import annotations


from traceforge.domain.enums import NodeStatus, NodeType, SourceType
from traceforge.domain.metadata import Metadata
from traceforge.domain.node import ExecutionNode
from traceforge.engine.raw_event import RawEvent

_TYPE_MAP: dict[str, NodeType] = {
    "FunctionEntered": NodeType.FUNCTION_CALL,
    "FunctionReturned": NodeType.FUNCTION_CALL,
    "HTTPRequest": NodeType.HTTP_REQUEST,
    "HTTPResponse": NodeType.HTTP_RESPONSE,
    "SQLQuery": NodeType.DATABASE_QUERY,
    "RedisCall": NodeType.REDIS_OPERATION,
    "CacheLookup": NodeType.CACHE_LOOKUP,
    "LLMCall": NodeType.LLM_CALL,
    "FilesystemRead": NodeType.FILESYSTEM_READ,
    "FilesystemWrite": NodeType.FILESYSTEM_WRITE,
    "MessageQueuePublish": NodeType.MESSAGE_QUEUE_PUBLISH,
    "MessageQueueConsume": NodeType.MESSAGE_QUEUE_CONSUME,
    "ExceptionThrown": NodeType.EXCEPTION,
    "ConditionalBranch": NodeType.CONDITIONAL_BRANCH,
    "Loop": NodeType.LOOP,
    "Custom": NodeType.CUSTOM_BUSINESS_STEP,
    "FrameworkLifecycleHook": NodeType.FRAMEWORK_LIFECYCLE_HOOK,
    "Render": NodeType.RENDER,
    "WidgetBuild": NodeType.WIDGET_BUILD,
    "BackgroundTask": NodeType.BACKGROUND_TASK,
    "ThreadSpawn": NodeType.THREAD_SPAWN,
}


class NodeFactory:
    """Transforms RawEvents into validated, immutable ExecutionNode entities."""

    @staticmethod
    def map_event_type(event_type: str) -> NodeType:
        if event_type in _TYPE_MAP:
            return _TYPE_MAP[event_type]
        try:
            return NodeType(event_type.lower())
        except ValueError:
            return NodeType.OTHER

    @classmethod
    def create_node(
        cls,
        raw_event: RawEvent,
        graph_id: str,
        parent_id: str | None = None,
    ) -> ExecutionNode:
        try:
            node_type = cls.map_event_type(raw_event.type)
            name = str(raw_event.payload.get("name") or raw_event.type)

            status_str = str(raw_event.payload.get("status", "completed")).lower()
            try:
                status = NodeStatus(status_str)
            except ValueError:
                status = NodeStatus.COMPLETED

            duration_ms = raw_event.payload.get("duration_ms")
            if duration_ms is not None:
                duration_ms = max(0.0, float(duration_ms))

            inputs = dict(raw_event.payload.get("inputs") or {})
            outputs = dict(raw_event.payload.get("outputs") or {})

            metadata_dict = dict(raw_event.metadata)
            if "exception" in raw_event.payload:
                metadata_dict["exception"] = raw_event.payload["exception"]

            source = raw_event.source
            if isinstance(source, str):
                try:
                    source = SourceType(source)
                except ValueError:
                    source = SourceType.UNKNOWN

            return ExecutionNode(
                node_id=raw_event.event_id,
                graph_id=graph_id,
                type=node_type,
                name=name,
                started_at=raw_event.timestamp,
                finished_at=raw_event.timestamp,
                duration_ms=duration_ms,
                status=status,
                parent_id=parent_id,
                child_ids=[],
                inputs=inputs,
                outputs=outputs,
                metadata=Metadata(attributes=metadata_dict),
                tags=set(raw_event.payload.get("tags") or []),
                source=source,
            )

        except Exception as exc:
            # Malformed raw event fallback node
            return ExecutionNode(
                node_id=raw_event.event_id or "error_node",
                graph_id=graph_id,
                type=NodeType.OTHER,
                name=f"Malformed:{raw_event.type}",
                started_at=raw_event.timestamp,
                finished_at=raw_event.timestamp,
                status=NodeStatus.FAILED,
                parent_id=parent_id,
                metadata=Metadata(
                    attributes={
                        "raw_event_error": str(exc),
                        "original_event_type": raw_event.type,
                    }
                ),
                source=SourceType.UNKNOWN,
            )
