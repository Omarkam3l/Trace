"""Assorted small helpers."""

from __future__ import annotations

from typing import Any


def truncate(text: str, max_length: int = 200) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length] + "...<truncated>"


def safe_repr(obj: Any, max_length: int = 200) -> str:
    try:
        return truncate(repr(obj), max_length)
    except Exception:  # noqa: BLE001
        return f"<unrepresentable:{type(obj).__name__}>"


def is_json_serializable(obj: Any) -> bool:
    import json

    try:
        json.dumps(obj)
        return True
    except (TypeError, ValueError):
        return False
