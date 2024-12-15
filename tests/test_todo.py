from datetime import datetime, timezone

import pytest

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
def mock_time(monkeypatch):
    monkeypatch.setattr("things_cloud.utils.Util.now", lambda: FAKE_TIME)


def test_mocked_now():
    assert Util.now() == FAKE_TIME


@pytest.fixture()
def task() -> TodoItem:
    return TodoItem(title="test task")


@pytest.fixture()
def project() -> TodoItem:
    return TodoItem(title="test project").as_project()


def test_basic(task: TodoItem):
    assert task.type is Type.TASK


# def test_reset_changes(todo: TodoItem):
#     assert todo.changes == {"title"}
#     todo.reset_changes()
#     assert not todo.changes


def test_update_title(task: TodoItem):
    task.title = "updated task"
    # assert todo.changes == {"title", "_modification_date"}


def test_as_project(project: TodoItem):
    assert project.type is Type.PROJECT
    assert project.instance_creation_paused is True
    assert project.destination is Destination.ANYTIME
    # assert project.changes == {
    #     "title",
    #     "_destination",
    #     "_instance_creation_paused",
    #     "type",
    #     "_modification_date",
    # }


def test_assign_project_uuid(task: TodoItem, project: TodoItem):
    task.project = project.uuid
    assert task._projects == [project.uuid]
    assert task.project == project.uuid
    assert task._areas == []
    assert task.area is None
    assert task.destination is Destination.ANYTIME
    # assert todo.changes == {
    #     "title",
    #     "_destination",
    #     "projects_",
    #     "_modification_date",
    # }


def test_assign_project_uuid_self(project: TodoItem):
    with pytest.raises(ValueError):
        project.project = project.uuid
    # assert not project.changes


def test_assign_project_item(task: TodoItem, project: TodoItem):
    task.project = project
    assert task._projects == [project.uuid]
    assert task.project == project.uuid
    assert isinstance(task.project, str)
    assert task._areas == []
    assert task.area is None
    assert task.destination is Destination.ANYTIME
    # assert todo.changes == {
    #     "title",
    #     "_destination",
    #     "projects_",
    #     "_modification_date",
    # }


def test_assign_project_self(project: TodoItem):
    with pytest.raises(ValueError):
        project.project = project
    # assert not project.changes


def test_assign_project_invalid(task: TodoItem):
    not_project = TodoItem(title="not project")
    with pytest.raises(ValueError):
        task.project = not_project
    assert not task.project
    assert not task.area
    assert not task.destination
    # assert not todo.changes


def test_clear_project(task: TodoItem):
    task._projects = ["test-project"]
    # assert not todo.changes

    # clear project
    task.project = None
    assert not task.project
    assert not task.area
    assert not task.destination
    # assert todo.changes == {
    #     "projects_",
    #     "_modification_date",
    # }


def test_assign_area_uuid(task: TodoItem):
    task.area = "test-area"
    assert task._areas == ["test-area"]
    assert task.area == "test-area"
    assert task._projects == []
    assert task.project is None
    assert task.destination is Destination.ANYTIME
    # assert task.changes == {
    #     "_destination",
    #     "areas_",
    #     "_modification_date",
    # }


def test_clear_area(task: TodoItem):
    task._areas = ["test-area"]

    # clear area
    task.area = None
    assert not task.area
    assert not task.project
    assert not task.destination
    # assert task.changes == {
    #     "areas_",
    #     "_modification_date",
    # }


def test_todo(task: TodoItem):
    # should fail if status is already todo
    with pytest.raises(ValueError):
        task.todo()

    task.status = Status.COMPLETE
    task.completion_date = datetime(2022, 1, 1)
    task.todo()
    assert task.status is Status.TODO
    assert task.completion_date is None
    # assert task.changes == {
    #     "_status",
    #     "_completion_date",
    #     "_modification_date",
    # }


def test_complete(task: TodoItem):
    assert task.status is Status.TODO
    assert task.completion_date is None
    task.complete()
    assert task.status is Status.COMPLETE
    assert task.completion_date == Util.now()
    # assert task.changes == {
    #     "_status",
    #     "_completion_date",
    #     "_modification_date",
    # }


def test_complete_already_completed(task: TodoItem):
    task.status = Status.COMPLETE
    task.completion_date = datetime(2022, 1, 1)
    # should fail if status is already complete
    with pytest.raises(ValueError):
        task.complete()
    # assert not task.changes


def test_cancel(task: TodoItem):
    task.cancel()
    assert task.status is Status.CANCELLED
    assert task.completion_date == Util.now()
    # assert task.changes == {
    #     "_status",
    #     "_completion_date",
    #     "_modification_date",
    # }


