from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, List, Optional

import orjson
from dataclasses_json import config
from dataclasses_json.api import DataClassJsonMixin
from pydantic import BaseModel, Field

from things import Destination, as_timestamp, get_timestamp

now = get_timestamp


def orjson_dumps(v, *, default):
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v, default=default).decode()


class Destination(int, Enum):
    # destination: {0: inbox, 1: today/evening, 2: someday}
    INBOX = 0
    TODAY = 1
    SOMEDAY = 2


class Status(int, Enum):
    # status: {0: todo, 3: done}?
    TODO = 0
    DONE = 3


@dataclass
class Note(DataClassJsonMixin):
    _t: str = field(default="tx", metadata=config(field_name="_t"))
    ch: int = field(default=0, metadata=config(field_name="ch"))
    value: str = field(default="", metadata=config(field_name="v"))
    t: int = field(default=0, metadata=config(field_name="t"))


@dataclass
class TodoItem(DataClassJsonMixin):
    index: int = field(metadata=config(field_name="ix"))
    title: str = field(metadata=config(field_name="tt"))
    destination: Destination = field(metadata=config(field_name="st"))
    creation_date: float = field(default_factory=now, metadata=config(field_name="cd"))
    modification_date: float = field(
        default_factory=now, metadata=config(field_name="md")
    )
    scheduled_date: Optional[int] = field(
        default=None, metadata=config(field_name="sr")
    )
    tir: Optional[int] = field(default=None, metadata=config(field_name="tir"))
    due_date: Optional[int] = field(default=None, metadata=config(field_name="dd"))
    status: Status = field(default=Status.TODO, metadata=config(field_name="ss"))
    in_trash: bool = field(default=False, metadata=config(field_name="tr"))
    is_project: bool = field(default=False, metadata=config(field_name="icp"))
    projects: List[Any] = field(default_factory=list, metadata=config(field_name="pr"))
    areas: List[Any] = field(default_factory=list, metadata=config(field_name="ar"))
    is_evening: int = field(default=0, metadata=config(field_name="sb"))
    tags: List[Any] = field(default_factory=list, metadata=config(field_name="tg"))
    tp: int = field(default=0, metadata=config(field_name="tp"))
    dds: None = field(default=None, metadata=config(field_name="dds"))
    rt: List[Any] = field(default_factory=list, metadata=config(field_name="rt"))
    rmd: None = field(default=None, metadata=config(field_name="rmd"))
    dl: List[Any] = field(default_factory=list, metadata=config(field_name="dl"))
    do: int = field(default=0, metadata=config(field_name="do"))
    lai: None = field(default=None, metadata=config(field_name="lai"))
    agr: List[Any] = field(default_factory=list, metadata=config(field_name="agr"))
    lt: bool = field(default=False, metadata=config(field_name="lt"))
    icc: int = field(default=0, metadata=config(field_name="icc"))
    ti: int = field(default=0, metadata=config(field_name="ti"))
    ato: None = field(default=None, metadata=config(field_name="ato"))
    icsd: None = field(default=None, metadata=config(field_name="icsd"))
    rp: None = field(default=None, metadata=config(field_name="rp"))
    acrd: None = field(default=None, metadata=config(field_name="acrd"))
    sp: None = field(default=None, metadata=config(field_name="sp"))
    rr: None = field(default=None, metadata=config(field_name="rr"))
    note: Note = field(default_factory=Note, metadata=config(field_name="nt"))


class TodoItemPydantic(BaseModel):
    index: int = Field(alias="ix")
    title: str = Field(alias="tt")
    destination: Destination = Field(alias="st")
    creation_date: datetime = Field(datetime.now(), alias="cd")
    modification_date: float = Field(default_factory=now, alias="md")
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
        # json_loads = orjson.loads
        # json_dumps = orjson_dumps


def create_todo_json(
    title: str,
    destination: Destination = Destination.INBOX,
    scheduled_date: datetime | None = None,
    due_date: datetime | None = None,
) -> str:
    now = get_timestamp()
    data = json.dumps(
        {
            "tp": 0,
            "sr": as_timestamp(scheduled_date) if scheduled_date else None,
            "dds": None,
            "rt": [],
            "rmd": None,
            "ss": 0,  # status {0: todo, 3: done}?
            "tr": False,  # in_trash
            "dl": [],
            "icp": False,  # is_project
            "st": destination.value,
            "ar": [],  # areas
            "tt": title,
            "do": 0,
            "lai": None,
            "tir": as_timestamp(scheduled_date) if scheduled_date else None,
            "tg": [],  # tags
            "agr": [],
            "ix": 0,  # position (order in inbox for example)
            "cd": now,  # creation_date
            "lt": False,
            "icc": 0,
            "ti": 0,  # -454
            "md": now,  # modification_date
            "dd": as_timestamp(due_date) if due_date else None,
            "ato": None,
            "nt": {"_t": "tx", "ch": 0, "v": "", "t": 1},  # note
            "icsd": None,
            "pr": [],  # projects
            "rp": None,
            "acrd": None,
            "sp": None,
            "sb": 0,  # {0: not evening, 1: evening}, in addition to st=1 (today)
            "rr": None,
        },
    )
    return data


if __name__ == "__main__":
    # item = TodoItem(index=123, title="test", destination=Destination.TODAY)
    # print("serialize to dict")
    # print(item.to_dict())

    # print("serialize to json")
    # print(item.to_json())
    # print(json.dumps(item.to_dict()))

    # print("deserialize from dict")
    # deserialized_json = TodoItem.from_dict({"ix": 0, "tt": "test", "st": 0})
    # print(deserialized_json)

    # print("deserialize from json")
    # deserialized_json = TodoItem.from_json(create_todo_json(title="test"))
    # print(deserialized_json)

    print("using pydantic")
    item = TodoItemPydantic(index=1, title="test", destination=Destination.TODAY)
    print(item)
    print("serialize to json")
    serialized_json = item.json(by_alias=True)
    print(serialized_json)
    print("deserialize from json")
    deserialized_json = TodoItemPydantic.parse_raw(serialized_json)
    # or
    # deserialized_json = TodoItemPydantic(**json.loads(serialized_json))
    print(deserialized_json)
