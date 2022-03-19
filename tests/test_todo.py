import datetime as dt

import pytest
from attrs import asdict

from things_cloud.models.serde import TodoSerde
from things_cloud.models.todo import Destination, Status, TodoItem, serialize_dict
from things_cloud.utils import Util

FAKE_TIME = dt.datetime(2021, 1, 1)


@pytest.fixture(autouse=True)
def todo(monkeypatch):
    monkeypatch.setattr("things_cloud.utils.Util.now", lambda: FAKE_TIME)


def test_mocked_now():
    assert Util.now() == FAKE_TIME


@pytest.mark.skip("fix Util.now mock")
def test_todo_schema_create():
    item = TodoItem("test")

    d = {
        "index": 0,
        "title": "test",
        "status": Status.TODO,
        "destination": Destination.INBOX,
        "creation_date": FAKE_TIME,
        "modification_date": FAKE_TIME,
        "scheduled_date": None,
        "completion_date": None,
        "acrd": None,
        "agr": [],
        "areas": [],
        "reminder": None,
        "due_date": None,
        "dds": None,
        "dl": [],
        "do": 0,
        "icc": 0,
        "is_project": False,
        "icsd": None,
        "lai": None,
        "lt": False,
        "note": {"_t": "tx", "ch": 0, "t": 0, "v": ""},
        "projects": [],
        "rmd": None,
        "rp": None,
        "rr": None,
        "rt": [],
        "is_evening": 0,
        "tags": [],
        "ti": 0,
        "tir": None,
        "tp": 0,
        "in_trash": False,
    }
    timestamp = TodoSerde.timestamp_rounded(FAKE_TIME)
    d_alias = {
        "ix": 0,
        "tt": "test",
        "st": 0,
        "cd": timestamp,
        "md": FAKE_TIME,
        "sr": None,
        "ss": 0,
        "acrd": None,
        "agr": [],
        "ar": [],
        "ato": None,
        "dd": None,
        "dds": None,
        "dl": [],
        "do": 0,
        "icc": 0,
        "icp": False,
        "icsd": None,
        "lai": None,
        "lt": False,
        "nt": {"_t": "tx", "ch": 0, "t": 0, "v": ""},
        "pr": [],
        "rmd": None,
        "rp": None,
        "rr": None,
        "rt": [],
        "sb": 0,
        "sp": None,
        "tg": [],
        "ti": 0,
        "tir": None,
        "tp": 0,
        "tr": False,
    }

    assert asdict(item) == d
    assert serialize_dict(item) == d_alias


def test_as_project():
    project = TodoItem().as_project()
    assert project._is_project is True
    assert project.destination == Destination.ANYTIME
    assert project.changes == {
        "_destination",
        "_is_project",
        "_tp",
        "_modification_date",
    }


def test_assign_project():
    todo = TodoItem("test task")
    todo.project = "test-project"
    assert todo._projects == ["test-project"]
    assert todo.project == "test-project"
    assert todo._areas == []
    assert todo.area is None
    assert todo.destination == Destination.ANYTIME
    assert todo.changes == {
        "_destination",
        "_projects",
        "_modification_date",
    }


def test_assign_area():
    todo = TodoItem("test task")
    todo.area = "test-area"
    assert todo._areas == ["test-area"]
    assert todo.area == "test-area"
    assert todo._projects == []
    assert todo.project is None
    assert todo.destination == Destination.ANYTIME
    assert todo.changes == {
        "_destination",
        "_areas",
        "_modification_date",
    }
