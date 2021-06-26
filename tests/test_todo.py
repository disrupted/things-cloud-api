import datetime as dt

import pytest

from things import Destination
from todo import Status, TodoItem, Util

FAKE_TIME = dt.datetime(2021, 1, 1)


@pytest.fixture
def todo(monkeypatch):
    monkeypatch.setattr(Util, "now", lambda: FAKE_TIME)
    return TodoItem


def test_mocked_now(todo):
    assert Util.now() == FAKE_TIME


def test_todo_schema():
    item = TodoItem(index=1, title="test", destination=Destination.INBOX)

    # mocking doesn't seem to work for pydantic default_factory
    item.creation_date = FAKE_TIME
    item.modification_date = FAKE_TIME

    d = {
        "acrd": None,
        "agr": [],
        "ar": [],
        "ato": None,
        "cd": FAKE_TIME,
        "dd": None,
        "dds": None,
        "dl": [],
        "do": 0,
        "icc": 0,
        "icp": False,
        "icsd": None,
        "ix": 1,
        "lai": None,
        "lt": False,
        "md": FAKE_TIME,
        "nt": {"ch": 0, "t": 0, "v": ""},
        "pr": [],
        "rmd": None,
        "rp": None,
        "rr": None,
        "rt": [],
        "sb": 0,
        "sp": None,
        "sr": None,
        "ss": Status.TODO,
        "st": Destination.INBOX,
        "tg": [],
        "ti": 0,
        "tir": None,
        "tp": 0,
        "tr": False,
        "tt": "test",
    }

    assert item.dict(by_alias=True) == d
