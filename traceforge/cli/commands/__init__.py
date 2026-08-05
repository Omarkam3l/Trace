"""CLI commands package."""

from traceforge.cli.commands import (
    config,
    diff,
    export,
    init,
    replay,
    server,
    version,
    visualize,
)

COMMAND_MODULES = [
    init,
    server,
    replay,
    diff,
    export,
    visualize,
    config,
    version,
]

__all__ = ["COMMAND_MODULES"]
