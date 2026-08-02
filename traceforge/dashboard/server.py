"""Reserved for a future release. Not implemented in the SDK-core milestone.

See traceforge/dashboard/__init__.py and docs/roadmap.md.
"""

from __future__ import annotations


def _not_implemented() -> None:
    raise NotImplementedError(
        "traceforge.dashboard.server is reserved for a future release "
        "and is not part of the current SDK-core milestone."
    )
