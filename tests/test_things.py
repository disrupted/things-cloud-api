from datetime import datetime

import pytest

from things_cloud.api.client import ThingsClient
from things_cloud.models.todo import Destination, Note, Status, TodoItem

ACCOUNT = ""  # TODO
OFFSET = 123
things = ThingsClient(ACCOUNT, initial_offset=123)


@pytest.mark.skip(reason="should put mocks in place")
def test_create():
    start_idx = things.offset
    assert start_idx == OFFSET
    item = TodoItem(title="test_create", destination=Destination.ANYTIME)
    new_idx = things.create(item)
    assert new_idx is not None
    assert new_idx == start_idx + 1


def test_process_new():
    data = {
        "items": [
            {
                "aBCDiHyah4Uf0MQqp11jsX": {
                    "p": {
                        "ix": 1234,
                        "cd": 1641234567,
                        "icsd": None,
                        "ar": [],
                        "tir": None,
                        "rmd": None,
                        "pr": ["ABCd1ee0ykmXYZqT98huxa"],
                        "rp": None,
                        "rr": None,
                        "dds": None,
                        "tt": "test task",
                        "tr": False,
                        "tp": 0,
                        "lt": False,
                        "acrd": None,
                        "ti": 0,
                        "tg": [],
                        "icp": False,
                        "nt": {"ch": 0, "_t": "tx", "t": 0, "v": ""},
                        "do": 0,
                        "dl": [],
                        "lai": None,
                        "dd": None,
                        "rt": [],
                        "md": 1641234567,
                        "ss": 0,
                        "sr": None,
                        "sp": None,
                        "st": 1,
                        "icc": 0,
                        "ato": None,
                        "sb": 0,
                        "agr": [],
                    },
                    "e": "Task6",
                    "t": 0,
                }
            }
        ],
        "current-item-index": 1234,
        "schema": 301,
        "start-total-content-size": 0,
        "end-total-content-size": 1234567,
        "latest-total-content-size": 1234567,
    }

    todos = things._process_updates(data)
    assert len(todos) == 1
    time = datetime(2022, 1, 3, 19, 29, 27)
    todo = todos[0]
    assert todo._uuid == "aBCDiHyah4Uf0MQqp11jsX"
    assert todo._index == 1234
    assert todo._title == "test task"
    assert todo._status == Status.TODO
    assert todo._destination == Destination.ANYTIME
    assert todo._creation_date == time
    assert todo._modification_date == time
    assert todo._scheduled_date is None
    assert todo._tir is None
    assert todo._completion_date is None
    assert todo._due_date is None
    assert todo._trashed is False
    assert todo._is_project is False
    assert todo._projects == ["ABCd1ee0ykmXYZqT98huxa"]
    assert todo._areas == []
    assert todo._is_evening == 0
    assert todo._tags == []
    assert todo._tp == 0
    assert todo._dds is None
    assert todo._rt == []
    assert todo._rmd is None
    assert todo._dl == []
    assert todo._do == 0
    assert todo._lai is None
    assert todo._agr == []
    assert todo._lt is False
    assert todo._icc == 0
    assert todo._ti == 0
    assert todo._reminder is None
    assert todo._icsd is None
    assert todo._rp is None
    assert todo._acrd is None
    assert todo._rr is None
    assert todo._note == Note()
    assert not todo._changes
