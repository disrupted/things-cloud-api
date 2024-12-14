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

    # create a new project
    project = TodoItem(title="Things Cloud Project").as_project()
    things.commit(project)
    log.debug("created project", uuid=project.uuid)

    sleep(10)
    # create a todo inside project
    todo = TodoItem(title="Try out Things Cloud")
    todo.project = project
    things.commit(todo)

    sleep(10)
    # schedule for today
    todo.today()
    things.commit(todo)


if __name__ == "__main__":
    main()
