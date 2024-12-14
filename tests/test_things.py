from datetime import datetime, timezone
from typing import Any

import pytest

from things_cloud.api.client import HistoryResponse, ThingsClient
from things_cloud.models.todo import (
    Destination,
    EditBody,
    NewBody,
    Note,
    Status,
    TodoItem,
    Type,
)

ACCOUNT = ""  # TODO
OFFSET = 123
things = ThingsClient(ACCOUNT, initial_offset=123)


@pytest.mark.skip(reason="should put mocks in place")
def test_create():
    start_idx = things.offset
    assert start_idx == OFFSET
    item = TodoItem(title="test_create")
    new_idx = things.commit(item)
    assert new_idx is not None
    assert new_idx == start_idx + 1


@pytest.fixture()
def history_data_new() -> dict[str, Any]:
    return {
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
        "start-total-content-size": 1,  # fake
        "end-total-content-size": 1234567,
        "latest-total-content-size": 1234567,
    }


@pytest.fixture()
def history_new(history_data_new: dict[str, Any]) -> HistoryResponse:
    return HistoryResponse.model_validate(history_data_new)


def test_deserialize_history_new(history_new: HistoryResponse):
    assert len(history_new.items) == 1
    updates = list(history_new.updates)
    assert len(updates) == 1
    assert all(isinstance(update.body, NewBody) for update in updates)


def test_process_new(history_new: HistoryResponse):
    things._items.clear()

    things._process_updates(history_new)
    todos = list(things._items.values())
    assert len(todos) == 1
    time = datetime(2022, 1, 3, 18, 29, 27, tzinfo=timezone.utc)
    todo = todos[0]
    assert todo.uuid == "aBCDiHyah4Uf0MQqp11jsX"
    assert todo.index == 1234
    assert todo.title == "test task"
    assert todo.status is Status.TODO
    assert todo.destination is Destination.ANYTIME
    assert todo.creation_date == time
    assert todo.modification_date == time
    assert todo.scheduled_date is None
    assert todo.today_index_reference_date is None
    assert todo.completion_date is None
    assert todo.due_date is None
    assert todo.trashed is False
    assert todo.instance_creation_paused is False
    assert todo._projects == ["ABCd1ee0ykmXYZqT98huxa"]
    assert todo._areas == []
    assert todo._evening is False
    assert todo.is_evening is False
    assert todo.tags == []
    assert todo._type == Type.TASK
    assert todo.due_date_suppression_date is None
    assert todo.repeating_template == []
    assert todo.repeater_migration_date is None
    assert todo.delegate == []
    assert todo.due_date_offset == 0
    assert todo.last_alarm_interaction_date is None
    assert todo.action_group == []
    assert todo.leaves_tombstone is False
    assert todo.instance_creation_count == 0
    assert todo.today_index == 0
    assert todo.reminder is None
    assert todo.instance_creation_start_date is None
    assert todo.repeater is None
    assert todo.after_completion_reference_date is None
    assert todo.recurrence_rule is None
    assert todo.note == Note()
    # assert not todo._changes


@pytest.fixture()
def history_data_edit() -> dict[str, Any]:
    return {
        "items": [
            {
                "aBCDiHyah4Uf0MQqp11jsX": {
                    "p": {"md": 1641234567.123456, "tt": "test updated"},
                    "e": "Task6",
                    "t": 1,
                }
            }
        ],
        "current-item-index": 1234,
        "schema": 301,
        "start-total-content-size": 1,
        "end-total-content-size": 1234567,
        "latest-total-content-size": 1234567,
    }


@pytest.fixture()
def history_edit(history_data_edit: dict[str, Any]) -> HistoryResponse:
    return HistoryResponse.model_validate(history_data_edit)


def test_deserialize_history_edit(history_edit: HistoryResponse):
    assert len(history_edit.items) == 1
    updates = list(history_edit.updates)
    assert len(updates) == 1
    assert all(isinstance(update.body, EditBody) for update in updates)


def test_process_updated(history_edit: HistoryResponse):
    things._items.clear()
    update = next(history_edit.updates)

    todo = TodoItem(title="test original")
    todo._uuid = update.id
    things._items[update.id] = todo

    things._process_updates(history_edit)
    assert len(things._items) == 1
    updated_todo = things._items[todo.uuid]
    assert updated_todo.uuid == todo.uuid
    assert updated_todo.title == "test updated"
    assert updated_todo.modification_date == datetime(
        2022, 1, 3, 18, 29, 27, 123456, tzinfo=timezone.utc
    )
    # assert not todo._changes


@pytest.fixture()
def history_data_mixed() -> dict[str, Any]:
    return {
        "items": [
            # updated non-existant todo
            # {
            #     "aBCDiHyah4Uf0MQqp11js1": {
            #         "p": {"md": 1641234567.123456, "tt": "test updated"},
            #         "e": "Task6",
            #         "t": 1,
            #     }
            # },
            # new todo
            {
                "aBCDiHyah4Uf0MQqp11js2": {
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
                "aBCDiHyah4Uf0MQqp11js3": {
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
        "start-total-content-size": 1,
        "end-total-content-size": 1234567,
        "latest-total-content-size": 1234567,
    }


@pytest.fixture()
def history_mixed(history_data_mixed: dict[str, Any]) -> HistoryResponse:
    return HistoryResponse.model_validate(history_data_mixed)


def test_process_multiple(history_mixed: HistoryResponse):
    things._items.clear()

    things._process_updates(history_mixed)
    todos = things._items
    UUID2 = "aBCDiHyah4Uf0MQqp11js2"
    UUID3 = "aBCDiHyah4Uf0MQqp11js3"

    assert len(todos) == 2
    todo2 = todos[UUID2]
    assert todo2.uuid == UUID2
    assert todo2.title == "task 2"
    todo3 = todos[UUID3]
    assert todo3.uuid == UUID3
    assert todo3.title == "task 3"
