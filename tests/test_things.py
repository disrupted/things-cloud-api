import pytest

from things import create, get_current_index


def test_create():
    start_index = 1540
    current_index = get_current_index(start_index)
    assert current_index is not None
    assert current_index > start_index

    index = create(current_index, title="test_create")
    assert index is not None
    assert index == current_index + 1
