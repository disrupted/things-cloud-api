from __future__ import annotations

from collections import deque
from collections.abc import Callable
from datetime import datetime, time
from enum import IntEnum
from typing import Annotated, Any, Concatenate, ParamSpec, TypeVar

import pydantic

from things_cloud.models.serde import TodoSerde
from things_cloud.utils import Util

SERDE = TodoSerde()


class Type(IntEnum):
    TASK = 0
    PROJECT = 1
    HEADING = 2


class Destination(IntEnum):
    # destination: {0: inbox, 1: anytime/today/evening, 2: someday}
    INBOX = 0
    ANYTIME = 1
    SOMEDAY = 2


class Status(IntEnum):
    TODO = 0
    CANCELLED = 2
    COMPLETE = 3


class Note(pydantic.BaseModel):
    t_: str = pydantic.Field(alias="_t", default="tx")
    ch: int = 0
    v: str = ""  # value
    t: int = 0


ShortUUID = Annotated[str, pydantic.StringConstraints(min_length=22, max_length=22)]
Timestamp = Annotated[
    datetime,
    pydantic.PlainValidator(
        TodoSerde.from_timestamp, json_schema_input_type=datetime | int
    ),
    pydantic.PlainSerializer(TodoSerde.timestamp_rounded),
]
BoolBit = Annotated[bool, pydantic.PlainSerializer(int)]


