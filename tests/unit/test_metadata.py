"""Unit tests for traceforge.models.metadata (attribute sanitization)."""

from __future__ import annotations

from traceforge.models.metadata import ExceptionInfo, sanitize_attributes


def test_none_returns_empty_dict():
    assert sanitize_attributes(None) == {}


def test_primitives_pass_through():
    attrs = {"s": "x", "i": 1, "f": 1.5, "b": True, "n": None}
    assert sanitize_attributes(attrs) == attrs


def test_long_strings_are_truncated():
    long_string = "x" * 20000
    result = sanitize_attributes({"k": long_string})
    assert len(result["k"]) <= 8192 + len("...<truncated>")
    assert result["k"].endswith("...<truncated>")


def test_non_serializable_value_falls_back_to_repr():
    class Weird:
        def __repr__(self):
            return "<Weird!>"

    result = sanitize_attributes({"k": Weird()})
    assert result["k"] == "<Weird!>"


def test_nested_dict_and_list_are_sanitized():
    result = sanitize_attributes({"nested": {"a": [1, 2, {"b": 3}]}})
    assert result == {"nested": {"a": [1, 2, {"b": 3}]}}


def test_too_many_keys_are_capped():
    attrs = {f"k{i}": i for i in range(500)}
    result = sanitize_attributes(attrs)
    assert len(result) == 256


def test_keys_are_coerced_to_strings():
    result = sanitize_attributes({1: "one"})  # type: ignore[dict-item]
    assert result == {"1": "one"}


def test_exception_info_from_exception():
    try:
        raise ValueError("bad input")
    except ValueError as exc:
        info = ExceptionInfo.from_exception(exc)
    assert info.type == "ValueError"
    assert info.message == "bad input"
    assert "ValueError: bad input" in info.stacktrace
