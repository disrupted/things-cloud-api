from __future__ import annotations

from datetime import datetime, time
from enum import IntEnum
from typing import Annotated, Any

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
    evening: Annotated[BoolBit, pydantic.Field(alias="sb")]
    tags: Annotated[list[Any], pydantic.Field(alias="tg")]
    type: Annotated[Type, pydantic.Field(alias="tp")]
    due_date_suppression_date: Annotated[Timestamp | None, pydantic.Field(alias="dds")]
    repeating_template: Annotated[list[str], pydantic.Field(alias="rt")]
    repeater_migration_date: Annotated[
        Any, pydantic.Field(alias="rmd")
    ]  # TODO: date type yet to be seen
    delegate: Annotated[
        list[Any], pydantic.Field(alias="dl")
    ]  # TODO: date type yet to be seen
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
        todo = TodoItem(
            index=self.index,
            title=self.title,
            creation_date=self.creation_date,
            modification_date=self.modification_date,
            scheduled_date=self.scheduled_date,
            today_index_reference_date=self.today_index_reference_date,
            completion_date=self.completion_date,
            due_date=self.due_date,
            trashed=self.trashed,
            instance_creation_paused=self.instance_creation_paused,
            tags=self.tags,
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
        todo._status = self.status
        todo._destination = self.destination
        todo._projects = self.projects
        todo._areas = self.areas
        todo._evening = self.evening
        todo._type = self.type
        todo._api_object = self
        return todo


class TodoItem(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(validate_assignment=True)

    _uuid: Annotated[str, pydantic.StringConstraints(min_length=22, max_length=22)] = (
        pydantic.PrivateAttr(default_factory=Util.uuid)
    )
    index: int = pydantic.Field(default=0)
    title: str
    _status: Status = pydantic.PrivateAttr(default=Status.TODO)
    _destination: Destination = pydantic.PrivateAttr(default=Destination.INBOX)
    creation_date: datetime | None = pydantic.Field(default_factory=Util.now)
    modification_date: datetime | None = pydantic.Field(default_factory=Util.now)
    scheduled_date: datetime | None = pydantic.Field(default=None)
    today_index_reference_date: datetime | None = pydantic.Field(
        default=None, repr=False
    )
    completion_date: datetime | None = pydantic.Field(default=None)
    due_date: datetime | None = pydantic.Field(default=None)
    trashed: bool = pydantic.Field(default=False)
    instance_creation_paused: bool = pydantic.Field(default=False)
    _projects: list[str] = pydantic.PrivateAttr(default_factory=list)
    _areas: list[str] = pydantic.PrivateAttr(default_factory=list)
    _evening: bool = pydantic.PrivateAttr(default=False)
    tags: list[Any] = pydantic.Field(default_factory=list)  # TODO: set data type
    _type: Type = pydantic.PrivateAttr(default=Type.TASK)
    due_date_suppression_date: datetime | None = pydantic.Field(default=None)
    repeating_template: list[str] = pydantic.Field(default_factory=list)
    repeater_migration_date: Any = pydantic.Field(default=None)
    delegate: list[Any] = pydantic.Field(default_factory=list)
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
            today_index_reference_date=self.today_index_reference_date,
            completion_date=self.completion_date,
            due_date=self.due_date,
            trashed=self.trashed,
            instance_creation_paused=self.instance_creation_paused,
            projects=self._projects,
            areas=self._areas,
            evening=self.is_evening,
            tags=self.tags,
            type=self._type,
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

    @property
    def uuid(self) -> str:
        return self._uuid

    @pydantic.computed_field
    @property
    def type(self) -> Type:
        return self._type

    @property
    def project(self) -> str | None:
        return self._projects[0] if self._projects else None

    @project.setter
    def project(self, project: TodoItem | str | None) -> None:
        if isinstance(project, TodoItem):
            if project.type is not Type.PROJECT:
                raise ValueError("argument must be a project")
            if self.uuid == project.uuid:
                raise ValueError("cannot assign self as project")
            self._projects = [project.uuid]
        elif project:
            if self.uuid == project:
                raise ValueError("cannot assign self as project")
            self._projects = [project]

        if not project:
            self._projects.clear()
            return

        # clear area
        if self.area:
            self.area = None
        # move out of inbox
        if self.destination is Destination.INBOX:
            self.destination = Destination.ANYTIME

    @property
    def area(self) -> str | None:
        return self._areas[0] if self._areas else None

    @area.setter
    def area(self, area: str | None) -> None:
        if not area:
            self._areas.clear()
            return
        self._areas = [area]

        # clear project
        if self.project:
            self.project = None
        # move out of inbox
        if self.destination is Destination.INBOX:
            self.destination = Destination.ANYTIME

    @pydantic.computed_field
    @property
    def status(self) -> Status:
        return self._status

    @status.setter
    def status(self, status: Status) -> None:
        if self._status is status:
            raise ValueError(f"item already has {status.name.lower()} status")
        self._status = status
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

    @pydantic.computed_field
    @property
    def destination(self) -> Destination:
        return self._destination

    @destination.setter
    def destination(self, destination: Destination) -> None:
        if self.type is not Type.TASK:
            raise ValueError("destination can only be changed for a task")
        self._destination = destination

    def delete(self) -> None:
        if self.trashed:
            raise ValueError("item is already trashed")
        self.trashed = True

    def restore(self) -> None:
        if not self.trashed:
            raise ValueError("item is not trashed")
        self.trashed = False

    def as_project(self) -> TodoItem:
        if self._type is not Type.TASK:
            raise ValueError("only a task can be converted to project")
        self._type = Type.PROJECT
        self.instance_creation_paused = True
        if self._destination is Destination.INBOX:
            self._destination = Destination.ANYTIME
        return self

    # @scheduled_date.setter
    # @mod("scheduled_date_", "today_index_reference_date_")
    # def scheduled_date(self, scheduled_date: datetime | None) -> None:
    #     self.scheduled_date_ = scheduled_date
    #     self.today_index_reference_date_ = scheduled_date

    @property
    def is_today(self) -> bool:
        return (
            self.destination is Destination.ANYTIME
            and self.scheduled_date == Util.today()
        )

    @property
    def is_evening(self) -> bool:
        return self.is_today and self._evening

    def evening(self) -> None:
        self.today()
        self._evening = True

    def today(self) -> None:
        today = Util.today()
        self.destination = Destination.ANYTIME
        self.scheduled_date = today

    # def update(self, update: TodoItem, keys: set[str]) -> None:
    #     for key in translate_keys_deserialize(keys):
    #         val = getattr(update, key)
    #         setattr(self, key, val)
