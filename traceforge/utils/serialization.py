"""JSON serialization helpers for TraceForge's data models."""

from __future__ import annotations

import json
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel


def to_jsonable(obj: Any) -> Any:
    """Recursively convert an object into plain JSON-compatible types."""
    if isinstance(obj, BaseModel):
        return json.loads(obj.model_dump_json())
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, dict):
        return {str(k): to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, list | tuple | set):
        return [to_jsonable(v) for v in obj]
    return obj


def dumps(obj: Any, **kwargs: Any) -> str:
    """``json.dumps`` that understands pydantic models, datetimes, and enums."""
    return json.dumps(to_jsonable(obj), **kwargs)
