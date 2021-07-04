from __future__ import annotations

import requests
from loguru import logger
from requests.exceptions import RequestException
from requests.models import Response

from settings import ACCOUNT, APP_ID, USER_AGENT
from todo import Destination, TodoItem, Util, orjson_prettydumps

API_BASE = "https://cloud.culturedcode.com/version/1"

headers = {
    "Accept": "application/json",
    "Accept-Charset": "UTF-8",
    "Accept-Language": "en-gb",
    "Host": "cloud.culturedcode.com",
    "User-Agent": USER_AGENT,
    "Schema": "301",
    "Content-Type": "application/json; charset=UTF-8",
    "App-Id": APP_ID,
    "App-Instance-Id": f"-{APP_ID}",
    "Push-Priority": "5",
}


class ThingsCloudException(Exception):
    pass


def request(
    method: str,
    endpoint: str,
    params: dict = {},
    headers: dict = headers,
    data: str | None = None,
) -> Response:
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
        raise ThingsCloudException from e


def get_current_index(index: int) -> int:
    response = request(
        method="GET",
        endpoint=f"history/{ACCOUNT}/items",
        params={
            "start-index": str(index),
        },
    )
    if response and response.status_code == 200:
        return response.json()["current-item-index"]
    else:
        logger.error("Error getting current index", response)
        raise ThingsCloudException


def create_todo(index: int, item: TodoItem) -> int:
    uuid = Util.uuid()
    data = orjson_prettydumps(
        {uuid: {"t": 0, "e": "Task6", "p": item.serialize_dict()}}
    )
    logger.debug(data)

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
        },
        data=data,
    )
    if response and response.status_code == 200:
        return response.json()["server-head-index"]
    else:
        logger.error("Error creating new item", response)
        raise ThingsCloudException


def modify_todo(uuid: str, index: int, item: TodoItem) -> int:
    data = orjson_prettydumps(
        {uuid: {"t": 1, "e": "Task6", "p": item.serialize_dict()}}
    )
    logger.debug(data)

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
        },
        data=data,
    )
    if response and response.status_code == 200:
        return response.json()["server-head-index"]
    else:
        logger.error("Error creating new item", response)
        raise ThingsCloudException


def complete_todo(uuid: str, index: int):
    item = TodoItem.complete()
    modify_todo(uuid, index, item)


def delete_todo(uuid: str, index: int):
    item = TodoItem.delete()
    modify_todo(uuid, index, item)


if __name__ == "__main__":
    index = get_current_index(2290)
    logger.debug(f"current index: {index}")
    if index is not None:
        item = TodoItem.create(index, "HELLO WORLD", Destination.INBOX)
        new_index = create_todo(index, item)
        logger.debug(f"new index: {new_index}")
