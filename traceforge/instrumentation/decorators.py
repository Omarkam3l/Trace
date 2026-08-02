"""Decorators for function execution boundaries."""

from __future__ import annotations

import functools
import inspect
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from traceforge.instrumentation.service import InstrumentationService


def wrap_with_activity(
    service: InstrumentationService,
    fn: Callable[..., Any],
    activity_name: str | None = None,
) -> Callable[..., Any]:
    name = activity_name or fn.__name__

    if inspect.iscoroutinefunction(fn):

        @functools.wraps(fn)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            started = False
            try:
                if service.is_recording():
                    service.start_activity(name=name)
                    started = True
            except Exception:
                pass

            try:
                return await fn(*args, **kwargs)
            finally:
                if started:
                    try:
                        service.stop_activity()
                    except Exception:
                        pass

        return async_wrapper

    else:

        @functools.wraps(fn)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            started = False
            try:
                if service.is_recording():
                    service.start_activity(name=name)
                    started = True
            except Exception:
                pass

            try:
                return fn(*args, **kwargs)
            finally:
                if started:
                    try:
                        service.stop_activity()
                    except Exception:
                        pass

        return sync_wrapper
