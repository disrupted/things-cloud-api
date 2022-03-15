import httpx
from httpx import Request, RequestError, Response
from structlog import get_logger

from things_cloud.api.const import API_BASE, HEADERS
from things_cloud.api.exceptions import ThingsCloudException
from things_cloud.models.serde import JsonSerde
from things_cloud.models.todo import TodoItem
from things_cloud.utils import Util

log = get_logger()


class ThingsClient:
    def __init__(self, acc: str, initial_offset: int | None = None):
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
        self._offset = self.__get_current_index(self._offset)

    def create(self, todo: TodoItem) -> int:
        self.update()
        todo.index = self._offset + 1
        return self.__create_todo(self._offset, todo)

    def complete_todo(self, uuid: str, index: int):
        item = TodoItem.complete()
        self.__modify_todo(uuid, index, item)

    def delete_todo(self, uuid: str, index: int):
        item = TodoItem.delete()
        self.__modify_todo(uuid, index, item)

    def __request(self, method: str, endpoint: str, **kwargs) -> Response:
        try:
            return self._client.request(method, endpoint, **kwargs)
        except RequestError as e:
            raise ThingsCloudException from e

    def __get_current_index(self, index: int) -> int:
        response = self.__request(
            "GET",
            "/items",
            params={
                "start-index": str(index),
            },
        )
        if response and response.status_code == 200:
            return response.json()["current-item-index"]
        else:
            log.error("Error getting current index", response=response)
            raise ThingsCloudException

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

    def __create_todo(self, index: int, item: TodoItem) -> int:
        uuid = Util.uuid()
        data = {uuid: {"t": 0, "e": "Task6", "p": item.serialize_dict()}}
        log.debug("", data=data)

        try:
            return self.__commit(index, data)
        except ThingsCloudException as e:
            log.error("Error creating todo")
            raise e

    def __modify_todo(self, uuid: str, index: int, item: TodoItem) -> int:
        data = {uuid: {"t": 1, "e": "Task6", "p": item.serialize_dict()}}
        log.debug("", data=data)

        try:
            return self.__commit(index, data)
        except ThingsCloudException as e:
            log.error("Error modifying todo")
            raise e
