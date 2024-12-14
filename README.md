# Things Cloud Python client

> work in progress, expect breaking changes

Things is an excellent to-do manager for Apple devices, specifically the Mac, iPad, iPhone and Watch. Unfortunately there is no support outside these devices. Like many other users, I encountered this limitation after spending years using Things daily to plan nearly every aspect of my life and work.

> "A life without Things is possible, but pointless." — Loriot (German humorist)

This is an attempt of recreating some basic functionality Things Cloud has to offer, to help automate some recurring tasks (e.g. inside of Home Assistant).

Since there's no documentation, I've been analyzing the requests made by the Mac app. The exchanged data is often difficult to understand, because none of the fields use clear names. So far, figuring out the meaning of the to-do item fields, has been a mixed success. I was able to document some fields, while others remain a mystery.

Contributions are welcome to translate the rest of the fields.

## Usage

```python
from things_cloud import ThingsClient
from things_cloud.api.account import Account, Credentials
from things_cloud.models import TodoItem

EMAIL = os.environ["THINGS_EMAIL"]
PASSWORD = os.environ["THINGS_PASSWORD"]

credentials = Credentials(email=EMAIL, password=PASSWORD)
account = Account.login(credentials)
things = ThingsClient(account)
# create a new project
project = TodoItem(title="Things Cloud Project").as_project()
# push to Things Cloud
things.commit(project)

# create a todo inside project
todo = TodoItem(title="Try out Things Cloud")
todo.project = project
things.commit(todo)

# schedule for today
todo.today()
things.commit(todo)
```

## Example

See [main.py](./main.py).

1. Install dependencies

```sh
poetry install
```

2. Pass your Things Cloud credentials as environment examples to run the example

```sh
THINGS_EMAIL=your-email@example.com THINGS_PASSWORD=your-password python main.py
```

### Progress

- [x] Todos
  - [x] create
  - [x] edit
  - [ ] list
  - [ ] note
- [x] Projects
  - [x] create
  - [x] edit
- [ ] Areas
  - [ ] Today
  - [ ] Inbox

### Similar projects

- @nicolai86's Go [`things-cloud-sdk`](https://github.com/nicolai86/things-cloud-sdk); it's also a work-in-progress, relying on reverse engineering the requests on the wire

### Disclaimer

This project is not affiliated with Cultured Code. They make a fantastic product, and I hope they will provide an official way of interacting with the API one day. If you want to learn more about it, visit [culturedcode.com](https://culturedcode.com/things/).
