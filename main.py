import os

from loguru import logger

from things_cloud import ThingsClient
from things_cloud.todo import Destination, TodoItem

ACCOUNT = os.environ["THINGS_ACCOUNT"]
USER_AGENT = os.environ["THINGS_USER_AGENT"]
APP_ID = os.environ.get("THINGS_APP_ID", "com.culturedcode.ThingsMac")

if __name__ == "__main__":
    things = ThingsClient(ACCOUNT)
    todo = TodoItem.create("HELLO WORLD", Destination.INBOX)
    idx = things.create(todo)
    logger.debug("new index: ", idx)
