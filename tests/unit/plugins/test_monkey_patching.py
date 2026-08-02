"""Unit tests for reversible monkey-patching utilities."""

from __future__ import annotations

from traceforge.plugins.patching import patch_attribute, restore_attribute


class SampleTarget:
    def greet(self) -> str:
        return "hello"


def test_reversible_monkey_patching():
    target = SampleTarget()
    assert target.greet() == "hello"

    def patched_greet() -> str:
        return "patched"

    unpatch = patch_attribute(target, "greet", patched_greet)
    assert target.greet() == "patched"

    # Unpatch restores original method
    unpatch()
    assert target.greet() == "hello"

    # Repeated patch and restore
    patch_attribute(target, "greet", patched_greet)
    assert target.greet() == "patched"
    restore_attribute(target, "greet")
    assert target.greet() == "hello"
