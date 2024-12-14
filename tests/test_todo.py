from datetime import datetime, timezone

import pytest

from things_cloud.models.serde import TodoSerde
from things_cloud.models.todo import (
    Destination,
    Note,
    Status,
    TodoApiObject,
    TodoItem,
    Type,
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
    item = TodoItem(title="test")

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

    assert item.model_dump(mode="json", by_alias=False) == d
    assert item.model_dump(mode="json", by_alias=True) == d_alias


def test_basic():
    todo = TodoItem(title="test task")
    assert todo.type is Type.TASK


def test_reset_changes():
    todo = TodoItem(title="test task")
    assert todo.changes == {"title"}
    todo.reset_changes()
    assert not todo.changes


def test_update_title():
    todo = TodoItem(title="test task")
    assert todo.changes == {"title"}
    todo.reset_changes()
    assert not todo.changes
    todo.title = "updated task"
    assert todo.changes == {"title", "_modification_date"}


def test_as_project():
    project = TodoItem().as_project()
    assert project.type is Type.PROJECT
    assert project._instance_creation_paused is True
    assert project.destination is Destination.ANYTIME
    assert project.changes == {
        "title",
        "_destination",
        "_instance_creation_paused",
        "type",
        "_modification_date",
    }


def test_assign_project_uuid():
    todo = TodoItem(title="test task")
    todo.project = "test-project"
    assert todo.projects_ == ["test-project"]
    assert todo.project == "test-project"
    assert todo.areas_ == []
    assert todo.area is None
    assert todo.destination is Destination.ANYTIME
    assert todo.changes == {
        "title",
        "_destination",
        "projects_",
        "_modification_date",
    }


def test_assign_project_item():
    project = TodoItem(title="test project").as_project()
    todo = TodoItem(title="test task")
    todo.project = project
    assert todo.projects_ == [project.uuid]
    assert todo.project == project.uuid
    assert isinstance(todo.project, str)
    assert todo.areas_ == []
    assert todo.area is None
    assert todo.destination == Destination.ANYTIME
    assert todo.changes == {
        "title",
        "_destination",
        "projects_",
        "_modification_date",
    }


def test_assign_project_invalid():
    not_project = TodoItem(title="not project")
    not_project.reset_changes()
    todo = TodoItem(title="test task")
    todo.reset_changes()
    with pytest.raises(ValueError):
        todo.project = not_project
    assert not todo.project
    assert not todo.area
    assert not todo.destination
    assert not todo.changes


def test_clear_project():
    todo = TodoItem(title="test task")
    todo.reset_changes()
    todo.projects_ = ["test-project"]
    assert not todo.changes

    # clear project
    todo.project = None
    assert not todo.project
    assert not todo.area
    assert not todo.destination
    assert todo.changes == {
        "projects_",
        "_modification_date",
    }


def test_assign_area_uuid():
    todo = TodoItem(title="test task")
    todo.reset_changes()
    todo.area = "test-area"
    assert todo.areas_ == ["test-area"]
    assert todo.area == "test-area"
    assert todo.projects_ == []
    assert todo.project is None
    assert todo.destination == Destination.ANYTIME
    assert todo.changes == {
        "_destination",
        "areas_",
        "_modification_date",
    }


def test_clear_area():
    todo = TodoItem(title="test task")
    todo.reset_changes()
    todo.areas_ = ["test-area"]
    assert not todo.changes

    # clear area
    todo.area = None
    assert not todo.area
    assert not todo.project
    assert not todo.destination
    assert todo.changes == {
        "areas_",
        "_modification_date",
    }


def test_todo():
    todo = TodoItem(title="test task")
    todo.reset_changes()
    # should fail if status is already todo
    with pytest.raises(ValueError):
        todo.todo()

    todo.status = Status.COMPLETE
    todo.completion_date = datetime(2022, 1, 1)
    todo.todo()
    assert todo.status == Status.TODO
    assert todo.completion_date is None
    assert todo.changes == {
        "_status",
        "_completion_date",
        "_modification_date",
    }


def test_complete():
    todo = TodoItem(title="test task")
    todo.reset_changes()
    todo.status_ = Status.COMPLETE
    todo.completion_date_ = datetime(2022, 1, 1)
    # should fail if status is already complete
    with pytest.raises(ValueError):
        todo.complete()
    assert not todo.changes

    todo.status_ = Status.TODO
    todo.completion_date_ = None
    todo.complete()
    assert todo.status_ == Status.COMPLETE
    assert todo.completion_date_ == Util.now()
    assert todo.changes == {
        "_status",
        "_completion_date",
        "_modification_date",
    }


def test_cancel():
    todo = TodoItem(title="test task")
    todo.reset_changes()
    todo.status_ = Status.CANCELLED
    todo.completion_date_ = datetime(2022, 1, 1)
    # should fail if status is already cancelled
    with pytest.raises(ValueError):
        todo.cancel()
    assert not todo.changes

    todo.status_ = Status.TODO
    todo.completion_date_ = None
    todo.cancel()
    assert todo.status_ == Status.CANCELLED
    assert todo.completion_date_ == Util.now()
    assert todo.changes == {
        "_status",
        "_completion_date",
        "_modification_date",
    }


def test_delete():
    todo = TodoItem(title="test task")
    todo.reset_changes()
    assert not todo.changes
    assert todo.trashed is False
    todo.delete()
    assert todo.changes == {
        "_modification_date",
        "trashed",
    }
    assert todo.trashed is True


def test_restore():
    todo = TodoItem(title="test task")
    todo.reset_changes()
    assert not todo.changes
    assert todo.trashed is False
    todo.delete()
    assert todo.trashed is True
    todo.restore()
    assert todo.trashed is False
    assert todo.changes == {
        "_modification_date",
        "trashed",
    }


def test_today():
    todo = TodoItem(title="test task")
    todo.reset_changes()
    assert todo.is_today is False
    assert todo.is_evening is False
    todo.today()
    assert todo.is_today is True
    assert todo.is_evening is False
    assert todo.destination == Destination.ANYTIME
    assert todo.scheduled_date == Util.today()
    assert todo.evening_ is False
    assert todo.today_index_reference_date_ == Util.today()
    assert todo.changes == {
        "_destination",
        "scheduled_date_",
        "today_index_reference_date_",
        "_modification_date",
    }


def test_evening():
    todo = TodoItem(title="test task")
    todo.reset_changes()
    assert todo.is_today is False
    assert todo.is_evening is False
    todo.evening()
    assert todo.is_today is True
    assert todo.is_evening is True
    assert todo.destination == Destination.ANYTIME
    assert todo.scheduled_date == Util.today()
    assert todo.today_index_reference_date_ == Util.today()
    assert todo.evening_ is True
    assert todo.changes == {
        "_destination",
        "scheduled_date_",
        "today_index_reference_date_",
        "evening_",
        "_modification_date",
    }


def test_serde():
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
    todo = TodoApiObject.model_validate(api_object)
    time = datetime(2022, 1, 3, 18, 29, 27, tzinfo=timezone.utc)
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
    assert todo.projects == ["ABCd1ee0ykmXYZqT98huxa"]
    assert todo.areas == []
    assert todo.is_evening is False
    assert todo.tags == []
    assert todo.type == Type.TASK
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
    assert todo.model_dump(mode="json", by_alias=True) == api_object


def test_todo_from_api_object():
    time = datetime(2022, 1, 3, 18, 29, 27, tzinfo=timezone.utc)
    api_object = TodoApiObject.model_validate(
        {
            "index": 1234,
            "title": "test task",
            "status": Status.TODO,
            "destination": Destination.ANYTIME,
            "creation_date": time,
            "modification_date": time,
            "scheduled_date": None,
            "today_index_reference_date": None,
            "completion_date": None,
            "due_date": None,
            "trashed": False,
            "instance_creation_paused": False,
            "projects": ["ABCd1ee0ykmXYZqT98huxa"],
            "areas": [],
            "is_evening": False,
            "tags": [],
            "type": Type.TASK,
            "due_date_suppression_date": None,
            "repeating_template": [],
            "repeater_migration_date": None,
            "delegate": [],
            "due_date_offset": 0,
            "last_alarm_interaction_date": None,
            "action_group": [],
            "leaves_tombstone": False,
            "instance_creation_count": 0,
            "today_index": 0,
            "reminder": None,
            "instance_creation_start_date": None,
            "repeater": None,
            "after_completion_reference_date": None,
            "recurrence_rule": None,
            "note": Note(),
        }
    )


def test_update():
    todo = TodoItem(title="original")
    update = TodoItem(title="updated")
    keys = {"tt"}
    todo.update(update, keys)
    assert todo.title == "updated"
