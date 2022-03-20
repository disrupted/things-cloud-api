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
    project = TodoItem("Things Cloud Project").as_project()
    things.create(project)
    log.debug("created project", uuid=project.uuid)

    sleep(10)
    # create a todo inside project
    todo = TodoItem("Try out Things Cloud")
    todo.project = project
    things.create(todo)

    sleep(10)
    # schedule for today
    todo.today()
    things.edit(todo)


if __name__ == "__main__":
    main()
