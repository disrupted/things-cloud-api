from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, time
from enum import IntEnum, StrEnum
from typing import Annotated, Any, Literal

import pydantic

from things_cloud.models.types import (
    BoolBit,
    ShortUUID,
    TimeInt,
    TimestampFloat,
    TimestampInt,
)
from things_cloud.utils import Util


class CommitResponse(pydantic.BaseModel):
    server_head_index: Annotated[
        pydantic.PositiveInt, pydantic.Field(alias="server-head-index")
    ]


class HistoryResponse(pydantic.BaseModel):
    current_item_index: Annotated[
        pydantic.PositiveInt, pydantic.Field(alias="current-item-index")
    ]
    end_total_content_size: Annotated[
        pydantic.PositiveInt, pydantic.Field(alias="end-total-content-size")
    ]
    latest_total_content_size: Annotated[
        pydantic.PositiveInt, pydantic.Field(alias="latest-total-content-size")
    ]
    schema_: Annotated[pydantic.PositiveInt, pydantic.Field(alias="schema")]  # 301
    start_total_content_size: Annotated[
        pydantic.PositiveInt, pydantic.Field(alias="start-total-content-size")
    ]
    items: Annotated[list[dict[str, Body]], pydantic.Field(min_length=1)]

    @property
    def updates(self) -> Iterator[Update]:
        for item in self.items:
            assert (
                isinstance(item, dict) and len(item) == 1
            ), "Expected items dict with one key-value pair"
            key, value = next(iter(item.items()))
            yield Update(id=key, body=value)


class Update(pydantic.BaseModel):
    id: ShortUUID
    body: Body = pydantic.Field(discriminator="type")

    # @pydantic.model_validator(mode="after")
    # def inject_task_id(self) -> Self:
    #     self.body.payload._uuid = self.id
    #     return self

    def to_api_payload(self) -> dict[ShortUUID, dict[str, Any]]:
        return {self.id: self.body.to_api_payload()}


class UpdateType(IntEnum):
    NEW = 0
    EDIT = 1
    DELETE = 2


class EntityType(StrEnum):
    TASK = "Task6"
    CHECKLIST_ITEM = "ChecklistItem3"
    AREA = "Area2"
    TAG = "Tag4"