def test_cancel_already_cancelled(task: TodoItem):
    task.status = Status.CANCELLED
    task.completion_date = datetime(2022, 1, 1)
    # should fail if status is already cancelled
    with pytest.raises(ValueError):
        task.cancel()
    # assert not task.changes


def test_delete(task: TodoItem):
    assert task.trashed is False
    task.delete()
    assert task.trashed is True
    # assert task.changes == {
    #     "_modification_date",
    #     "trashed",
    # }


def test_delete_already_trashed(task: TodoItem):
    task.trashed = True
    with pytest.raises(ValueError):
        task.delete()
    # assert not task.changes


def test_restore(task: TodoItem):
    task.delete()
    assert task.trashed is True
    task.restore()
    assert task.trashed is False
    # assert task.changes == {
    #     "_modification_date",
    #     "trashed",
    # }


def test_restore_not_trashed(task: TodoItem):
    with pytest.raises(ValueError):
        task.restore()
    # assert not task.changes


def test_today(task: TodoItem):
    assert task.is_today is False
    assert task.is_evening is False
    task.today()
    assert task.is_today is True
    assert task.is_evening is False
    assert task.destination is Destination.ANYTIME
    assert task.scheduled_date == Util.today()
    assert task._evening is False
    # assert task.today_index_reference_date == Util.today()  # FIXME
    # assert task.changes == {
    #     "_destination",
    #     "scheduled_date_",
    #     "today_index_reference_date_",
    #     "_modification_date",
    # }


def test_evening(task: TodoItem):
    assert task.is_today is False
    assert task.is_evening is False
    task.evening()
    assert task.is_today is True
    assert task.is_evening is True
    assert task.destination is Destination.ANYTIME
    assert task.scheduled_date == Util.today()
    assert task._evening is True
    # assert task.today_index_reference_date == Util.today()  # FIXME
    # assert task.changes == {
    #     "_destination",
    #     "scheduled_date_",
    #     "today_index_reference_date_",
    #     "evening_",
    #     "_modification_date",
    # }


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
        "md": 1641234567.007013,
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
    assert todo.modification_date == datetime(
        2022, 1, 3, 18, 29, 27, 7013, tzinfo=timezone.utc
    )
    assert todo.scheduled_date is None
    assert todo.today_index_reference_date is None
    assert todo.completion_date is None
    assert todo.due_date is None
    assert todo.trashed is False
    assert todo.instance_creation_paused is False
    assert todo.projects == ["ABCd1ee0ykmXYZqT98huxa"]
    assert todo.areas == []
    assert todo.evening is False
    assert todo.tags == []
    assert todo.type is Type.TASK
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
            "evening": False,
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
    todo = api_object.to_todo()
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
    assert todo.is_evening is False
    assert todo.tags == []
    assert todo.type is Type.TASK
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
    assert todo._synced_state == api_object


def test_to_new(task: TodoItem):
    assert task._synced_state is None
    new = task._to_new()
    # we simulate what happens when we commit the changes
    task._commit(new)
    assert task._synced_state
    assert task._synced_state.title == "test task"


def test_to_new_exists(task: TodoItem):
    assert task._synced_state is None
    new = task._to_new()
    # we simulate what happens when we commit the changes
    task._commit(new)

    with pytest.raises(
        ValueError, match="^current version exists for todo, use _to_edit instead$"
    ):
        task._to_new()


def test_to_edit_does_not_exist(task: TodoItem):
    with pytest.raises(
        ValueError, match="^no current version exists for todo, use _to_new instead$"
    ):
        task._to_edit()


def test_to_edit_unchanged(task: TodoItem):
    assert task._synced_state is None
    new = task._to_new()
    # we simulate what happens when we commit the changes
    task._commit(new)

    with pytest.raises(ValueError, match="^no changes found$"):
        task._to_edit()


def test_to_edit(task: TodoItem):
    assert task._synced_state is None
    new = task._to_new()
    # we simulate what happens when we commit the changes
    task._commit(new)

    task.title = "updated task"
    delta = task._to_edit()
    assert delta
    assert delta.model_dump(exclude_none=True) == {"title": "updated task"}


def test_to_edit_detect_reverts(task: TodoItem):
    assert task._synced_state is None
    new = task._to_new()
    # we simulate what happens when we commit the changes
    task._commit(new)

    task.title = "updated task"  # first we change something
    task.title = "test task"  # but then we revert to the old value
    with pytest.raises(ValueError, match="no changes found"):
        task._to_edit()
