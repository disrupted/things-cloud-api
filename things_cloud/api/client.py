from typing import Any

import httpx
from httpx import Request, RequestError, Response
from structlog import get_logger

from things_cloud.api.const import API_BASE, HEADERS
from things_cloud.api.exceptions import ThingsCloudException, ThingsUpdateException
from things_cloud.models.serde import JsonSerde
from things_cloud.models.todo import TodoItem, deserialize, serialize_dict
from things_cloud.utils import Util

log = get_logger()


class ThingsClient:
    def __init__(self, acc: str, initial_offset: int | None = None):
        self._items: dict[str, TodoItem] = {}  # TODO: create DB
        self._base_url: str = f"{API_BASE}/history/{acc}"
        self._client = httpx.Client(
            base_url=self._base_url,
            headers=HEADERS,
            event_hooks={
                "request": [self.log_request],
                "response": [self.raise_on_4xx_5xx, self.log_response],
            },
        )
        if initial_offset:
            self._offset: int = initial_offset
        else:
            self.update()

    def __del__(self):
        self._client.close()

    @staticmethod
    def log_request(request: Request):
        log.debug(f"Request: {request.method} {request.url} - Waiting for response")

    @staticmethod
    def raise_on_4xx_5xx(response: Response):
        """Raises a HTTPStatusError on 4xx and 5xx responses."""
        response.raise_for_status()

    @staticmethod
    def log_response(response: Response):
        request = response.request
        log.debug(
            f"Response: {request.method} {request.url}", status=response.status_code
        )
        response.read()  # access response body
        log.debug("Body", content=response.content)

    @property
    def offset(self) -> int:
        return self._offset

    def update(self):
        self._offset = self.__fetch(self._offset)

    def create(self, item: TodoItem) -> None:
        self.update()
        item._index = self._offset + 1
        self.__create_todo(self._offset, item)

    def edit(self, item: TodoItem) -> None:
        self.__modify_todo(self._offset, item)

    def __request(self, method: str, endpoint: str, **kwargs) -> Response:
        try:
            return self._client.request(method, endpoint, **kwargs)
        except RequestError as e:
            raise ThingsCloudException from e

    def __fetch(self, index: int) -> int:
        response = self.__request(
            "GET",
            "/items",
            params={
                "start-index": str(index),
            },
        )
        if response.status_code == 200:
            data = response.json()
            self._process_updates(data)
            return data["current-item-index"]
        else:
            log.error("Error getting current index", response=response)
            raise ThingsCloudException

    def _process_updates(self, data: dict) -> None:
        if not data["items"]:
            return

        updates: list[dict[str, dict]] = data["items"]
        for update in updates:
            for uuid, body in update.items():  # actually just one item
                log.debug("found update", uuid=uuid, body=body)
                item: dict[str, Any] = body["p"]
                todo = deserialize(item)
                todo._uuid = uuid
                if body["t"] == 0:  # new todo
                    self._items[uuid] = todo
                elif body["t"] == 1:  # edited todo
                    self._apply_edits(todo, set(item.keys()))
                else:
                    raise ThingsUpdateException

    def _apply_edits(self, update: TodoItem, keys: set[str]) -> None:
        try:
            self._items[update.uuid].update(update, keys)
        except KeyError:
            log.error(f"todo {update.uuid} not found")

    # HACK: temporary
    def today(self) -> list[TodoItem]:
        return [
            item
            for _, item in self._items.items()
            if item.scheduled_date == Util.today()
        ]

    def __commit(
        self,
        index: int,
        data: dict | None = None,
    ) -> int:
        response = self.__request(
            method="POST",
            endpoint="/commit",
            params={
                "ancestor-index": str(index),
                "_cnt": "1",
            },
            content=JsonSerde.dumps(data),
        )
        return response.json()["server-head-index"]

    def __create_todo(self, index: int, item: TodoItem) -> None:
        data = {item.uuid: {"t": 0, "e": "Task6", "p": serialize_dict(item)}}
        log.debug("", data=data)

        try:
            self._offset = self.__commit(index, data)
            item.reset_changes()
        except ThingsCloudException as e:
            log.error("Error creating todo")
            raise e

    def __modify_todo(self, index: int, item: TodoItem) -> None:
        changes = item.changes
        if not changes:
            log.warning("there are no changes to be sent")
            return
        data = {item.uuid: {"t": 1, "e": "Task6", "p": serialize_dict(item, changes)}}
        log.debug("", data=data)

        try:
            self._offset = self.__commit(index, data)
            item.reset_changes()
        except ThingsCloudException as e:
            log.error("Error modifying todo")
            raise e
