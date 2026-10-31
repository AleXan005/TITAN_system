"""Fixtures compartidas por todos los tests."""

import pytest

from storage import create_sqlite_storage


@pytest.fixture
def storage():
    """Base SQLite en memoria, nueva en cada test."""
    st = create_sqlite_storage(":memory:")
    yield st
    st.close()
