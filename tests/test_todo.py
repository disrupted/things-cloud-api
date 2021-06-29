import datetime as dt

import pytest

from things import Destination
from todo import Status, TodoItem, Util

FAKE_TIME = dt.datetime(2021, 1, 1)


# TODO: write as setup/beforeall?
@pytest.fixture
def todo(monkeypatch):
    monkeypatch.setattr(Util, "now", lambda: FAKE_TIME)
    return TodoItem


def test_mocked_now(todo):
    assert Util.now() == FAKE_TIME


def test_todo_schema_create(todo):
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
        "destination": Destination.INBOX,
        "creation_date": FAKE_TIME,
        "modification_date": FAKE_TIME,
        "scheduled_date": None,
        "status": Status.TODO,
        "acrd": None,
        "agr": [],
        "areas": [],
        "ato": None,
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
        "sp": None,
        "tags": [],
        "ti": 0,
        "tir": None,
        "tp": 0,
        "in_trash": False,
    }

    d_alias = {
        "ix": 1,
        "tt": "test",
        "st": Destination.INBOX,
        "cd": FAKE_TIME,
        "md": FAKE_TIME,
        "sr": None,
        "ss": Status.TODO,
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
        "nt": {"ch": 0, "t": 0, "v": ""},
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

    assert item.dict() == d
    assert item.dict(by_alias=True) == d_alias
