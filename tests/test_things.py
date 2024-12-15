import json
import uuid
from datetime import datetime, timezone
from typing import Any

import pytest
from freezegun import freeze_time
from pydantic import SecretStr
from pytest_httpx import HTTPXMock

from things_cloud.api.account import Account, Credentials
from things_cloud.api.client import HistoryResponse, ThingsClient
from things_cloud.models.todo import (
    XX,
    Destination,
    EditBody,
    NewBody,
    Note,
    Status,
    TodoItem,
    Type,
)


@pytest.fixture()
def account_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture()
def account(account_id: uuid.UUID, httpx_mock: HTTPXMock) -> Account:
    credentials = Credentials(
        email="johndoe@example.com", password=SecretStr("example_f0$'@")
    )
    httpx_mock.add_response(
        200,
        json={
            "SLA-version-accepted": "5",
            "email": "johndoe@example.com",
            "history-key": str(account_id),
            "issues": [],
            "maildrop-email": "maildrop-does-not-exist@things.email",
            "status": "SYAccountStatusActive",
        },
    )
    account = Account.login(credentials)
    assert len(httpx_mock.get_requests()) == 1
    request = httpx_mock.get_request()
    assert request
    assert request.method == "GET"
    assert (
        request.url
        == "https://cloud.culturedcode.com/version/1/account/johndoe@example.com"
    )
    assert request.headers["Authorization"] == "Password example_f0%24'%40"
    return account


def test_login(account_id: uuid.UUID, account: Account):
    assert account._info.sla_version_accepted == "5"
    assert account._info.email == "johndoe@example.com"
    assert account._info.history_key == account_id
    assert account._info.issues == []
    assert account._info.maildrop_email == "maildrop-does-not-exist@things.email"
    assert account._info.status == "SYAccountStatusActive"


@pytest.fixture()
def things(account: Account, httpx_mock: HTTPXMock) -> ThingsClient:
    httpx_mock.reset()
    httpx_mock.add_response(
        201,
        json={"headIndex": 123, "historyKeySessionSecret": "fake"},
    )
    things = ThingsClient(account)
    request = httpx_mock.get_request()
    assert request
    assert request.method == "POST"
    assert (
        request.url
        == "https://cloud.culturedcode.com/api/account/login/getT3SharedSession"
    )
    assert (
        request.headers["Authorization"]
        == "B64SON eyJlcCI6IHsiZSI6ICJqb2huZG9lQGV4YW1wbGUuY29tIiwgInAiOiAiZXhhbXBsZV9mMCQnQCJ9fQ=="
    )
    return things


def test_client_session(things: ThingsClient):
    assert things._session.head_index == 123
    assert things._session.history_key_session_secret == "fake"


@pytest.fixture()
@freeze_time(datetime(2024, 12, 9, 12, 31, 46, 919961, tzinfo=timezone.utc))
def task() -> TodoItem:
    task = TodoItem(title="test_create")
    task._uuid = "tiqzvgT8m7ME4gooPqtdq3"  # overwrite uuid so that we can assert it
    return task


@freeze_time(datetime(2024, 12, 9, 12, 31, 47, 123456, tzinfo=timezone.utc))
def test_create(
    things: ThingsClient, task: TodoItem, account_id: uuid.UUID, httpx_mock: HTTPXMock
):
    start_idx = things._offset
    assert start_idx == 123

    httpx_mock.reset()
    httpx_mock.add_response(
        200,
        json={"server-head-index": 124},
    )
    things.commit(task)
    request = httpx_mock.get_request()
    assert request
    assert request.method == "POST"
    assert (
        request.url
        == f"https://cloud.culturedcode.com/version/1/history/{account_id}/commit?ancestor-index={start_idx}&_cnt=1"
    )
    assert json.loads(request.content) == {
        "tiqzvgT8m7ME4gooPqtdq3": {
            "t": 0,
            "p": {
                "ix": 0,
                "tt": "test_create",
                "ss": 0,
                "st": 0,
                "cd": 1733747506.919961,
                "md": 1733747507.123456,
                "sr": None,
                "tir": None,
                "sp": None,
                "dd": None,
                "tr": False,
                "icp": False,
                "pr": [],
                "ar": [],
                "sb": 0,
                "tg": [],
                "tp": 0,
                "dds": None,
                "rt": [],
                "rmd": None,
                "dl": [],
                "do": 0,
                "lai": None,
                "agr": [],
                "lt": False,
                "icc": 0,
                "ti": 0,
                "ato": None,
                "icsd": None,
                "rp": None,
                "acrd": None,
                "rr": None,
                "nt": {"_t": "tx", "ch": 0, "v": "", "t": 1},
                "xx": {"sn": {}, "_t": "oo"},
            },
            "e": "Task6",
        }
    }
    assert things._offset == start_idx + 1


@pytest.fixture()
def existing_task(task: TodoItem) -> TodoItem:
    new = task._to_new()
    # we simulate what happens when we commit the changes
    task._commit(new)
    assert task._synced_state
    return task


@freeze_time(datetime(2024, 12, 9, 12, 31, 59, 259910, tzinfo=timezone.utc))
def test_update(
    things: ThingsClient,
    existing_task: TodoItem,
    account_id: uuid.UUID,
    httpx_mock: HTTPXMock,
):
    start_idx = things._offset
    assert start_idx == 123

    httpx_mock.reset()
    httpx_mock.add_response(
        200,
        json={"server-head-index": 124},
    )
    existing_task.title = "test_update"
    things.commit(existing_task)
    request = httpx_mock.get_request()
    assert request
    assert request.method == "POST"
    assert (
        request.url
        == f"https://cloud.culturedcode.com/version/1/history/{account_id}/commit?ancestor-index=123&_cnt=1"
    )
    assert json.loads(request.content) == {
        "tiqzvgT8m7ME4gooPqtdq3": {
            "t": 1,
            "p": {
                "tt": "test_update",
                "md": 1733747519.25991,
            },
            "e": "Task6",
        }
    }
    assert things._offset == start_idx + 1


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
                        "nt": {"ch": 0, "_t": "tx", "t": 1, "v": ""},
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
                        "xx": {"sn": {}, "_t": "oo"},
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


def test_history_new(things: ThingsClient, history_new: HistoryResponse):
    things._items.clear()

    things._process_history(history_new)
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
    assert todo.xx == XX()
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


def test_history_edit(things: ThingsClient, history_edit: HistoryResponse):
    things._items.clear()
    update = next(history_edit.updates)

    todo = TodoItem(title="test original")
    todo._uuid = update.id
    things._items[update.id] = todo

    things._process_history(history_edit)
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
                        "xx": {"sn": {}, "_t": "oo"},
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
                        "xx": {"sn": {}, "_t": "oo"},
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


def test_history_mixed(things: ThingsClient, history_mixed: HistoryResponse):
    things._items.clear()

    things._process_history(history_mixed)
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
