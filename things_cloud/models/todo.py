from __future__ import annotations

from datetime import datetime, time
from enum import Enum
from typing import Any, Deque

import cattrs
from attr import Factory
from attrs import asdict, define, field
from cattrs.gen import make_dict_unstructure_fn, override

from things_cloud.models.serde import TodoSerde
from things_cloud.utils import Util

SERDE = TodoSerde()


class Destination(int, Enum):
    # destination: {0: inbox, 1: anytime/today/evening, 2: someday}
    INBOX = 0
    ANYTIME = 1
    SOMEDAY = 2


class Status(int, Enum):
    TODO = 0
    CANCELLED = 2
    COMPLETE = 3


@define
class Note:
    _t: str = field(init=False, default="tx")
    ch: int = 0
    v: str = ""  # value
    t: int = 0


@define
class TodoItem:
    index: int = field(default=0, init=False)
    _title: str = field(default="")
    status: Status = field(default=Status.TODO, init=False)
    _destination: Destination = field(default=Destination.INBOX)
    creation_date: datetime | None = field(factory=Util.now, init=False)
    modification_date: datetime | None = field(factory=Util.now, init=False)
    _scheduled_date: datetime | None = field(default=None)
    _tir: datetime | None = field(default=None)  # same as scheduled_date?
    completion_date: datetime | None = field(default=None)
    _due_date: datetime | None = field(default=None)
    trashed: bool = field(default=False)
    is_project: bool = field(default=False)
    _projects: list[str] = field(factory=list)
    _areas: list[str] = field(factory=list)
    is_evening: bool = field(default=False, converter=int)
    tags: list[Any] = field(factory=list)
    tp: int = field(default=0)  # 0: todo, 1: project?
    dds: None = field(default=None)
    rt: list[Any] = field(factory=list)
    rmd: None = field(default=None)
    dl: list[Any] = field(factory=list)
    do: int = field(default=0)
    lai: None = field(default=None)
    agr: list[Any] = field(factory=list)
    lt: bool = field(default=False)
    icc: int = field(default=0)
    ti: int = field(default=0)  # position/order of items
    _reminder: time | None = field(default=None)
    icsd: None = field(default=None)
    rp: None = field(default=None)
    acrd: None = field(default=None)
    rr: None = field(default=None)
    note: Note = field(factory=Note)
    _changes = Deque()

    # def serialize(self) -> str:
    #     return self.json(by_alias=True)

    # def serialize_dict(self) -> dict:
    #     return SERDE.deserialize(self.serialize())

    @property
    def changes(self) -> set:
        return set(self._changes)

    def reset_changes(self) -> None:
        self._changes.clear()

    # @changes.deleter
    # def changes(self) -> None:
    #     self._changes.clear()

    def modify(self) -> None:
        self.modification_date = Util.now()
        self._changes.append("modification_date")

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, title: str) -> None:
        self.modify()
        self._changes.append("title")
        self._title = title

    @property
    def destination(self) -> Destination:
        return self._destination

    @destination.setter
    def destination(self, destination: Destination) -> None:
        self.modify()
        self._changes.append("_destination")
        self._destination = destination

    @property
    def project(self) -> str | None:
        return self._projects[0] if self._projects else None

    @project.setter
    def project(self, project: str | None) -> None:
        self.modify()
        self._changes.append("_projects")
        if not project:
            self._projects.clear()
            return
        self._projects = [project]
        if self.area:
            self.area = None
        if self.destination == Destination.INBOX:
            self.destination = Destination.SOMEDAY

    @property
    def area(self) -> str | None:
        return self._areas[0] if self._areas else None

    @area.setter
    def area(self, area: str | None) -> None:
        self.modify()
        self._changes.append("_areas")
        if not area:
            self._areas.clear()
            return
        self._areas = [area]
        if self.project:
            self.project = None
        if self.destination == Destination.INBOX:
            self.destination = Destination.SOMEDAY

    @staticmethod
    def create_project(title: str) -> TodoItem:
        return TodoItem(
            title,
            Destination.ANYTIME,
            is_project=True,
            tp=1,
        )

    # HACK: prolly not needed longterm
    def find_changed(self) -> Deque[str]:
        d = Deque()
        for attribute in self.__attrs_attrs__:  # type: ignore
            value = getattr(self, attribute.name)
            if value != attribute.default:
                if (
                    type(attribute.default) is Factory
                    and attribute.default.factory() == value
                ):
                    continue
                d.append(attribute.name)
        return d

    def todo(self) -> None:
        self.status = Status.TODO
        self._changes.append("status")
        self.completion_date = None
        self._changes.append("completion_date")
        self.modify()

    def complete(self) -> None:
        self.status = Status.COMPLETE
        self._changes.append("status")
        self.completion_date = Util.now()
        self._changes.append("completion_date")
        self.modify()

    def cancel(self) -> None:
        self.status = Status.CANCELLED
        self._changes.append("status")
        self.completion_date = Util.now()
        self._changes.append("completion_date")
        self.modify()

    def delete(self) -> None:
        self._changes.append("trashed")
        self.trashed = True
        self.modify()

    def restore(self) -> None:
        self._changes.append("trashed")
        self.trashed = False
        self.modify()

    @property
    def scheduled_date(self) -> datetime | None:
        return self._scheduled_date

    @scheduled_date.setter
    def scheduled_date(self, scheduled_date: datetime | None) -> None:
        self._changes.append("_scheduled_date")
        self._scheduled_date = scheduled_date
        self._changes.append("_tir")
        self._tir = scheduled_date
        self.modify()

    @property
    def due_date(self) -> datetime | None:
        return self._due_date

    @due_date.setter
    def due_date(self, deadline: datetime | None) -> None:
        self._changes.append("_due_date")
        self._due_date = deadline
        self.modify()

    @property
    def reminder(self) -> time | None:
        return self._reminder

    @reminder.setter
    def reminder(self, reminder: time | None) -> None:
        self._changes.append("_reminder")
        self._reminder = reminder
        self.modify()

    def evening(self) -> None:
        today = Util.today()
        self.destination = Destination.ANYTIME
        self.scheduled_date = today
        self.is_evening = True
        self._changes.append("is_evening")
        self.modify()

    def today(self) -> None:
        today = Util.today()
        self.destination = Destination.ANYTIME
        self.scheduled_date = today
        self.modify()


