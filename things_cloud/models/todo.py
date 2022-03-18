from __future__ import annotations

from collections import deque
from datetime import datetime, time
from enum import Enum
from typing import Any

import cattrs
from attr import Factory
from attrs import define, field
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
    index: int = 0
    title: str = ""
    status: Status = Status.TODO
    destination: Destination = field(default=Destination.INBOX)
    creation_date: datetime | None = None
    modification_date: datetime | None = None
    scheduled_date: datetime | None = None
    tir: datetime | None = None  # same as scheduled_date?
    completion_date: datetime | None = None
    due_date: datetime | None = None
    in_trash: bool = False
    is_project: bool = False
    projects: list[str] = []
    areas: list[str] = []
    is_evening: bool = field(default=False, converter=int)
    tags: list[Any] = []
    tp: int = 0  # 0: todo, 1: project?
    dds: None = None
    rt: list[Any] = []
    rmd: None = None
    dl: list[Any] = []
    do: int = 0
    lai: None = None
    agr: list[Any] = []
    lt: bool = False
    icc: int = 0
    ti: int = 0  # position/order of items
    reminder: time | None = None
    icsd: None = None
    rp: None = None
    acrd: None = None
    rr: None = None
    note: Note = field(factory=Note)
    _changes = deque()

    # def serialize(self) -> str:
    #     return self.json(by_alias=True)

    # def serialize_dict(self) -> dict:
    #     return SERDE.deserialize(self.serialize())

    def modify(self) -> None:
        self.modification_date = Util.now()
        self._changes.append("modification_date")

    @property
    def project(self) -> str | None:
        return self.projects[0] if self.projects else None

    # @property
    # def title(self) -> str:
    #     return self._title

    # @title.setter
    # def title(self, title: str) -> None:
    #     self._title = title
    #     self._changes.append("title")

    @project.setter
    def project(self, project: str) -> None:
        self.areas.clear()
        self.projects = [project]
        if self.destination == Destination.INBOX:
            self.destination = Destination.SOMEDAY

    @property
    def area(self) -> str | None:
        return self.areas[0] if self.areas else None

    @area.setter
    def area(self, area: str) -> None:
        self.projects.clear()
        self.areas = [area]
        if self.destination == Destination.INBOX:
            self.destination = Destination.SOMEDAY

    @staticmethod
    def create(title: str, destination: Destination) -> TodoItem:
        now = Util.now()
        return TodoItem(
            title=title,
            destination=destination,
            creation_date=now,
            modification_date=now,
        )

    @staticmethod
    def create_project(title: str) -> TodoItem:
        now = Util.now()
        return TodoItem(
            title=title,
            destination=Destination.ANYTIME,
            creation_date=now,
            modification_date=now,
            is_project=True,
            tp=1,
        )

    def find_changed(self) -> deque[str]:
        d = deque()
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
        self.completion_date = None
        self._changes.append("completion_date")
        self.modify()

    @staticmethod
    def cancel() -> TodoItem:
        now = Util.now()
        item = TodoItem(
            status=Status.CANCELLED, modification_date=now, completion_date=now
        )
        return item.copy(include={"status", "modification_date", "completion_date"})

    @staticmethod
    def delete() -> TodoItem:
        item = TodoItem(in_trash=True, modification_date=Util.now())
        return item.copy(include={"in_trash", "modification_date"})

    @staticmethod
    def restore() -> TodoItem:
        item = TodoItem(in_trash=False, modification_date=Util.now())
        return item.copy(include={"in_trash", "modification_date"})

    @staticmethod
    def set_due_date(deadline: datetime) -> TodoItem:
        item = TodoItem(due_date=deadline, modification_date=Util.now())
        return item.copy(include={"due_date", "modification_date"})

    @staticmethod
    def clear_due_date() -> TodoItem:
        item = TodoItem(due_date=None, modification_date=Util.now())
        return item.copy(include={"due_date", "modification_date"})

    @staticmethod
    def set_reminder(reminder: time, scheduled_date: datetime) -> TodoItem:
        item = TodoItem(
            reminder=reminder,
            scheduled_date=scheduled_date,
            modification_date=Util.now(),
        )
        return item.copy(include={"reminder", "scheduled_date", "modification_date"})

    @staticmethod
    def clear_reminder() -> TodoItem:
        item = TodoItem(reminder=None, modification_date=Util.now())
        return item.copy(include={"reminder", "modification_date"})

    @staticmethod
    def set_evening() -> TodoItem:
        today = Util.today()
        item = TodoItem(
            destination=Destination.ANYTIME,
            scheduled_date=today,
            tir=today,
            is_evening=True,
            modification_date=Util.now(),
        )
        return item.copy(
            include={
                "destination",
                "scheduled_date",
                "tir",
                "is_evening",
                "modification_date",
            }
        )

    @staticmethod
    def set_destination(destination: Destination) -> TodoItem:
        item = TodoItem(
            destination=destination,
            modification_date=Util.now(),
        )
        return item.copy(include={"destination", "modification_date"})

    @staticmethod
    def set_today() -> TodoItem:
        today = Util.today()
        item = TodoItem(
            destination=Destination.ANYTIME,
            scheduled_date=today,
            tir=today,
            modification_date=Util.now(),
        )
        return item.copy(
            include={"destination", "scheduled_date", "tir", "modification_date"}
        )


converter = cattrs.Converter()
todo_unst_hook = make_dict_unstructure_fn(
    TodoItem,
    converter,
    index=override(rename="ix"),
    title=override(rename="tt"),
    status=override(rename="ss"),
    destination=override(rename="st"),
    creation_date=override(rename="cd"),
    modification_date=override(rename="md"),
    scheduled_date=override(rename="sr"),
    tir=override(rename="tir"),  # same as scheduled_date?
    completion_date=override(rename="sp"),
    due_date=override(rename="dd"),
    in_trash=override(rename="tr"),
    is_project=override(rename="icp"),
    projects=override(rename="pr"),
    areas=override(rename="ar"),
    is_evening=override(rename="sb"),
    tags=override(rename="tg"),
    tp=override(rename="tp"),  # 0: todo, 1: project?
    dds=override(rename="dds"),
    rt=override(rename="rt"),
    rmd=override(rename="rmd"),
    dl=override(rename="dl"),
    do=override(rename="do"),
    lai=override(rename="lai"),
    agr=override(rename="agr"),
    lt=override(rename="lt"),
    icc=override(rename="icc"),
    ti=override(rename="ti"),  # position/order of items
    reminder=override(rename="ato"),
    icsd=override(rename="icsd"),
    rp=override(rename="rp"),
    acrd=override(rename="acrd"),
    rr=override(rename="rr"),
    note=override(rename="nt"),
)


converter.register_unstructure_hook(TodoItem, todo_unst_hook)


def serialize_dict(todo: TodoItem) -> dict:
    return converter.unstructure(todo)
