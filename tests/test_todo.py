import datetime as dt

import pytest
from attrs import asdict

from things_cloud.models.serde import TodoSerde
from things_cloud.models.todo import Destination, Status, TodoItem, serialize_dict
from things_cloud.utils import Util

FAKE_TIME = dt.datetime(2021, 1, 1)


@pytest.fixture(autouse=True)
def todo(monkeypatch):
    monkeypatch.setattr(Util, "now", lambda: FAKE_TIME)
    return TodoItem


def test_mocked_now():
    assert Util.now() == FAKE_TIME


def test_todo_schema_create():
    now = Util.now()
    item = TodoItem(
        index=1,
        title="test",
        destination=Destination.INBOX,
        creation_date=now,
        modification_date=now,
    )

    d = {
        "index": 1,
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

    d_alias = {
        "ix": 1,
        "tt": "test",
        "st": 0,
        "cd": FAKE_TIME,
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


def test_create():
    item = TodoItem.create("test", Destination.ANYTIME)
    d = {
        "index": 0,
        "title": "test",
        "status": Status.TODO,
        "destination": Destination.ANYTIME,
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
        "note": {"ch": 0, "t": 0, "value": ""},
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
    assert item.dict() == d


def test_create_project():
    item = TodoItem.create_project("test project")
    d = {
        "index": 0,
        "title": "test project",
        "status": Status.TODO,
        "destination": Destination.ANYTIME,
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
        "is_project": True,
        "icsd": None,
        "lai": None,
        "lt": False,
        "note": {"ch": 0, "t": 0, "value": ""},
        "projects": [],
        "rmd": None,
        "rp": None,
        "rr": None,
        "rt": [],
        "is_evening": 0,
        "tags": [],
        "ti": 0,
        "tir": None,
        "tp": 1,
        "in_trash": False,
    }
    assert item.dict() == d


def test_todo():
    item = TodoItem.todo()
    assert item.dict() == {
        "status": Status.TODO,
        "modification_date": FAKE_TIME,
        "completion_date": None,
    }


def test_complete():
    item = TodoItem.complete()
    assert item.dict() == {
        "status": Status.COMPLETE,
        "modification_date": FAKE_TIME,
        "completion_date": FAKE_TIME,
    }


def test_cancel():
    item = TodoItem.cancel()
    assert item.dict() == {
        "status": Status.CANCELLED,
        "modification_date": FAKE_TIME,
        "completion_date": FAKE_TIME,
    }


def test_delete():
    item = TodoItem.delete()
    assert item.dict() == {"in_trash": True, "modification_date": FAKE_TIME}


def test_restore():
    item = TodoItem.restore()
    assert item.dict() == {"in_trash": False, "modification_date": FAKE_TIME}


def test_set_due_date():
    due_date = dt.datetime(2021, 12, 31)
    item = TodoItem.set_due_date(due_date)
    assert item.dict() == {"due_date": due_date, "modification_date": FAKE_TIME}
    assert item.json(by_alias=True) == TodoSerde.prettydumps(
        {
            "md": FAKE_TIME.timestamp(),
            "dd": int(due_date.timestamp()),
        }
    )


def test_clear_due_date():
    item = TodoItem.clear_due_date()
    assert item.dict() == {"due_date": None, "modification_date": FAKE_TIME}


def test_set_reminder():
    reminder = dt.time(21, 0)
    scheduled_date = Util.today()
    item = TodoItem.set_reminder(reminder, scheduled_date)
    assert item.dict() == {
        "reminder": reminder,
        "scheduled_date": scheduled_date,
        "modification_date": FAKE_TIME,
    }
    assert item.json(by_alias=True) == TodoSerde.prettydumps(
        {
            "md": FAKE_TIME.timestamp(),
            "sr": int(scheduled_date.timestamp()),
            "ato": 75600,
        }
    )


def test_clear_reminder():
    item = TodoItem.clear_reminder()
    assert item.dict() == {
        "reminder": None,
        "modification_date": FAKE_TIME,
    }
    assert item.json(by_alias=True) == TodoSerde.prettydumps(
        {
            "md": FAKE_TIME.timestamp(),
            "ato": None,
        }
    )


def test_set_evening():
    scheduled_date = Util.today()
    item = TodoItem.set_evening()
    assert item.dict() == {
        "destination": Destination.ANYTIME,
        "scheduled_date": scheduled_date,
        "tir": scheduled_date,
        "is_evening": True,
        "modification_date": FAKE_TIME,
    }
    assert item.json(by_alias=True) == TodoSerde.prettydumps(
        {
            "st": 1,
            "md": FAKE_TIME.timestamp(),
            "sr": int(scheduled_date.timestamp()),
            "tir": int(scheduled_date.timestamp()),
            "sb": 1,
        }
    )


def test_set_project():
    todo = TodoItem.create("test task", Destination.INBOX)
    todo.set_project("test-project")
    assert todo.projects == ["test-project"]
    assert todo.project == "test-project"
    assert todo.areas == []
    assert todo.destination == Destination.SOMEDAY


def test_set_area():
    todo = TodoItem.create("test task", Destination.INBOX)
    todo.set_area("test-area")
    assert todo.areas == ["test-area"]
    assert todo.area == "test-area"
    assert todo.projects == []
    assert todo.destination == Destination.SOMEDAY
