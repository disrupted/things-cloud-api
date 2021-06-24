import datetime

import pytest

from things import Destination
from todo import Note, Status, TodoItem


def test_todo_schema(mocker):
    def get_timestamp():
        return 0

    mocker.patch(
        "things.get_timestamp",
        get_timestamp,
    )

    item = TodoItem(index=1, title="test", destination=Destination.INBOX)

    d = {
        "acrd": None,
        "agr": [],
        "ar": [],
        "ato": None,
        "cd": datetime.datetime(2021, 6, 24, 16, 4, 58, 212859),
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
        "md": datetime.datetime(2021, 6, 24, 16, 4, 58, 212859),
        "nt": Note,
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