class NewBody(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    type: Annotated[Literal[UpdateType.NEW], pydantic.Field(alias="t")] = UpdateType.NEW
    payload: Annotated[TodoApiObject, pydantic.Field(alias="p")]
    entity: Annotated[EntityType, pydantic.Field(alias="e")] = EntityType.TASK

    def to_api_payload(self) -> dict[str, Any]:
        return self.model_dump(mode="json", by_alias=True)


class EditBody(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    type: Annotated[Literal[UpdateType.EDIT], pydantic.Field(alias="t")] = (
        UpdateType.EDIT
    )
    payload: Annotated[TodoDeltaApiObject, pydantic.Field(alias="p")]
    entity: Annotated[EntityType, pydantic.Field(alias="e")] = EntityType.TASK

    def to_api_payload(self) -> dict[str, Any]:
        return self.model_dump(mode="json", by_alias=True, exclude_none=True)


class TodoDeleteApiObject(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")


class DeleteBody(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    type: Annotated[Literal[UpdateType.DELETE], pydantic.Field(alias="t")] = (
        UpdateType.DELETE
    )
    payload: Annotated[TodoDeleteApiObject, pydantic.Field(alias="p")] = (
        TodoDeleteApiObject()  # empty payload
    )
    entity: Annotated[EntityType, pydantic.Field(alias="e")]

    def to_api_payload(self) -> dict[str, Any]:
        return self.model_dump(mode="json", by_alias=True, exclude_none=True)


Body = Annotated[NewBody | EditBody | DeleteBody, pydantic.Field(discriminator="type")]


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
    t_: Annotated[str, pydantic.Field(alias="_t")] = "tx"
    ch: int = 0
    value: Annotated[str, pydantic.Field(alias="v")] = ""  # value
    t: int = 1


class XX(pydantic.BaseModel):
    sn: dict = {}
    t_: Annotated[str, pydantic.Field(alias="_t")] = "oo"


class TodoApiObject(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    index: Annotated[int, pydantic.Field(alias="ix")]
    title: Annotated[str, pydantic.Field(alias="tt")]
    status: Annotated[Status, pydantic.Field(alias="ss")]
    destination: Annotated[Destination, pydantic.Field(alias="st")]
    creation_date: Annotated[TimestampFloat, pydantic.Field(alias="cd")]
    modification_date: Annotated[TimestampFloat, pydantic.Field(alias="md")]
    scheduled_date: Annotated[TimestampInt | None, pydantic.Field(alias="sr")]
    today_index_reference_date: Annotated[
        TimestampInt | None, pydantic.Field(alias="tir")
    ]
    completion_date: Annotated[TimestampInt | None, pydantic.Field(alias="sp")]
    due_date: Annotated[TimestampInt | None, pydantic.Field(alias="dd")]
    trashed: Annotated[bool, pydantic.Field(alias="tr")]
    instance_creation_paused: Annotated[bool, pydantic.Field(alias="icp")]
    projects: Annotated[list[str], pydantic.Field(alias="pr")]
    areas: Annotated[list[str], pydantic.Field(alias="ar")]
    evening: Annotated[BoolBit, pydantic.Field(alias="sb")]
    tags: Annotated[list[Any], pydantic.Field(alias="tg")]
    type: Annotated[Type, pydantic.Field(alias="tp")]
    due_date_suppression_date: Annotated[
        TimestampInt | None, pydantic.Field(alias="dds")
    ]
    repeating_template: Annotated[list[str], pydantic.Field(alias="rt")]
    repeater_migration_date: Annotated[
        Any, pydantic.Field(alias="rmd")
    ]  # TODO: date type yet to be seen
    delegate: Annotated[
        list[Any], pydantic.Field(alias="dl")
    ]  # TODO: date type yet to be seen
    due_date_offset: Annotated[int, pydantic.Field(alias="do")]
    last_alarm_interaction_date: Annotated[
        TimestampInt | None, pydantic.Field(alias="lai")
    ]
    action_group: Annotated[list[str], pydantic.Field(alias="agr")]
    leaves_tombstone: Annotated[bool, pydantic.Field(alias="lt")]
    instance_creation_count: Annotated[int, pydantic.Field(alias="icc")]
    today_index: Annotated[int, pydantic.Field(alias="ti")]
    reminder: Annotated[TimeInt | None, pydantic.Field(alias="ato")]
    instance_creation_start_date: Annotated[
        TimestampInt | None, pydantic.Field(alias="icsd")
    ]
    repeater: Annotated[Any, pydantic.Field(alias="rp")]
    after_completion_reference_date: Annotated[
        TimestampInt | None, pydantic.Field(alias="acrd")
    ]
    recurrence_rule: Annotated[str | None, pydantic.Field(alias="rr")]
    note: Annotated[Note, pydantic.Field(alias="nt")]
    xx: Annotated[XX, pydantic.Field(alias="xx")]
    # task: Annotated[
    #     list[ShortUUID] | None,
    #     pydantic.Field(
    #         alias="ts", description="for checklist items, references parent task"
    #     ),
    # ] = None  # exclude otherwise
    # sh: Annotated[Any | None, pydantic.Field(alias="sh", description="for Tag")] = None
    # pn: Annotated[list, pydantic.Field(alias="pn", description="for Tag")] = []

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
        todo._synced_state = self
        return todo


class TodoDeltaApiObject(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    index: Annotated[int | None, pydantic.Field(alias="ix")] = None
    title: Annotated[str | None, pydantic.Field(alias="tt")] = None
    status: Annotated[Status | None, pydantic.Field(alias="ss")] = None
    destination: Annotated[Destination | None, pydantic.Field(alias="st")] = None
    creation_date: Annotated[TimestampFloat | None, pydantic.Field(alias="cd")] = None
    modification_date: Annotated[TimestampFloat, pydantic.Field(alias="md")] = (
        pydantic.Field(default_factory=Util.now)
    )
    scheduled_date: Annotated[TimestampInt | None, pydantic.Field(alias="sr")] = None
    today_index_reference_date: Annotated[
        TimestampInt | None, pydantic.Field(alias="tir")
    ] = None
    completion_date: Annotated[TimestampInt | None, pydantic.Field(alias="sp")] = None
    due_date: Annotated[TimestampInt | None, pydantic.Field(alias="dd")] = None
    trashed: Annotated[bool | None, pydantic.Field(alias="tr")] = None
    instance_creation_paused: Annotated[bool | None, pydantic.Field(alias="icp")] = None
    projects: Annotated[list[str] | None, pydantic.Field(alias="pr")] = None
    areas: Annotated[list[str] | None, pydantic.Field(alias="ar")] = None
    evening: Annotated[BoolBit | None, pydantic.Field(alias="sb")] = None
    tags: Annotated[list[Any] | None, pydantic.Field(alias="tg")] = None
    type: Annotated[Type | None, pydantic.Field(alias="tp")] = None
    due_date_suppression_date: Annotated[
        TimestampInt | None, pydantic.Field(alias="dds")
    ] = None
    repeating_template: Annotated[list[str] | None, pydantic.Field(alias="rt")] = None
    repeater_migration_date: Annotated[Any | None, pydantic.Field(alias="rmd")] = None
    delegate: Annotated[list[Any] | None, pydantic.Field(alias="dl")] = None
    due_date_offset: Annotated[int | None, pydantic.Field(alias="do")] = None
    last_alarm_interaction_date: Annotated[
        TimestampInt | None, pydantic.Field(alias="lai")
    ] = None
    action_group: Annotated[list[str] | None, pydantic.Field(alias="agr")] = None
    leaves_tombstone: Annotated[bool | None, pydantic.Field(alias="lt")] = None
    instance_creation_count: Annotated[int | None, pydantic.Field(alias="icc")] = None
    today_index: Annotated[int | None, pydantic.Field(alias="ti")] = None
    reminder: Annotated[TimeInt | None, pydantic.Field(alias="ato")] = None
    instance_creation_start_date: Annotated[
        TimestampInt | None, pydantic.Field(alias="icsd")
    ] = None
    repeater: Annotated[Any | None, pydantic.Field(alias="rp")] = None
    after_completion_reference_date: Annotated[
        TimestampInt | None, pydantic.Field(alias="acrd")
    ] = None
    recurrence_rule: Annotated[str | None, pydantic.Field(alias="rr")] = None
    note: Annotated[Note | None, pydantic.Field(alias="nt")] = None
    xx: Annotated[XX | None, pydantic.Field(alias="xx")] = None

    def apply_edits(self, todo: TodoItem) -> None:
        keys = self.model_dump(by_alias=False, exclude_none=True).keys()
        if not keys:
            raise RuntimeError("there are no edits to apply")
        for key in keys:
            old_value = getattr(todo, key)
            new_value = getattr(self, key)
            if old_value == new_value:
                msg = f"old and new value are identical: {new_value}"
                raise ValueError(msg)
            setattr(todo, key, new_value)


class TodoItem(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(validate_assignment=True)

    _uuid: ShortUUID = pydantic.PrivateAttr(default_factory=Util.uuid)
    index: int = pydantic.Field(default=0)
    title: str
    _status: Status = pydantic.PrivateAttr(default=Status.TODO)
    _destination: Destination = pydantic.PrivateAttr(default=Destination.INBOX)
    creation_date: datetime = pydantic.Field(default_factory=Util.now)
    modification_date: datetime = pydantic.Field(default_factory=Util.now)
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
    xx: XX = pydantic.Field(default_factory=XX)
    _synced_state: TodoApiObject | None = pydantic.PrivateAttr(default=None)

    def to_update(self) -> Update:
        if not self._synced_state:
            complete = self._to_new()
            body = NewBody(payload=complete)
            update = Update(id=self.uuid, body=body)
        else:
            delta = self._to_edit()
            body = EditBody(payload=delta)
            update = Update(id=self.uuid, body=body)
        return update

    def _to_new(self) -> TodoApiObject:
        if self._synced_state:
            msg = (
                f"current version exists for todo, use {self._to_edit.__name__} instead"
            )
            raise ValueError(msg)

        self.modification_date = Util.now()
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
            xx=self.xx,
        )

    def _to_edit(self) -> TodoDeltaApiObject:
        if not self._synced_state:
            msg = f"no current version exists for todo, use {self._to_new.__name__} instead"
            raise ValueError(msg)

        keys = self.model_dump(by_alias=False).keys()
        edits = {}
        for key in keys:
            current_value = getattr(self._synced_state, key)
            new_value = getattr(self, key)
            if current_value == new_value:
                continue
            edits[key] = new_value
        if not edits:
            raise ValueError("no changes found")
        return TodoDeltaApiObject.model_validate(edits)

    def _commit(
        self,
        complete_or_delta: TodoApiObject | TodoDeltaApiObject | TodoDeleteApiObject,
    ) -> None:
        if isinstance(complete_or_delta, TodoApiObject):
            self._synced_state = complete_or_delta
        elif isinstance(complete_or_delta, TodoDeleteApiObject):
            self._synced_state = None

        else:
            delta = complete_or_delta.model_dump(by_alias=False, exclude_none=True)
            for key in delta.keys():
                new_value = getattr(complete_or_delta, key)
                setattr(self._synced_state, key, new_value)

    @property
    def uuid(self) -> ShortUUID:
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
