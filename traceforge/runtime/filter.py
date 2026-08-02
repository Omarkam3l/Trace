"""RuntimeFilter for include/exclude wildcard pattern evaluation."""

from __future__ import annotations

import fnmatch
from typing import Any


class RuntimeFilter:
    """Evaluates wildcard include and exclude patterns against module, file, and function targets."""

    def __init__(self, include: list[str] | None = None, exclude: list[str] | None = None) -> None:
        self._include = list(include or [])
        self._exclude = list(exclude or [])

    def should_trace(self, module_name: str | None, filename: str | None, func_name: str | None = None) -> bool:
        """Return True if the target matches include patterns and does not match exclude patterns."""
        mod = module_name or ""
        fname = filename or ""
        func = func_name or ""
        target_str = f"{mod}.{func}" if mod and func else (mod or fname)

        # 1. Check exclude patterns
        for pattern in self._exclude:
            if fnmatch.fnmatch(mod, pattern) or fnmatch.fnmatch(fname, pattern) or fnmatch.fnmatch(target_str, pattern):
                return False

        # 2. Check include patterns (if specified, target must match at least one)
        if self._include:
            matched = False
            for pattern in self._include:
                if fnmatch.fnmatch(mod, pattern) or fnmatch.fnmatch(fname, pattern) or fnmatch.fnmatch(target_str, pattern):
                    matched = True
                    break
            if not matched:
                return False

        return True
