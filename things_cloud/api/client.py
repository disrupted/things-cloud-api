import httpx
from httpx import Request, RequestError, Response
from structlog import get_logger

from things_cloud.api.account import Account
from things_cloud.api.const import API_BASE, HEADERS
from things_cloud.api.exceptions import ThingsCloudException
from things_cloud.models.todo import (
    CommitResponse,
    HistoryResponse,
    NewBody,
    TodoItem,
    Update,
    UpdateType,
)
from things_cloud.utils import Util

log = get_logger()


class ThingsClient:
    def __init__(self, account: Account) -> None:
        self._account = account
        self._items: dict[str, TodoItem] = {}  # TODO: create DB
        self._base_url: str = f"{API_BASE}/history/{account._info.history_key}"
        self._client = httpx.Client(
            base_url=self._base_url,
            headers=HEADERS,
            event_hooks={
                "request": [self.log_request],
                "response": [self.raise_on_4xx_5xx, self.log_response],
            },
        )
        self._session = account.new_session()
        self._offset = self._session.head_index

    def __del__(self):
        self._client.close()

    @staticmethod
    def log_request(request: Request) -> None:
        log.debug(f"Request: {request.method} {request.url} - Waiting for response")

    @staticmethod
    def raise_on_4xx_5xx(response: Response) -> None:
        """Raises a HTTPStatusError on 4xx and 5xx responses."""
        response.raise_for_status()

    @staticmethod
    def log_response(response: Response) -> None:
        request = response.request
        log.debug(
            f"Response: {request.method} {request.url}", status=response.status_code
        )
        response.read()  # access response body
        log.debug("Body", content=response.content)

    def update(self) -> None:
        data = self.__fetch(self._offset)
        self._process_updates(data)
        self._offset = data.current_item_index

    def commit(self, item: TodoItem) -> None:
        update = item.to_update()
        try:
            commit = self.__commit(update)
            item._commit(update.body.payload)
            self._offset = commit.server_head_index
        except ThingsCloudException as e:
            log.error("Error commiting")
            raise e

    def __request(self, method: str, endpoint: str, **kwargs) -> Response:
        try:
            return self._client.request(method, endpoint, **kwargs)
        except RequestError as e:
            raise ThingsCloudException from e

    def __fetch(self, index: int) -> HistoryResponse:
        response = self.__request(
            "GET",
            "/items",
            params={
                "start-index": str(index),
            },
        )
        if response.status_code == 200:
            return HistoryResponse.model_validate_json(response.read())
        else:
            log.error("Error getting current index", response=response)
            raise ThingsCloudException

    def _process_updates(self, history: HistoryResponse) -> None:
        for update in history.updates:
            log.debug("processing update", update=update)
            match update.body.type:
                case UpdateType.NEW:
                    assert isinstance(
                        update.body, NewBody
                    )  # HACK: type narrowing does not work
                    item = update.body.payload.to_todo()
                    item._uuid = update.id
                    self._items[item.uuid] = item
                case UpdateType.EDIT:
                    try:
                        item = self._items[update.id]
                    except KeyError as key_err:
                        msg = f"todo {id} not found"
                        raise ValueError(msg) from key_err
                    update.body.payload.apply_edits(item)

    # HACK: temporary
    def today(self) -> list[TodoItem]:
        return [
            item
            for _, item in self._items.items()
            if item.scheduled_date == Util.today()
        ]

    def __commit(self, update: Update) -> CommitResponse:
        index = self._offset
        if update.body.type is UpdateType.NEW:
            index += 1
        response = self.__request(
            method="POST",
            endpoint="/commit",
            params={
                "ancestor-index": str(index),
                "_cnt": "1",
            },
            json=update.to_api_payload(),
        )
        return CommitResponse.model_validate_json(response.read())
