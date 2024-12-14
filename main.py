import os
from time import sleep

from structlog import get_logger

from things_cloud import ThingsClient
from things_cloud.api.account import Account, Credentials
from things_cloud.models import TodoItem

log = get_logger()

EMAIL = os.environ["THINGS_EMAIL"]
PASSWORD = os.environ["THINGS_PASSWORD"]


def main():
    credentials = Credentials(email=EMAIL, password=PASSWORD)
    account = Account.login(credentials)
    things = ThingsClient(account)

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
