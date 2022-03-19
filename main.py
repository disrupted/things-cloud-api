import os
from time import sleep

from structlog import get_logger

from things_cloud import ThingsClient
from things_cloud.models import TodoItem

log = get_logger()

ACCOUNT = os.environ["THINGS_ACCOUNT"]
OFFSET = int(os.environ.get("THINGS_OFFSET", 0))


def main():
    things = ThingsClient(ACCOUNT, initial_offset=OFFSET)

    # create a project
    project = TodoItem.create_project("Things Cloud Project")
    project_uuid = things.create(project)
    log.debug("created project", uuid=project_uuid)

    sleep(10)
    # create a todo inside project
    todo = TodoItem("Try out Things Cloud")
    todo.project = project_uuid
    print(todo.changes)
    uuid = things.create(todo)
    print(todo.changes)

    sleep(10)
    # schedule for today
    todo.today()
    print(todo.changes)
    things.edit(uuid, todo)
    print(todo.changes)


if __name__ == "__main__":
    main()
