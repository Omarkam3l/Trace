"""Unit tests for Pagination model validation."""

from __future__ import annotations

import pytest

from traceforge.query.exceptions import InvalidQueryError
from traceforge.query.pagination import Pagination


def test_pagination_validation():
    pag = Pagination(limit=50, offset=10)
    assert pag.limit == 50
    assert pag.offset == 10

    with pytest.raises(InvalidQueryError):
        Pagination(limit=0)

    with pytest.raises(InvalidQueryError):
        Pagination(offset=-1)
