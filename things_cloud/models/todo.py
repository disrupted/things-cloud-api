from __future__ import annotations

from datetime import datetime, time
from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, Field

from things_cloud.models.serde import TodoSerde
from things_cloud.utils import Util

SERDE = TodoSerde()


class Destination(int, Enum):
    # destination: {0: inbox, 1: today/evening, 2: someday}
    INBOX = 0
    TODAY = 1
    SOMEDAY = 2


class Status(int, Enum):
    TODO = 0
    CANCELLED = 2
    COMPLETE = 3


class Note(BaseModel):
    _t: str = Field("tx", alias="_t")
    ch: int = Field(0, alias="ch")
    value: str = Field("", alias="v")
    t: int = Field(0, alias="t")

    class Config:
        allow_population_by_field_name = True


class TodoItem(BaseModel):
    index: int = Field(0, alias="ix")
    title: str = Field("", alias="tt")
    status: Status = Field(Status.TODO, alias="ss")
    destination: Destination = Field(Destination.INBOX, alias="st")
    creation_date: Optional[datetime] = Field(None, alias="cd")
    modification_date: Optional[datetime] = Field(None, alias="md")
    scheduled_date: Optional[datetime] = Field(None, alias="sr")
    completion_date: Optional[datetime] = Field(None, alias="sp")
    tir: Optional[int] = Field(None, alias="tir")
    due_date: Optional[datetime] = Field(None, alias="dd")
    in_trash: bool = Field(False, alias="tr")
    is_project: bool = Field(False, alias="icp")
    projects: List[Any] = Field(default_factory=list, alias="pr")
    areas: List[Any] = Field(default_factory=list, alias="ar")
    is_evening: bool = Field(False, alias="sb")
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
    ti: int = Field(0, alias="ti")  # position/order of items
    reminder: Optional[time] = Field(None, alias="ato")
    icsd: None = Field(None, alias="icsd")
    rp: None = Field(None, alias="rp")
    acrd: None = Field(None, alias="acrd")
    rr: None = Field(None, alias="rr")
    note: Note = Field(default_factory=Note, alias="nt")

    class Config:
        allow_population_by_field_name = True
        json_loads = SERDE.deserialize
        json_dumps = SERDE.serialize

    def serialize(self) -> str:
        return self.json(by_alias=True)

    def serialize_dict(self) -> dict:
        return SERDE.deserialize(self.serialize())

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
    def todo() -> TodoItem:
        item = TodoItem(
            status=Status.TODO, modification_date=Util.now(), completion_date=None
        )
        return item.copy(include={"status", "modification_date", "completion_date"})

    @staticmethod
    def complete() -> TodoItem:
        now = Util.now()
        item = TodoItem(
            status=Status.COMPLETE, modification_date=now, completion_date=now
        )
        return item.copy(include={"status", "modification_date", "completion_date"})

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
        item = TodoItem(
            is_evening=1,
            modification_date=Util.now(),
        )
        return item.copy(include={"is_evening", "modification_date"})
