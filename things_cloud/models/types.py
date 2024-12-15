from datetime import datetime, time, timezone
from typing import Annotated

import pydantic

ShortUUID = Annotated[str, pydantic.StringConstraints(min_length=22, max_length=22)]


def from_timestamp(timestamp: datetime | int | float) -> datetime:
    if isinstance(timestamp, datetime):
        return timestamp
    return datetime.fromtimestamp(timestamp, timezone.utc)


def timestamp_rounded(dt: datetime) -> int:
    return int(dt.timestamp())


def timestamp_precise(dt: datetime) -> float:
    return dt.timestamp()


def time_to_int(t: time) -> int:
    return (t.hour * 60 + t.minute) * 60 + t.second


TimestampInt = Annotated[
    datetime,
    pydantic.PlainValidator(from_timestamp, json_schema_input_type=datetime | int),
    pydantic.PlainSerializer(timestamp_rounded),
]

TimestampFloat = Annotated[
    datetime,
    pydantic.PlainValidator(from_timestamp, json_schema_input_type=datetime | float),
    pydantic.PlainSerializer(timestamp_precise),
]

TimeInt = Annotated[
    time,
    pydantic.PlainSerializer(time_to_int),
]

BoolBit = Annotated[bool, pydantic.PlainSerializer(int)]
