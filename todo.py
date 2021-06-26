from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, List, Optional

import orjson
from pydantic import BaseModel, Field

from things import Destination


def orjson_dumps(v, *, default):
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v, default=default).decode()


def orjson_prettydumps(v, *, default):
    return orjson.dumps(v, default=default, option=orjson.OPT_INDENT_2).decode()


class Destination(int, Enum):
    # destination: {0: inbox, 1: today/evening, 2: someday}
    INBOX = 0
    TODAY = 1
    SOMEDAY = 2


class Status(int, Enum):
    # status: {0: todo, 3: done}?
    TODO = 0
    DONE = 3


class Note(BaseModel):
    _t: str = Field("tx", alias="_t")
    ch: int = Field(0, alias="ch")
    value: str = Field("", alias="v")
    t: int = Field(0, alias="t")

    class Config:
        allow_population_by_field_name = True


class Util:
    @staticmethod
    def now():
        return datetime.now()


class TodoItem(BaseModel):
    index: int = Field(alias="ix")
    title: str = Field(alias="tt")
    destination: Destination = Field(alias="st")
    creation_date: datetime = Field(default_factory=Util.now, alias="cd")
    modification_date: datetime = Field(Util.now(), alias="md")
    scheduled_date: Optional[int] = Field(None, alias="sr")
    tir: Optional[int] = Field(None, alias="tir")
    due_date: Optional[int] = Field(None, alias="dd")
    status: Status = Field(Status.TODO, alias="ss")
    in_trash: bool = Field(False, alias="tr")
    is_project: bool = Field(False, alias="icp")
    projects: List[Any] = Field(default_factory=list, alias="pr")
    areas: List[Any] = Field(default_factory=list, alias="ar")
    is_evening: int = Field(0, alias="sb")
    tags: List[Any] = Field(default_factory=list, alias="tg")
    tp: int = Field(0, alias="tp")
    dds: None = Field(None, alias="dds")
    rt: List[Any] = Field(default_factory=list, alias="rt")
    rmd: None = Field(None, alias="rmd")
    dl: List[Any] = Field(default_factory=list, alias="dl")
    do: int = Field(0, alias="do")
    lai: None = Field(None, alias="lai")
    agr: List[Any] = Field(default_factory=list, alias="agr")
    lt: bool = Field(False, alias="lt")
    icc: int = Field(0, alias="icc")
    ti: int = Field(0, alias="ti")
    ato: None = Field(None, alias="ato")
    icsd: None = Field(None, alias="icsd")
    rp: None = Field(None, alias="rp")
    acrd: None = Field(None, alias="acrd")
    sp: None = Field(None, alias="sp")
    rr: None = Field(None, alias="rr")
    note: Note = Field(default_factory=Note, alias="nt")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.timestamp(),
        }
        json_loads = orjson.loads
        # json_dumps = orjson_dumps
        json_dumps = orjson_prettydumps


# def create_todo_json(
#     title: str,
#     destination: Destination = Destination.INBOX,
#     scheduled_date: datetime | None = None,
#     due_date: datetime | None = None,
# ) -> str:
#     now = get_timestamp()
#     data = json.dumps(
#         {
#             "tp": 0,
#             "sr": as_timestamp(scheduled_date) if scheduled_date else None,
#             "dds": None,
#             "rt": [],
#             "rmd": None,
#             "ss": 0,  # status {0: todo, 3: done}?
#             "tr": False,  # in_trash
#             "dl": [],
#             "icp": False,  # is_project
#             "st": destination.value,
#             "ar": [],  # areas
#             "tt": title,
#             "do": 0,
#             "lai": None,
#             "tir": as_timestamp(scheduled_date) if scheduled_date else None,
#             "tg": [],  # tags
#             "agr": [],
#             "ix": 0,  # position (order in inbox for example)
#             "cd": now,  # creation_date
#             "lt": False,
#             "icc": 0,
#             "ti": 0,  # -454
#             "md": now,  # modification_date
#             "dd": as_timestamp(due_date) if due_date else None,
#             "ato": None,
#             "nt": {"_t": "tx", "ch": 0, "v": "", "t": 1},  # note
#             "icsd": None,
#             "pr": [],  # projects
#             "rp": None,
#             "acrd": None,
#             "sp": None,
#             "sb": 0,  # {0: not evening, 1: evening}, in addition to st=1 (today)
#             "rr": None,
#         },
#     )
#     return data


if __name__ == "__main__":
    print("using pydantic")
    item = TodoItem(index=1, title="test", destination=Destination.TODAY)
    print(item)
    # print("serialize to json")
    # serialized_json = item.json(by_alias=True)
    # print(serialized_json)
    # print("deserialize from json")
    # deserialized_json = TodoItem.parse_raw(serialized_json)
    # print(deserialized_json)
