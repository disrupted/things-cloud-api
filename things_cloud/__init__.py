from __future__ import annotations

import requests
from loguru import logger
from requests.exceptions import RequestException
from requests.models import Response

from .serde import JsonSerde
from .settings import APP_ID, USER_AGENT
from .todo import TodoItem
from .utils import Util

__version__ = "0.1.0"

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


class ThingsClient:
    def __init__(self, acc: str):
        self._acc = acc
        self._offset = 0

    def __refresh_offset(self):
        self._offset = self.__get_current_index(self._offset)

    def create(self, todo: TodoItem) -> int:
        self.__refresh_offset()
        todo.index = self._offset + 1
        return self.__create_todo(self._offset, todo)

    def complete_todo(self, uuid: str, index: int):
        item = TodoItem.complete()
        self.__modify_todo(uuid, index, item)

    def delete_todo(self, uuid: str, index: int):
        item = TodoItem.delete()
        self.__modify_todo(uuid, index, item)

    def __request(
        self,
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

    def __get_current_index(self, index: int) -> int:
        response = self.__request(
            method="GET",
            endpoint=f"history/{self._acc}/items",
            params={
                "start-index": str(index),
            },
        )
        if response and response.status_code == 200:
            return response.json()["current-item-index"]
        else:
            logger.error("Error getting current index", response)
            raise ThingsCloudException

    def __create_todo(self, index: int, item: TodoItem) -> int:
        uuid = Util.uuid()
        data = JsonSerde.prettydumps(
            {uuid: {"t": 0, "e": "Task6", "p": item.serialize_dict()}}
        )
        logger.debug(data)

        # send API request
        response = self.__request(
            method="POST",
            endpoint=f"history/{self._acc}/commit",
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

    def __modify_todo(self, uuid: str, index: int, item: TodoItem) -> int:
        data = JsonSerde.prettydumps(
            {uuid: {"t": 1, "e": "Task6", "p": item.serialize_dict()}}
        )
        logger.debug(data)

        # send API request
        response = self.__request(
            method="POST",
            endpoint=f"history/{self._acc}/commit",
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
