"""Reversible monkey-patching utilities for plugins."""

from __future__ import annotations

import threading
from collections.abc import Callable
from typing import Any

_patch_registry: dict[tuple[int, str], Any] = {}
_lock = threading.RLock()


def patch_attribute(target: Any, attribute_name: str, replacement: Any) -> Callable[[], None]:
    """Safely replace target.attribute_name with replacement, returning an unpatch callback."""
    with _lock:
        key = (id(target), attribute_name)
        if key not in _patch_registry:
            original = getattr(target, attribute_name)
            _patch_registry[key] = original

        setattr(target, attribute_name, replacement)

    def unpatch() -> None:
        restore_attribute(target, attribute_name)

    return unpatch


def restore_attribute(target: Any, attribute_name: str) -> None:
    """Restore target.attribute_name to its original pre-patched value."""
    with _lock:
        key = (id(target), attribute_name)
        if key in _patch_registry:
            original = _patch_registry.pop(key)
            setattr(target, attribute_name, original)
