"""Unit tests for immutable Batch model."""

from __future__ import annotations

import pytest

from traceforge.storage.batch import Batch


def test_batch_immutability_and_metadata():
    batch = Batch(
        batch_id="b1",
        records=("rec1", "rec2", "rec3"),
        record_count=3,
    )
    assert batch.batch_id == "b1"
    assert batch.record_count == 3
    assert batch.records == ("rec1", "rec2", "rec3")

    with pytest.raises(Exception):
        batch.batch_id = "modified"

    with pytest.raises(Exception):
        batch.record_count = 10
