from datetime import datetime, timezone

import pytest

from things_cloud.api.client import ThingsClient
from things_cloud.models.todo import Destination, Note, Status, TodoItem, Type

ACCOUNT = ""  # TODO
OFFSET = 123
things = ThingsClient(ACCOUNT, initial_offset=123)


@pytest.mark.skip(reason="should put mocks in place")
def test_create():
    start_idx = things.offset
    assert start_idx == OFFSET
    item = TodoItem("test_create")
    new_idx = things.create(item)
    assert new_idx is not None
    assert new_idx == start_idx + 1


def test_process_new():
    things._items.clear()
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

    things._process_updates(data)
    todos = list(things._items.values())
    assert len(todos) == 1
    time = datetime(2022, 1, 3, 18, 29, 27, tzinfo=timezone.utc)
    todo = todos[0]
    assert todo._uuid == "aBCDiHyah4Uf0MQqp11jsX"
    assert todo._index == 1234
    assert todo._title == "test task"
    assert todo._status == Status.TODO
    assert todo._destination == Destination.ANYTIME
    assert todo._creation_date == time
    assert todo._modification_date == time
    assert todo._scheduled_date is None
    assert todo._today_index_reference_date is None
    assert todo._completion_date is None
    assert todo._due_date is None
    assert todo._trashed is False
    assert todo._instance_creation_paused is False
    assert todo._projects == ["ABCd1ee0ykmXYZqT98huxa"]
    assert todo._areas == []
    assert todo._is_evening == 0
    assert todo._tags == []
    assert todo._type == Type.TASK
    assert todo._due_date_suppression_date is None
    assert todo._repeating_template == []
    assert todo._repeater_migration_date is None
    assert todo._delegate == []
    assert todo._due_date_offset == 0
    assert todo._last_alarm_interaction_date is None
    assert todo._action_group == []
    assert todo._leaves_tombstone is False
    assert todo._instance_creation_count == 0
    assert todo._today_index == 0
    assert todo._reminder is None
    assert todo._instance_creation_start_date is None
    assert todo._repeater is None
    assert todo._after_completion_reference_date is None
    assert todo._recurrence_rule is None
    assert todo._note == Note()
    assert not todo._changes


def test_process_updated():
    things._items.clear()
    UUID = "aBCDiHyah4Uf0MQqp11jsX"
    todo = TodoItem("test original")
    todo._uuid = UUID
    things._items = {UUID: todo}
    data = {
        "items": [
            {
                UUID: {
                    "p": {"md": 1641234567.123456, "tt": "test updated"},
                    "e": "Task6",
                    "t": 1,
                }
            }
        ],
        "current-item-index": 1234,
        "schema": 301,
        "start-total-content-size": 0,
        "end-total-content-size": 1234567,
        "latest-total-content-size": 1234567,
    }

    things._process_updates(data)
    todos = things._items
    assert len(todos) == 1
    todo = todos[UUID]
    assert todo._uuid == UUID
    assert todo._title == "test updated"
    assert todo._modification_date == datetime(
        2022, 1, 3, 18, 29, 27, 123456, tzinfo=timezone.utc
    )
    assert not todo._changes


def test_process_multiple():
    things._items.clear()
    UUID1 = "aBCDiHyah4Uf0MQqp11js1"
    UUID2 = "aBCDiHyah4Uf0MQqp11js2"
    UUID3 = "aBCDiHyah4Uf0MQqp11js3"
    data = {
        "items": [
            # updated non-existant todo
            {
                UUID1: {
                    "p": {"md": 1641234567.123456, "tt": "test updated"},
                    "e": "Task6",
                    "t": 1,
                }
            },
            # new todo
            {
                UUID2: {
                    "p": {
                        "ix": 2,
                        "cd": 1641234567,
                        "icsd": None,
                        "ar": [],
                        "tir": None,
                        "rmd": None,
                        "pr": ["ABCd1ee0ykmXYZqT98huxa"],
                        "rp": None,
                        "rr": None,
                        "dds": None,
                        "tt": "task 2",
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
            },
            # new todo
            {
                UUID3: {
                    "p": {
                        "ix": 3,
                        "cd": 1641234567,
                        "icsd": None,
                        "ar": [],
                        "tir": None,
                        "rmd": None,
                        "pr": [],
                        "rp": None,
                        "rr": None,
                        "dds": None,
                        "tt": "task 3",
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
            },
        ],
        "current-item-index": 1234,
        "schema": 301,
        "start-total-content-size": 0,
        "end-total-content-size": 1234567,
        "latest-total-content-size": 1234567,
    }

    things._process_updates(data)
    todos = things._items
    assert len(todos) == 2
    todo2 = todos[UUID2]
    assert todo2._uuid == UUID2
    assert todo2._title == "task 2"
    todo3 = todos[UUID3]
    assert todo3._uuid == UUID3
    assert todo3._title == "task 3"
