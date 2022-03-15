import pytest

from things_cloud.api.client import ThingsClient
from things_cloud.models.todo import Destination, TodoItem

ACCOUNT = ""  # TODO
OFFSET = 123
things = ThingsClient(ACCOUNT, initial_offset=123)


@pytest.mark.skip(reason="should put mocks in place")
def test_create():
    start_idx = things.offset
    assert start_idx == OFFSET
    item = TodoItem(title="test_create", destination=Destination.TODAY)
    new_idx = things.create(item)
    assert new_idx is not None
    assert new_idx == start_idx + 1
