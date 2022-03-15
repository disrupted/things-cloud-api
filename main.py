import os

from structlog import get_logger

from things_cloud import ThingsClient
from things_cloud.models.todo import Destination, TodoItem

log = get_logger()

ACCOUNT = os.environ["THINGS_ACCOUNT"]
OFFSET = int(os.environ.get("THINGS_OFFSET", 0))


def main():
    log.debug("initial offset", offset=OFFSET)
    things = ThingsClient(ACCOUNT, initial_offset=OFFSET)
    log.debug("current index", offset=things.offset)
    todo = TodoItem(title="HELLO WORLD", destination=Destination.INBOX)
    idx = things.create(todo)
    log.debug("new index", index=idx)


if __name__ == "__main__":
    main()
