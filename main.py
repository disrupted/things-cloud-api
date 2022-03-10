import os

from loguru import logger

from things_cloud import ThingsClient
from things_cloud.todo import Destination, TodoItem

ACCOUNT = os.environ["THINGS_ACCOUNT"]
USER_AGENT = os.environ["THINGS_USER_AGENT"]
APP_ID = os.environ.get("THINGS_APP_ID", "com.culturedcode.ThingsMac")
OFFSET = int(os.environ.get("THINGS_OFFSET", 0))


def main():
    logger.debug("initial offset: {}", OFFSET)
    things = ThingsClient(ACCOUNT, initial_offset=OFFSET)
    logger.debug("current index: {}", things.offset)
    todo = TodoItem.create("HELLO WORLD", Destination.INBOX)
    idx = things.create(todo)
    logger.debug("new index: {}", idx)


if __name__ == "__main__":
    main()
