from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum

from dataclasses_json import config
from dataclasses_json.api import DataClassJsonMixin

from things import Destination, get_timestamp


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


now = get_timestamp


@dataclass
class TodoItem(DataClassJsonMixin):
    index: int = field(metadata=config(field_name="ix"))
    title: str = field(metadata=config(field_name="tt"))
    destination: Destination = field(metadata=config(field_name="st"))
    creation_date: float = field(default=now(), metadata=config(field_name="cd"))
    modification_date: float = field(default=now(), metadata=config(field_name="md"))
    scheduled_date: int | None = field(default=None, metadata=config(field_name="sr"))
    tir: int | None = field(default=None, metadata=config(field_name="tir"))
    due_date: int | None = field(default=None, metadata=config(field_name="dd"))
    status: Status = field(default=Status.TODO, metadata=config(field_name="ss"))
    in_trash: bool = field(default=False, metadata=config(field_name="tr"))
    is_project: bool = field(default=False, metadata=config(field_name="icp"))
    projects: list = field(default_factory=list, metadata=config(field_name="pr"))
    areas: list = field(default_factory=list, metadata=config(field_name="ar"))
    is_evening: int = field(default=0, metadata=config(field_name="sb"))
    tags: list = field(default_factory=list, metadata=config(field_name="tg"))
    tp: int = field(default=0, metadata=config(field_name="tp"))
    dds: None = field(default=None, metadata=config(field_name="dds"))
    rt: list = field(default_factory=list, metadata=config(field_name="rt"))
    rmd: None = field(default=None, metadata=config(field_name="rmd"))
    dl: list = field(default_factory=list, metadata=config(field_name="dl"))
    do: int = field(default=0, metadata=config(field_name="do"))
    lai: None = field(default=None, metadata=config(field_name="lai"))
    agr: list = field(default_factory=list, metadata=config(field_name="agr"))
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


# @dataclass
# class TodoItem():
#     index: int
#     destination: Destination

#     def to_dict(self) -> dict:
#         return {
#             "ix": self.index,
#             "st": self.destination.value,
#         }

#     def to_json(self) -> str:
#         return json.dumps(self.to_dict())

if __name__ == "__main__":
    item = TodoItem(index=123, title="test", destination=Destination.TODAY)
    print(item.to_dict())
    print(item.to_json())
    print(json.dumps(item.to_dict()))
