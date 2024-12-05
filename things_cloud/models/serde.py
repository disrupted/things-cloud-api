import datetime as dt
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

import orjson
from typing_extensions import override


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

    @override
    def serialize(self, v, *, default=None) -> str:
        for key, value in v.items():
            if serializer := self.field_serializers.get(key):
                v[key] = serializer(value)
            elif serializer := self.type_serializers.get(type(value)):
                v[key] = serializer(value)

        return JsonSerde.prettydumps(v, default=default)

    @override
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
        dt.time: lambda t: (t.hour * 60 + t.minute) * 60 + t.second,
        dt.datetime: lambda d: d.timestamp(),
    }

    @staticmethod
    def timestamp_rounded(d: dt.datetime | None) -> int | None:
        if d is None:
            return None
        return int(d.timestamp())
