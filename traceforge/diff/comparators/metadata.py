"""MetadataDiffComparator for environment and profile metadata comparison."""

from __future__ import annotations

from typing import TYPE_CHECKING

from traceforge.diff.report import MetadataDiff

if TYPE_CHECKING:
    from traceforge.replay.session import ReplaySession


class MetadataDiffComparator:
    """Compares session environment and profile metadata."""

    def compare(self, baseline: ReplaySession, target: ReplaySession) -> MetadataDiff:
        """Compare OS, Python version, and profile names."""
        b_sess = baseline.session
        t_sess = target.session

        os_changed = (b_sess.environment_os != t_sess.environment_os) if (b_sess and t_sess) else False
        py_changed = (b_sess.environment_python != t_sess.environment_python) if (b_sess and t_sess) else False
        prof_changed = (b_sess.profile_name != t_sess.profile_name) if (b_sess and t_sess) else False

        return MetadataDiff(
            environment_os_changed=os_changed,
            environment_python_changed=py_changed,
            profile_name_changed=prof_changed,
        )