converter = cattrs.Converter()
todo_unst_hook = make_dict_unstructure_fn(
    TodoItem,
    converter,
    # index=override(rename="ix"),
    # title=override(rename="tt"),
    # status=override(rename="ss"),
    # destination=override(rename="st"),
    # creation_date=override(rename="cd"),
    # modification_date=override(rename="md"),
    # scheduled_date=override(rename="sr"),
    # tir=override(rename="tir"),  # same as scheduled_date?
    # completion_date=override(rename="sp"),
    # due_date=override(rename="dd"),
    # in_trash=override(rename="tr"),
    # is_project=override(rename="icp"),
    # projects=override(rename="pr"),
    # areas=override(rename="ar"),
    # is_evening=override(rename="sb"),
    # tags=override(rename="tg"),
    # tp=override(rename="tp"),  # 0: todo, 1: project?
    # dds=override(rename="dds"),
    # rt=override(rename="rt"),
    # rmd=override(rename="rmd"),
    # dl=override(rename="dl"),
    # do=override(rename="do"),
    # lai=override(rename="lai"),
    # agr=override(rename="agr"),
    # lt=override(rename="lt"),
    # icc=override(rename="icc"),
    # ti=override(rename="ti"),  # position/order of items
    # reminder=override(rename="ato"),
    # icsd=override(rename="icsd"),
    # rp=override(rename="rp"),
    # acrd=override(rename="acrd"),
    # rr=override(rename="rr"),
    # note=override(rename="nt"),
)


# converter.register_unstructure_hook(TodoItem, todo_unst_hook)

converter.register_unstructure_hook(datetime, TodoSerde.timestamp_rounded)

ALIASES = {
    "index": "ix",
    "_title": "tt",
    "status": "ss",
    "_destination": "st",
    "creation_date": "cd",
    "modification_date": "md",
    "_scheduled_date": "sr",
    "_tir": "tir",  # same as scheduled_date?
    "completion_date": "sp",
    "_due_date": "dd",
    "trashed": "tr",
    "is_project": "icp",
    "_projects": "pr",
    "_areas": "ar",
    "is_evening": "sb",
    "tags": "tg",
    "tp": "tp",  # 0: todo, 1: project?
    "dds": "dds",
    "rt": "rt",
    "rmd": "rmd",
    "dl": "dl",
    "do": "do",
    "lai": "lai",
    "agr": "agr",
    "lt": "lt",
    "icc": "icc",
    "ti": "ti",  # position/order of items
    "_reminder": "ato",
    "icsd": "icsd",
    "rp": "rp",
    "acrd": "acrd",
    "rr": "rr",
    "note": "nt",
}


def serialize_dict(todo: TodoItem, keys: set[str] | None = None) -> dict:
    # d = asdict(todo)
    d = converter.unstructure(todo)
    # filter allowed keys
    return {ALIASES[k]: v for k, v in d.items() if keys is None or k in keys}
