from __future__ import annotations

import datetime as dt
import json
from abc import ABC, abstractmethod
from typing import Any, Callable

import orjson
import pydantic.json


class Serde(ABC):
    field_serializers: dict[str, Callable]
    type_serializers: dict[type, Callable]

    @abstractmethod
    def serialize():
        ...

    @abstractmethod
    def deserialize():
        ...


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

    def serialize(self, v, *, default=None) -> str:
        for key, value in v.items():
            if serializer := self.field_serializers.get(key):
                v[key] = serializer(value)
            elif serializer := self.type_serializers.get(type(value)):
                v[key] = serializer(value)

        return JsonSerde.prettydumps(v, default=default)

    @staticmethod
    def deserialize(v: bytes | bytearray | str) -> Any:
        return orjson.loads(v)


class TodoSerde(JsonSerde):
    field_serializers: dict[str, Callable] = {
        "sb": lambda v: int(v),
        "sr": lambda d: TodoSerde.timestamp_rounded(d),
        "dd": lambda d: TodoSerde.timestamp_rounded(d),
    }

    type_serializers: dict[type, Callable] = {
        dt.time: lambda t: (t.hour * 60 + t.minute) * 60 + t.second,
        dt.datetime: lambda d: d.timestamp(),
    }

    @staticmethod
    def timestamp_rounded(d: dt.datetime | None) -> int | None:
        if d:
            return int(d.timestamp())


class DictSerde(Serde):
    @staticmethod
    def dumps(*args) -> str:
        return json.dumps(*args, default=pydantic.json.pydantic_encoder)

    # @staticmethod
    # def prettydumps(v, *, default=None) -> str:
    #     return JsonSerde.dumps(v, default=default, indent=orjson.OPT_INDENT_2)

    def serialize(self, v) -> str:
        # for key, value in v.items():
        #     if serializer := self.field_serializers.get(key):
        #         v[key] = serializer(value)
        #     elif serializer := self.type_serializers.get(type(value)):
        #         v[key] = serializer(value)

        return DictSerde.dumps(v)
