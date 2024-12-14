from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import datetime, time, timezone
from typing import Any

import orjson


class Serde(ABC):
    field_serializers: dict[str, Callable]
    type_serializers: dict[type, Callable]

    @abstractmethod
    def serialize(self, v, *, default=None) -> str: ...

    @abstractmethod
    def deserialize(self, v) -> Any: ...


class JsonSerde(Serde):
    @staticmethod
    def dumps(v, *, default=None, indent: int | None = None) -> str:
        # orjson.dumps returns bytes, to match standard json.dumps we need to decode
        kw = {}
        if indent is not None:
            kw["option"] = indent
        return orjson.dumps(v, default=default, **kw).decode()

    @staticmethod
    def prettydumps(v, *, default=None) -> str:
        return JsonSerde.dumps(v, default=default, indent=orjson.OPT_INDENT_2)

    # @override  # TODO
    def serialize(self, v, *, default=None) -> str:
        for key, value in v.items():
            if serializer := self.field_serializers.get(key):
                v[key] = serializer(value)
            elif serializer := self.type_serializers.get(type(value)):
                v[key] = serializer(value)

        return JsonSerde.prettydumps(v, default=default)

    # @override  # TODO
    def deserialize(self, v: bytes | bytearray | str) -> Any:
        return orjson.loads(v)


class TodoSerde(JsonSerde):
    field_serializers: dict[str, Callable] = {
        "sb": lambda v: int(v),
        "sr": lambda d: TodoSerde.timestamp_rounded(d),
        "tir": lambda d: TodoSerde.timestamp_rounded(d),
        "dd": lambda d: TodoSerde.timestamp_rounded(d),
    }

    type_serializers: dict[type, Callable] = {
        time: lambda t: (t.hour * 60 + t.minute) * 60 + t.second,
        datetime: lambda d: d.timestamp(),
    }

    @staticmethod
    def from_timestamp(timestamp: datetime | int) -> datetime:
        if isinstance(timestamp, datetime):
            return timestamp
        return datetime.fromtimestamp(timestamp, timezone.utc)

    @staticmethod
    def timestamp_rounded(dt: datetime | None) -> int | None:
        if dt is None:
            return None
        return int(dt.timestamp())
