from datetime import datetime, timezone

import pytest
from attrs import asdict

from things_cloud.models.serde import TodoSerde
from things_cloud.models.todo import (
    Destination,
    Note,
    Status,
    TodoItem,
    Type,
    deserialize,
    serialize_dict,
)
from things_cloud.utils import Util

FAKE_TIME = datetime(2021, 1, 1)


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
        "instance_creation_paused": False,
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
    assert project._type == Type.PROJECT
    assert project._instance_creation_paused is True
    assert project.destination == Destination.ANYTIME
    assert project.changes == {
        "_destination",
        "_instance_creation_paused",
        "_type",
        "_modification_date",
    }


def test_assign_project_uuid():
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


def test_assign_project_item():
    project = TodoItem("test project").as_project()
    todo = TodoItem("test task")
    todo.project = project
    assert todo._projects == [project.uuid]
    assert todo.project == project.uuid
    assert isinstance(todo.project, str)
    assert todo._areas == []
    assert todo.area is None
    assert todo.destination == Destination.ANYTIME
    assert todo.changes == {
        "_destination",
        "_projects",
        "_modification_date",
    }


def test_assign_project_invalid():
    not_project = TodoItem("not project")
    todo = TodoItem("test task")
    with pytest.raises(ValueError):
        todo.project = not_project
    assert not todo.project
    assert not todo.area
    assert not todo.destination
    assert not todo.changes


def test_clear_project():
    todo = TodoItem("test task")
    todo._projects = ["test-project"]
    assert not todo.changes

    # clear project
    todo.project = None
    assert not todo.project
    assert not todo.area
    assert not todo.destination
    assert todo.changes == {
        "_projects",
        "_modification_date",
    }


def test_assign_area_uuid():
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


def test_clear_area():
    todo = TodoItem("test task")
    todo._areas = ["test-area"]
    assert not todo.changes

    # clear area
    todo.area = None
    assert not todo.area
    assert not todo.project
    assert not todo.destination
    assert todo.changes == {
        "_areas",
        "_modification_date",
    }


def test_todo():
    todo = TodoItem("test task")
    # should fail if status is already todo
    with pytest.raises(ValueError):
        todo.todo()
    assert not todo.changes

    todo._status = Status.COMPLETE
    todo._completion_date = datetime(2022, 1, 1)
    todo.todo()
    assert todo._status == Status.TODO
    assert todo._completion_date is None
    assert todo.changes == {
        "_status",
        "_completion_date",
        "_modification_date",
    }


def test_complete():
    todo = TodoItem("test task")
    todo._status = Status.COMPLETE
    todo._completion_date = datetime(2022, 1, 1)
    # should fail if status is already complete
    with pytest.raises(ValueError):
        todo.complete()
    assert not todo.changes

    todo._status = Status.TODO
    todo._completion_date = None
    todo.complete()
    assert todo._status == Status.COMPLETE
    assert todo._completion_date == Util.now()
    assert todo.changes == {
        "_status",
        "_completion_date",
        "_modification_date",
    }


def test_cancel():
    todo = TodoItem("test task")
    todo._status = Status.CANCELLED
    todo._completion_date = datetime(2022, 1, 1)
    # should fail if status is already cancelled
    with pytest.raises(ValueError):
        todo.cancel()
    assert not todo.changes

    todo._status = Status.TODO
    todo._completion_date = None
    todo.cancel()
    assert todo._status == Status.CANCELLED
    assert todo._completion_date == Util.now()
    assert todo.changes == {
        "_status",
        "_completion_date",
        "_modification_date",
    }


def test_today():
    todo = TodoItem("test task")
    todo.today()
    assert todo.destination == Destination.ANYTIME
    assert todo.scheduled_date == Util.today()
    assert todo._today_index_reference_date == Util.today()
    assert todo.changes == {
        "_destination",
        "_scheduled_date",
        "_today_index_reference_date",
        "_modification_date",
    }


def test_evening():
    todo = TodoItem("test task")
    todo.evening()
    assert todo.destination == Destination.ANYTIME
    assert todo.scheduled_date == Util.today()
    assert todo._today_index_reference_date == Util.today()
    assert todo._is_evening == 1
    assert todo.changes == {
        "_destination",
        "_scheduled_date",
        "_today_index_reference_date",
        "_is_evening",
        "_modification_date",
    }


def test_deserialize():
    api_object = {
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
    }
    todo = deserialize(api_object)
    time = datetime(2022, 1, 3, 18, 29, 27, tzinfo=timezone.utc)
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
    assert todo._rt == []
    assert todo._repeater_migration_date is None
    assert todo._dl == []
    assert todo._do == 0
    assert todo._last_alarm_interaction_date is None
    assert todo._action_group == []
    assert todo._lt is False
    assert todo._instance_creation_count == 0
    assert todo._today_index == 0
    assert todo._reminder is None
    assert todo._instance_creation_start_date is None
    assert todo._rp is None
    assert todo._after_completion_reference_date is None
    assert todo._recurrence_rule is None
    assert todo._note == Note()
    assert not todo._changes


def test_update():
    todo = TodoItem("original")
    update = TodoItem("updated")
    keys = {"tt"}
    todo.update(update, keys)
    assert todo.title == "updated"
