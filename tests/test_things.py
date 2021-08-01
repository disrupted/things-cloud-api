import pytest
from todo import TodoItem

from things import Destination, create_todo, get_current_index


@pytest.mark.skip(reason="should put mocks in place")
def test_create():
    start_index = 1540
    current_index = get_current_index(start_index)
    assert current_index is not None
    assert current_index > start_index
    item = TodoItem(title="test_create", destination=Destination.TODAY)

    index = create_todo(current_index, item)
    assert index is not None
    assert index == current_index + 1
