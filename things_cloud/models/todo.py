from __future__ import annotations

from datetime import datetime, time, timezone
from enum import Enum
from typing import Any, Deque

import cattrs
from attrs import define, field
from cattr.gen import make_dict_structure_fn
from cattrs.gen import make_dict_unstructure_fn, override

from things_cloud.models.serde import TodoSerde
from things_cloud.utils import Util

SERDE = TodoSerde()


class Type(int, Enum):
    TASK = 0
    PROJECT = 1
    HEADING = 2


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
    _uuid: str = field(factory=Util.uuid, init=False)
    _index: int = field(default=0, kw_only=True)
    _title: str = field(default="")
    _status: Status = field(default=Status.TODO, kw_only=True)
    _destination: Destination = field(default=Destination.INBOX, kw_only=True)
    _creation_date: datetime | None = field(factory=Util.now, kw_only=True)
    _modification_date: datetime | None = field(factory=Util.now, kw_only=True)
    _scheduled_date: datetime | None = field(default=None, kw_only=True)
    _today_index_reference_date: datetime | None = field(default=None, kw_only=True)
    _completion_date: datetime | None = field(default=None, kw_only=True)
    _due_date: datetime | None = field(default=None, kw_only=True)
    _trashed: bool = field(default=False, kw_only=True)
    _instance_creation_paused: bool = field(default=False, kw_only=True)
    _projects: list[str] = field(factory=list, kw_only=True)
    _areas: list[str] = field(factory=list, kw_only=True)
    _is_evening: bool = field(default=False, converter=int, kw_only=True)
    _tags: list[Any] = field(factory=list, kw_only=True)
    _type: Type = field(default=Type.TASK, kw_only=True)
    _due_date_suppression_date: datetime | None = field(default=None, kw_only=True)
    _repeating_template: list[str] = field(factory=list, kw_only=True)
    _repeater_migration_date: Any = field(default=None, kw_only=True)
    _delegate: list[Any] = field(factory=list, kw_only=True)
    _due_date_offset: int = field(default=0, kw_only=True)
    _last_alarm_interaction_date: Any = field(default=None, kw_only=True)
    _action_group: list[Any] = field(factory=list, kw_only=True)
    _leaves_tombstone: bool = field(default=False, kw_only=True)
    _instance_creation_count: int = field(default=0, kw_only=True)
    _today_index: int = field(default=0, kw_only=True)
    _reminder: time | None = field(default=None, kw_only=True)
    _instance_creation_start_date: Any = field(default=None, kw_only=True)
    _repeater: Any = field(default=None, kw_only=True)  # TODO: date type yet to be seen
    _after_completion_reference_date: Any = field(default=None, kw_only=True)
    _recurrence_rule: Any = field(default=None, kw_only=True)
    _note: Note = field(factory=Note, kw_only=True)
    _changes: Deque[str] = field(factory=Deque, init=False)

    @property
    def uuid(self) -> str:
        return self._uuid

    @property
    def changes(self) -> set:
        return set(self._changes)

    def reset_changes(self) -> None:
        self._changes.clear()

    # @changes.deleter
    # def changes(self) -> None:
    #     self._changes.clear()

    def modify(self) -> None:
        self._modification_date = Util.now()
        self._changes.append("_modification_date")

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, title: str) -> None:
        self.modify()
        self._changes.append("_title")
        self._title = title

    @property
    def status(self) -> Status:
        return self._status

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
    def project(self, project: TodoItem | str | None) -> None:
        if isinstance(project, TodoItem):
            if not project._type == Type.PROJECT:
                raise ValueError("argument must be a project")
            self._projects = [project.uuid]
        elif project:
            self._projects = [project]
        self.modify()
        self._changes.append("_projects")

        if not project:
            self._projects.clear()
            return

        # clear area
        if self.area:
            self.area = None
        # move out of inbox
        if self.destination == Destination.INBOX:
            self.destination = Destination.ANYTIME

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

        # clear project
        if self.project:
            self.project = None
        # move out of inbox
        if self.destination == Destination.INBOX:
            self.destination = Destination.ANYTIME

    def todo(self) -> None:
        if self._status == Status.TODO:
            raise ValueError("item already has todo status")
        self._status = Status.TODO
        self._changes.append("_status")
        self.completion_date = None

    def complete(self) -> None:
        if self._status == Status.COMPLETE:
            raise ValueError("item already has complete status")
        self._status = Status.COMPLETE
        self._changes.append("_status")
        self.completion_date = Util.now()

    def cancel(self) -> None:
        if self._status == Status.CANCELLED:
            raise ValueError("item already has cancelled status")
        self._status = Status.CANCELLED
        self._changes.append("_status")
        self.completion_date = Util.now()

    def delete(self) -> None:
        self._changes.append("_trashed")
        self._trashed = True
        self.modify()

    def restore(self) -> None:
        self._changes.append("_trashed")
        self._trashed = False
        self.modify()

    def as_project(self) -> TodoItem:
        self._type = Type.PROJECT
        self._changes.append("_type")
        self._instance_creation_paused = True
        self._changes.append("_instance_creation_paused")
        if self.destination == Destination.INBOX:
            self.destination = Destination.ANYTIME
        self.modify()
        return self

    @property
    def completion_date(self) -> datetime | None:
        return self._completion_date

    @completion_date.setter
    def completion_date(self, completion_date: datetime | None) -> None:
        self._changes.append("_completion_date")
        self._completion_date = completion_date
        self.modify()

    @property
    def scheduled_date(self) -> datetime | None:
        return self._scheduled_date

    @scheduled_date.setter
    def scheduled_date(self, scheduled_date: datetime | None) -> None:
        self._changes.append("_scheduled_date")
        self._scheduled_date = scheduled_date
        self._changes.append("_today_index_reference_date")
        self._today_index_reference_date = scheduled_date
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
        self._is_evening = True
        self._changes.append("_is_evening")
        self.modify()

    def today(self) -> None:
        today = Util.today()
        self.destination = Destination.ANYTIME
        self.scheduled_date = today
        self.modify()

    def update(self, update: TodoItem, keys: set[str]) -> None:
        for key in translate_keys_deserialize(keys):
            val = getattr(update, key)
            setattr(self, key, val)


