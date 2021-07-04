from __future__ import annotations

import json
from datetime import datetime, timedelta

import requests
from loguru import logger
from requests.exceptions import RequestException
from requests.models import Response

from settings import ACCOUNT, APP_ID, USER_AGENT
from todo import Destination, TodoItem, Util

API_BASE = "https://cloud.culturedcode.com/version/1"

headers = {
    "Accept": "application/json",
    "Accept-Charset": "UTF-8",
    "Accept-Language": "en-gb",
    "Host": "cloud.culturedcode.com",
    "User-Agent": USER_AGENT,
}


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
    uuid = Util.uuid()
    # now = Util.now()

    # create todo object
    item = TodoItem(
        # *args,
        # **kwargs
        index=index,
        title=title,
        destination=destination,
        # creation_date=now,
        # modification_date=now,
        scheduled_date=scheduled_date,
        due_date=due_date,
    )

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
        data=json.dumps({uuid: {"t": 0, "e": "Task6", "p": item.dict()}}),
    )
    if not response:
        return
    if response.status_code == 200:
        return response.json()["server-head-index"]
    else:
        logger.error("Error creating new item", response.content)


def modify_todo(
    uuid: str,
    item: TodoItem,
    # index: int,
    # title: str,
    # destination: Destination,
    # scheduled_date: datetime | None = None,
    # due_date: datetime | None = None,
    # *args,
    # **kwargs,
) -> int | None:
    # item = TodoItem(*args, **kwargs)

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
        data=json.dumps({uuid: {"t": 1, "e": "Task6", "p": item.dict()}}),
    )
    if not response:
        return
    if response.status_code == 200:
        return response.json()["server-head-index"]
    else:
        logger.error("Error creating new item", response.content)


def complete_todo(uuid: str):
    item = TodoItem.complete()
    modify_todo(uuid=uuid, item=item)


def delete_todo(uuid: str):
    # item = TodoItem(in_trash=True)
    # item.copy(include={"in_trash"})
    item = TodoItem.delete()
    modify_todo(uuid=uuid, item=item)


if __name__ == "__main__":
    index = get_current_index(1540)
    logger.debug(f"current index: {index}")
    due_date = Util.today() + timedelta(days=2)
    if index is not None:
        new_index = create_todo(
            index,
            "HELLO WORLD",
            destination=Destination.INBOX,
            # due_date=due_date,
        )
        logger.debug(f"new index: {new_index}")
