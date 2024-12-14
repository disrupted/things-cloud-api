import os
from time import sleep

from pydantic import SecretStr
from structlog import get_logger

from things_cloud import ThingsClient
from things_cloud.api.account import Account, Credentials
from things_cloud.models import TodoItem

log = get_logger()

EMAIL = os.environ["THINGS_EMAIL"]
PASSWORD = os.environ["THINGS_PASSWORD"]


def main():
    credentials = Credentials(email=EMAIL, password=SecretStr(PASSWORD))
    account = Account.login(credentials)
    things = ThingsClient(account)

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