# converter = cattrs.Converter()
converter = cattrs.GenConverter(forbid_extra_keys=True)
# TODO
todo_unst_hook = make_dict_unstructure_fn(
    TodoItem,
    converter,
    _uuid=override(omit=True),
    _changes=override(omit=True),
)

todo_st_hook = make_dict_structure_fn(
    TodoItem,
    converter,
    _index=override(rename="ix"),
    _title=override(rename="tt"),
    _status=override(rename="ss"),
    _destination=override(rename="st"),
    _creation_date=override(rename="cd"),
    _modification_date=override(rename="md"),
    _scheduled_date=override(rename="sr"),
    _today_index_reference_date=override(rename="tir"),
    _completion_date=override(rename="sp"),
    _due_date=override(rename="dd"),
    _in_trash=override(rename="tr"),
    _instance_creation_paused=override(rename="icp"),
    _projects=override(rename="pr"),
    _areas=override(rename="ar"),
    _is_evening=override(rename="sb"),
    _tags=override(rename="tg"),
    _type=override(rename="tp"),
    _due_date_suppression_date=override(rename="dds"),
    _repeating_template=override(rename="rt"),
    _repeater_migration_date=override(rename="rmd"),
    _delegate=override(rename="dl"),
    _due_date_offset=override(rename="do"),
    _last_alarm_interaction_date=override(rename="lai"),
    _action_group=override(rename="agr"),
    _leaves_tombstone=override(rename="lt"),
    _instance_creation_count=override(rename="icc"),
    _today_index=override(rename="ti"),
    _reminder=override(rename="ato"),
    _instance_creation_start_date=override(rename="icsd"),
    _repeater=override(rename="rp"),
    _after_completion_reference_date=override(rename="acrd"),
    _recurrence_rule=override(rename="rr"),
    _note=override(rename="nt"),
)


converter.register_unstructure_hook(TodoItem, todo_unst_hook)
converter.register_structure_hook(TodoItem, todo_st_hook)

converter.register_unstructure_hook(datetime, TodoSerde.timestamp_rounded)
converter.register_structure_hook(
    datetime, lambda timestamp, _: datetime.fromtimestamp(timestamp, timezone.utc)
)

ALIASES_UNSTRUCT = {
    "_index": "ix",
    "_title": "tt",
    "_status": "ss",
    "_destination": "st",
    "_creation_date": "cd",
    "_modification_date": "md",
    "_scheduled_date": "sr",
    "_today_index_reference_date": "tir",
    "_completion_date": "sp",
    "_due_date": "dd",
    "_trashed": "tr",
    "_instance_creation_paused": "icp",
    "_projects": "pr",
    "_areas": "ar",
    "_is_evening": "sb",
    "_tags": "tg",
    "_type": "tp",
    "_due_date_suppression_date": "dds",
    "_repeating_template": "rt",
    "_repeater_migration_date": "rmd",
    "_delegate": "dl",
    "_due_date_offset": "do",
    "_last_alarm_interaction_date": "lai",
    "_action_group": "agr",
    "_leaves_tombstone": "lt",
    "_instance_creation_count": "icc",
    "_today_index": "ti",
    "_reminder": "ato",
    "_instance_creation_start_date": "icsd",
    "_repeater": "rp",
    "_after_completion_reference_date": "acrd",
    "_recurrence_rule": "rr",
    "_note": "nt",
}

ALIASES_STRUCT = {v: k for k, v in ALIASES_UNSTRUCT.items()}


def get_changes(todo: TodoItem) -> dict:
    return serialize_dict(todo, todo.changes)


def serialize_dict(todo: TodoItem, keys: set[str] | None = None) -> dict:
    # d = asdict(todo)
    d = converter.unstructure(todo)
    # filter allowed keys
    return {ALIASES_UNSTRUCT[k]: v for k, v in d.items() if keys is None or k in keys}


def deserialize(api_object: dict) -> TodoItem:
    return converter.structure(api_object, TodoItem)


def translate_keys_deserialize(keys: set[str]) -> set[str]:
    return {ALIASES_STRUCT[k] for k in keys}
