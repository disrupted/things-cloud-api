import pytest

from things import Destination, create_todo_todo, get_current_index


def test_create():
    start_index = 1540
    current_index = get_current_index(start_index)
    assert current_index is not None
    assert current_index > start_index

    index = create_todo_todo(
        current_index, title="test_create", destination=Destination.TODAY
    )
    assert index is not None
    assert index == current_index + 1
