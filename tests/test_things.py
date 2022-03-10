import pytest

from things_cloud import ThingsClient
from things_cloud.todo import Destination, TodoItem

ACCOUNT = ""  # TODO
things = ThingsClient(ACCOUNT)


@pytest.mark.skip(reason="should put mocks in place")
def test_create():
    start_index = 123
    current_idx = things._offset
    assert current_idx is not None
    assert current_idx > start_index
    item = TodoItem(title="test_create", destination=Destination.TODAY)
    new_idx = things.create(item)
    assert new_idx is not None
    assert new_idx == current_idx + 1
