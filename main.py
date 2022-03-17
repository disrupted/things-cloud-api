import os
from time import sleep

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
    todo = TodoItem.create("Try out Things Cloud", Destination.INBOX)
    uuid = things.create(todo)
    log.debug("created todo", uuid=uuid)

    things.edit(uuid, TodoItem.set_today())

    sleep(2)
    things.edit(uuid, TodoItem.complete())


if __name__ == "__main__":
    main()
