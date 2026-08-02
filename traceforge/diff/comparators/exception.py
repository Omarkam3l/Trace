"""ExceptionDiffComparator for error state and captured exception comparison."""

from __future__ import annotations

from typing import TYPE_CHECKING

from traceforge.diff.report import ExceptionDiff

if TYPE_CHECKING:
    from traceforge.replay.session import ReplaySession


class ExceptionDiffComparator:
    """Compares error states and captured exceptions between baseline and target sessions."""

    def compare(self, baseline: ReplaySession, target: ReplaySession) -> ExceptionDiff:
        """Identify added and removed exception states deterministically."""
        base_errs = {f"{n.name}:{n.status}" for n in baseline.nodes if n.status == "error"}
        target_errs = {f"{n.name}:{n.status}" for n in target.nodes if n.status == "error"}

        added = sorted(list(target_errs - base_errs))
        removed = sorted(list(base_errs - target_errs))

        return ExceptionDiff(
            added_exceptions=added,
            removed_exceptions=removed,
        )