class TodoApiObject(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    _uuid: ShortUUID | None = pydantic.PrivateAttr(default=None)
    index: Annotated[int, pydantic.Field(alias="ix")]
    title: Annotated[str, pydantic.Field(alias="tt")]
    status: Annotated[Status, pydantic.Field(alias="ss")]
    destination: Annotated[Destination, pydantic.Field(alias="st")]
    creation_date: Annotated[Timestamp | None, pydantic.Field(alias="cd")]
    modification_date: Annotated[Timestamp | None, pydantic.Field(alias="md")]
    scheduled_date: Annotated[Timestamp | None, pydantic.Field(alias="sr")]
    today_index_reference_date: Annotated[Timestamp | None, pydantic.Field(alias="tir")]
    completion_date: Annotated[Timestamp | None, pydantic.Field(alias="sp")]
    due_date: Annotated[Timestamp | None, pydantic.Field(alias="dd")]
    trashed: Annotated[bool, pydantic.Field(alias="tr")]
    instance_creation_paused: Annotated[bool, pydantic.Field(alias="icp")]
    projects: Annotated[list[str], pydantic.Field(alias="pr")]
    areas: Annotated[list[str], pydantic.Field(alias="ar")]
    is_evening: Annotated[BoolBit, pydantic.Field(alias="sb")]
    tags: Annotated[list[Any], pydantic.Field(alias="tg")]
    type: Annotated[Type, pydantic.Field(alias="tp")]
    due_date_suppression_date: Annotated[Timestamp | None, pydantic.Field(alias="dds")]
    repeating_template: Annotated[list[str], pydantic.Field(alias="rt")]
    repeater_migration_date: Annotated[Any, pydantic.Field(alias="rmd")]
    delegate: Annotated[list[Any], pydantic.Field(alias="dl")]
    due_date_offset: Annotated[int, pydantic.Field(alias="do")]
    last_alarm_interaction_date: Annotated[
        Timestamp | None, pydantic.Field(alias="lai")
    ]
    action_group: Annotated[list[str], pydantic.Field(alias="agr")]
    leaves_tombstone: Annotated[bool, pydantic.Field(alias="lt")]
    instance_creation_count: Annotated[int, pydantic.Field(alias="icc")]
    today_index: Annotated[int, pydantic.Field(alias="ti")]
    reminder: Annotated[time | None, pydantic.Field(alias="ato")]
    instance_creation_start_date: Annotated[
        Timestamp | None, pydantic.Field(alias="icsd")
    ]
    repeater: Annotated[Any, pydantic.Field(alias="rp")]
    after_completion_reference_date: Annotated[
        Timestamp | None, pydantic.Field(alias="acrd")
    ]
    recurrence_rule: Annotated[str | None, pydantic.Field(alias="rr")]
    note: Annotated[Note, pydantic.Field(alias="nt")]

    def to_todo(self) -> TodoItem:
        return TodoItem()


P = ParamSpec("P")
_R = TypeVar("_R")


def mod(
    *field_names: str,
) -> Callable[
    [Callable[Concatenate[TodoItem, P], _R]], Callable[Concatenate[TodoItem, P], _R]
]:
    def decorate(
        func: Callable[Concatenate[TodoItem, P], _R],
    ) -> Callable[Concatenate[TodoItem, P], _R]:
        def wrapper(self: TodoItem, *args: P.args, **kwargs: P.kwargs) -> _R:
            # first we call the wrapped function,
            # in case it throws an exception we don't want to modify
            ret = func(self, *args, **kwargs)
            self._modification_date = Util.now()
            self._changes.extend(field_names)
            self._changes.append("_modification_date")
            return ret

        return wrapper

    return decorate


class TodoItem(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(validate_assignment=True)

    _uuid: Annotated[str, pydantic.StringConstraints(min_length=22, max_length=22)] = (
        pydantic.PrivateAttr(default_factory=Util.uuid)
    )
    index: int = pydantic.Field(default=0)
    title_: str = pydantic.Field(default="", alias="title")
    status_: Status = pydantic.Field(default=Status.TODO, repr=False)
    destination_: Destination = pydantic.Field(default=Destination.INBOX)
    creation_date: datetime | None = pydantic.Field(default_factory=Util.now)
    modification_date: datetime | None = pydantic.Field(default_factory=Util.now)
    scheduled_date_: datetime | None = pydantic.Field(default=None)
    today_index_reference_date_: datetime | None = pydantic.Field(
        default=None, repr=False
    )
    completion_date_: datetime | None = pydantic.Field(default=None, repr=False)
    due_date: datetime | None = pydantic.Field(default=None)
    trashed: bool = pydantic.Field(default=False)
    instance_creation_paused: bool = pydantic.Field(default=False)
    projects_: list[str] = pydantic.Field(default_factory=list, repr=False)
    areas_: list[str] = pydantic.Field(default_factory=list)
    evening_: bool = pydantic.Field(default=False)
    tags: list[Any] = pydantic.Field(default_factory=list)  # TODO: set data type
    type: Type = pydantic.Field(default=Type.TASK)
    due_date_suppression_date: datetime | None = pydantic.Field(default=None)
    repeating_template: list[str] = pydantic.Field(default_factory=list)
    repeater_migration_date: Any = pydantic.Field(
        default=None
    )  # TODO: date type yet to be seen
    delegate: list[Any] = pydantic.Field(
        default_factory=list
    )  # TODO: date type yet to be seen
    due_date_offset: int = pydantic.Field(default=0)
    last_alarm_interaction_date: datetime | None = pydantic.Field(default=None)
    action_group: list[str] = pydantic.Field(default_factory=list)
    leaves_tombstone: bool = pydantic.Field(default=False)
    instance_creation_count: int = pydantic.Field(default=0)
    today_index: int = pydantic.Field(default=0)
    reminder: time | None = pydantic.Field(default=None)
    instance_creation_start_date: datetime | None = pydantic.Field(default=None)
    repeater: Any = pydantic.Field(default=None)  # TODO: date type yet to be seen
    after_completion_reference_date: datetime | None = pydantic.Field(default=None)
    recurrence_rule: str | None = pydantic.Field(default=None)  # TODO: weird XML values
    note: Note = pydantic.Field(default_factory=Note)
    _changes: deque[str] = pydantic.PrivateAttr(default=deque(["title"]))
    _api_object: TodoApiObject | None = pydantic.PrivateAttr(default=None)

    def to_api_object(self) -> TodoApiObject:
        return TodoApiObject(
            index=self.index,
            title=self.title,
            status=self.status,
            destination=self.destination,
            creation_date=self.creation_date,
            modification_date=self.modification_date,
            scheduled_date=self.scheduled_date,
            today_index_reference_date=self.today_index_reference_date_,
            completion_date=self.completion_date,
            due_date=self.due_date,
            trashed=self.trashed,
            instance_creation_paused=self.instance_creation_paused,
            projects=self.projects_,
            areas=self.areas_,
            is_evening=self.is_evening,
            tags=self.tags,
            type=self.type,
            due_date_suppression_date=self.due_date_suppression_date,
            repeating_template=self.repeating_template,
            repeater_migration_date=self.repeater_migration_date,
            delegate=self.delegate,
            due_date_offset=self.due_date_offset,
            last_alarm_interaction_date=self.last_alarm_interaction_date,
            action_group=self.action_group,
            leaves_tombstone=self.leaves_tombstone,
            instance_creation_count=self.instance_creation_count,
            today_index=self.today_index,
            reminder=self.reminder,
            instance_creation_start_date=self.instance_creation_start_date,
            repeater=self.repeater,
            after_completion_reference_date=self.after_completion_reference_date,
            recurrence_rule=self.recurrence_rule,
            note=self.note,
        )

    # @pydantic.model_serializer(mode="wrap")
    # def serialize_model(
    #     self,
    #     handler: pydantic.SerializerFunctionWrapHandler,
    #     info: pydantic.SerializationInfo,
    # ) -> dict[str, Any]:
    #     result = handler(self)
    #     return {
    #         "ix": self._index,
    #         "_title": "tt",
    #         "_status": "ss",
    #         "_destination": "st",
    #         "_creation_date": "cd",
    #         "_modification_date": "md",
    #         "_scheduled_date": "sr",
    #         "_today_index_reference_date": "tir",
    #         "_completion_date": "sp",
    #         "_due_date": "dd",
    #         "_trashed": "tr",
    #         "_instance_creation_paused": "icp",
    #         "_projects": "pr",
    #         "_areas": "ar",
    #         "_is_evening": "sb",
    #         "_tags": "tg",
    #         "_type": "tp",
    #         "_due_date_suppression_date": "dds",
    #         "_repeating_template": "rt",
    #         "_repeater_migration_date": "rmd",
    #         "_delegate": "dl",
    #         "_due_date_offset": "do",
    #         "_last_alarm_interaction_date": "lai",
    #         "_action_group": "agr",
    #         "_leaves_tombstone": "lt",
    #         "_instance_creation_count": "icc",
    #         "_today_index": "ti",
    #         "_reminder": "ato",
    #         "_instance_creation_start_date": "icsd",
    #         "_repeater": "rp",
    #         "_after_completion_reference_date": "acrd",
    #         "_recurrence_rule": "rr",
    #         "_note": "nt",
    #     }

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

    @property
    def title(self) -> str:
        return self.title_

    @title.setter
    @mod("title")
    def title(self, title: str) -> None:
        self.title_ = title

    @property
    def destination(self) -> Destination:
        return self.destination_

    @destination.setter
    @mod("_destination")
    def destination(self, destination: Destination) -> None:
        self.destination_ = destination

    @property
    def project(self) -> str | None:
        return self.projects_[0] if self.projects_ else None

    @project.setter
    @mod("projects_")
    def project(self, project: TodoItem | str | None) -> None:
        if isinstance(project, TodoItem):
            if project.type != Type.PROJECT:
                raise ValueError("argument must be a project")
            self.projects_ = [project.uuid]
        elif project:
            self.projects_ = [project]

        if not project:
            self.projects_.clear()
            return

        # clear area
        if self.area:
            self.area = None
        # move out of inbox
        if self.destination == Destination.INBOX:
            self.destination = Destination.ANYTIME

    @property
    def area(self) -> str | None:
        return self.areas_[0] if self.areas_ else None

    @area.setter
    @mod("areas_")
    def area(self, area: str | None) -> None:
        if not area:
            self.areas_.clear()
            return
        self.areas_ = [area]

        # clear project
        if self.project:
            self.project = None
        # move out of inbox
        if self.destination == Destination.INBOX:
            self.destination = Destination.ANYTIME

    @pydantic.computed_field
    @property
    def status(self) -> Status:
        return self.status_

    @status.setter
    @mod("_status")
    def status(self, status: Status) -> None:
        if self.status_ is status:
            raise ValueError(f"item already has {status.name.lower()} status")
        self.status_ = status
        match status:
            case Status.TODO:
                self.completion_date = None
            case Status.COMPLETE | Status.CANCELLED:
                self.completion_date = Util.now()

    def todo(self) -> None:
        self.status = Status.TODO

    def complete(self) -> None:
        self.status = Status.COMPLETE

    def cancel(self) -> None:
        self.status = Status.CANCELLED

    @mod("trashed")
    def delete(self) -> None:
        self.trashed = True

    @mod("trashed")
    def restore(self) -> None:
        self.trashed = False

    @mod("type", "_instance_creation_paused")
    def as_project(self) -> TodoItem:
        self.type = Type.PROJECT
        self._instance_creation_paused = True
        if self.destination == Destination.INBOX:
            self.destination = Destination.ANYTIME
        return self

    @property
    def completion_date(self) -> datetime | None:
        return self.completion_date_

    @completion_date.setter
    @mod("_completion_date")
    def completion_date(self, completion_date: datetime | None) -> None:
        self.completion_date_ = completion_date

    @property
    def scheduled_date(self) -> datetime | None:
        return self.scheduled_date_

    @scheduled_date.setter
    @mod("scheduled_date_", "today_index_reference_date_")
    def scheduled_date(self, scheduled_date: datetime | None) -> None:
        self.scheduled_date_ = scheduled_date
        self.today_index_reference_date_ = scheduled_date

    @property
    def due_date(self) -> datetime | None:
        return self._due_date

    @due_date.setter
    @mod("_due_date")
    def due_date(self, deadline: datetime | None) -> None:
        self._due_date = deadline

    @property
    def reminder(self) -> time | None:
        return self._reminder

    @reminder.setter
    @mod("_reminder")
    def reminder(self, reminder: time | None) -> None:
        self._reminder = reminder

    @property
    def is_today(self) -> bool:
        return (
            self.destination is Destination.ANYTIME
            and self.scheduled_date == Util.today()
        )

    @property
    def is_evening(self) -> bool:
        return self.is_today and self.evening_

    @mod("evening_")
    def evening(self) -> None:
        self.today()
        self.evening_ = True

    @mod()
    def today(self) -> None:
        today = Util.today()
        self.destination = Destination.ANYTIME
        self.scheduled_date = today

    # def update(self, update: TodoItem, keys: set[str]) -> None:
    #     for key in translate_keys_deserialize(keys):
    #         val = getattr(update, key)
    #         setattr(self, key, val)


# converter = cattrs.Converter(forbid_extra_keys=True)
# todo_unst_hook = make_dict_unstructure_fn(
#     TodoItem,
#     converter,
#     _uuid=override(omit=True),
#     _changes=override(omit=True),
# )

# todo_st_hook = make_dict_structure_fn(
#     TodoItem,
#     converter,
#     _index=override(rename="ix"),
#     _title=override(rename="tt"),
#     _status=override(rename="ss"),
#     _destination=override(rename="st"),
#     _creation_date=override(rename="cd"),
#     _modification_date=override(rename="md"),
#     _scheduled_date=override(rename="sr"),
#     _today_index_reference_date=override(rename="tir"),
#     _completion_date=override(rename="sp"),
#     _due_date=override(rename="dd"),
#     _trashed=override(rename="tr"),
#     _instance_creation_paused=override(rename="icp"),
#     _projects=override(rename="pr"),
#     _areas=override(rename="ar"),
#     _is_evening=override(
#         rename="sb", struct_hook=lambda value, _: bool(value), unstruct_hook=int
#     ),
#     _tags=override(rename="tg"),
#     _type=override(rename="tp"),
#     _due_date_suppression_date=override(rename="dds"),
#     _repeating_template=override(rename="rt"),
#     _repeater_migration_date=override(rename="rmd"),
#     _delegate=override(rename="dl"),
#     _due_date_offset=override(rename="do"),
#     _last_alarm_interaction_date=override(rename="lai"),
#     _action_group=override(rename="agr"),
#     _leaves_tombstone=override(rename="lt"),
#     _instance_creation_count=override(rename="icc"),
#     _today_index=override(rename="ti"),
#     _reminder=override(rename="ato"),
#     _instance_creation_start_date=override(rename="icsd"),
#     _repeater=override(rename="rp"),
#     _after_completion_reference_date=override(rename="acrd"),
#     _recurrence_rule=override(rename="rr"),
#     _note=override(rename="nt"),
# )


# converter.register_unstructure_hook(TodoItem, todo_unst_hook)
# converter.register_structure_hook(TodoItem, todo_st_hook)

# converter.register_unstructure_hook(datetime, TodoSerde.timestamp_rounded)
# converter.register_structure_hook(
#     datetime, lambda timestamp, _: datetime.fromtimestamp(timestamp, timezone.utc)
# )

# ALIASES_UNSTRUCT = {
#     "_index": "ix",
#     "_title": "tt",
#     "_status": "ss",
#     "_destination": "st",
#     "_creation_date": "cd",
#     "_modification_date": "md",
#     "_scheduled_date": "sr",
#     "_today_index_reference_date": "tir",
#     "_completion_date": "sp",
#     "_due_date": "dd",
#     "_trashed": "tr",
#     "_instance_creation_paused": "icp",
#     "_projects": "pr",
#     "_areas": "ar",
#     "_is_evening": "sb",
#     "_tags": "tg",
#     "_type": "tp",
#     "_due_date_suppression_date": "dds",
#     "_repeating_template": "rt",
#     "_repeater_migration_date": "rmd",
#     "_delegate": "dl",
#     "_due_date_offset": "do",
#     "_last_alarm_interaction_date": "lai",
#     "_action_group": "agr",
#     "_leaves_tombstone": "lt",
#     "_instance_creation_count": "icc",
#     "_today_index": "ti",
#     "_reminder": "ato",
#     "_instance_creation_start_date": "icsd",
#     "_repeater": "rp",
#     "_after_completion_reference_date": "acrd",
#     "_recurrence_rule": "rr",
#     "_note": "nt",
# }

# ALIASES_STRUCT = {v: k for k, v in ALIASES_UNSTRUCT.items()}


# def get_changes(todo: TodoItem) -> dict:
#     return serialize_dict(todo, todo.changes)


# def serialize_dict(todo: TodoItem, keys: set[str] | None = None) -> dict:
#     # d = asdict(todo)
#     d = converter.unstructure(todo)
#     # filter allowed keys
#     return {ALIASES_UNSTRUCT[k]: v for k, v in d.items() if keys is None or k in keys}


# def deserialize(api_object: dict) -> TodoItem:
#     return converter.structure(api_object, TodoItem)


# def translate_keys_deserialize(keys: set[str]) -> set[str]:
#     return {ALIASES_STRUCT[k] for k in keys}
