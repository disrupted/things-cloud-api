from __future__ import annotations

import requests
from loguru import logger
from requests.exceptions import RequestException
from requests.models import Response

from things_cloud.serde import JsonSerde

from .exceptions import ThingsCloudException
from .settings import APP_ID, USER_AGENT
from .todo import TodoItem
from .utils import Util

__version__ = "0.1.0"

API_BASE = "https://cloud.culturedcode.com/version/1"

HEADERS = {
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


class ThingsClient:
    def __init__(self, acc: str, initial_offset: int | None = None):
        self._acc: str = acc
        if initial_offset:
            self._offset: int = initial_offset
        else:
            self.__refresh_offset()

    @property
    def offset(self) -> int:
        return self._offset

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
        params: dict | None = None,
        headers: dict | None = None,
        data: dict | str | None = None,
    ) -> Response:
        if headers is None:
            headers = HEADERS
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

    def __commit(
        self,
        index: int,
        data: dict | None = None,
    ) -> int:
        try:
            response = self.__request(
                method="POST",
                endpoint=f"history/{self._acc}/commit",
                params={
                    "ancestor-index": str(index),
                    "_cnt": "1",
                },
                headers={
                    **HEADERS,
                },
                data=JsonSerde.dumps(data),
            )
            logger.debug(f"Status: {response.status_code}")
            logger.debug(f"Body: {response.content}")
            return response.json()["server-head-index"]
        except RequestException as e:
            raise ThingsCloudException from e

    def __create_todo(self, index: int, item: TodoItem) -> int:
        uuid = Util.uuid()
        data = {uuid: {"t": 0, "e": "Task6", "p": item.serialize_dict()}}
        logger.debug(data)

        try:
            return self.__commit(index, data)
        except ThingsCloudException as e:
            logger.error("Error creating todo")
            raise e

    def __modify_todo(self, uuid: str, index: int, item: TodoItem) -> int:
        data = {uuid: {"t": 1, "e": "Task6", "p": item.serialize_dict()}}
        logger.debug(data)

        try:
            return self.__commit(index, data)
        except ThingsCloudException as e:
            logger.error("Error modifying todo")
            raise e
