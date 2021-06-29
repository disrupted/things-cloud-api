from __future__ import annotations

import json
import random
import string
from datetime import date, datetime, timedelta, timezone
from enum import Enum

import requests
from loguru import logger
from requests.exceptions import RequestException
from requests.models import Response

from settings import ACCOUNT, APP_ID, USER_AGENT

API_BASE = "https://cloud.culturedcode.com/version/1"

headers = {
    "Accept": "application/json",
    "Accept-Charset": "UTF-8",
    "Accept-Language": "en-gb",
    "Host": "cloud.culturedcode.com",
    "User-Agent": USER_AGENT,
}


class Destination(int, Enum):
    # status: {0: inbox, 1: today/evening, 2: someday}
    INBOX = 0
    TODAY = 1
    SOMEDAY = 2


def now() -> datetime:
    return datetime.now()


def get_timestamp() -> float:
    return datetime.now().timestamp()


def today() -> datetime:
    tz_local = datetime.now(timezone.utc).astimezone().tzinfo
    return datetime.combine(date.today(), datetime.min.time(), tz_local)


def offset_date(dt: datetime, days: int) -> datetime:
    return dt + timedelta(days=days)


def as_timestamp(dt: datetime) -> int:
    return int(dt.replace(tzinfo=timezone.utc).timestamp())


def create_random_string(len: int = 22) -> str:
    # TODO: use uuid module here instead?
    return "".join(random.choices(string.ascii_letters, k=len))


def request(
    method: str,
    endpoint: str,
    params: dict = {},
    headers: dict = headers,
    data: str | None = None,
) -> Response | None:
    try:
        response = requests.request(
            method=method,
            url=f"{API_BASE}/{endpoint}",
            params=params,
            headers=headers,
            data=data,
        )
        logger.debug(f"Status: {response.status_code}")
        logger.debug(f"Body: {response.content}")
        return response
    except RequestException as e:
        logger.error("HTTP Request failed", e)


def get_current_index(index: int) -> int | None:
    response = request(
        method="GET",
        endpoint=f"history/{ACCOUNT}/items",
        params={
            "start-index": str(index),
        },
    )
    if not response:
        return
    if response.status_code == 200:
        return response.json()["current-item-index"]
    else:
        logger.error("Error getting current index", response.content)


def create_todo(
    index: int,
    title: str,
    destination: Destination,
    scheduled_date: datetime | None = None,
    due_date: datetime | None = None,
    # *args,
    # **kwargs,
) -> int | None:
    uuid = create_random_string()
    # now = Util.now()

    # create todo object
    # item = TodoItem(
    #     # *args,
    #     # **kwargs
    #     index=index,
    #     title=title,
    #     destination=destination,
    #     # creation_date=now,
    #     # modification_date=now,
    #     scheduled_date=scheduled_date,
    #     due_date=due_date,
    # )

    # send API request
    response = request(
        method="POST",
        endpoint=f"history/{ACCOUNT}/commit",
        params={
            "ancestor-index": str(index),
            "_cnt": "1",
        },
        headers={
            **headers,
            "Schema": "301",
            "Content-Type": "application/json; charset=UTF-8",
            "App-Id": APP_ID,
            "App-Instance-Id": f"-{APP_ID}",
            "Push-Priority": "5",
        },
        data=json.dumps(
            {uuid: {"t": 0, "e": "Task6", "p": {}}}  # TODO  # item.dict(),
        ),
    )
    if not response:
        return
    if response.status_code == 200:
        return response.json()["server-head-index"]
    else:
        logger.error("Error creating new item", response.content)


if __name__ == "__main__":
    index = get_current_index(1540)
    logger.debug(f"current index: {index}")
    due_date = today() + timedelta(days=2)
    if index is not None:
        new_index = create_todo(
            index,
            "HELLO WORLD",
            destination=Destination.INBOX,
            # due_date=due_date,
        )
        logger.debug(f"new index: {new_index}")
