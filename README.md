# Things Cloud Python client

> work in progress, expect breaking changes

Things is an excellent to-do manager for Apple devices, specifically the Mac, iPad, iPhone and Watch. Unfortunately there is no support outside these devices. Like many other users, I encountered this limitation after spending years using Things daily to plan nearly every aspect of my life and work.

> "A life without Things is possible, but pointless." — Loriot (German humorist)

This is an attempt of recreating some basic functionality Things Cloud has to offer, to help automate some recurring tasks (e.g. inside of Home Assistant).

Since there's no documentation, I've been analyzing the requests made by the Mac app. The exchanged data is often difficult to understand, because none of the fields use clear names. So far, figuring out the meaning of the to-do item fields, has been a mixed success. I was able to document some fields, while others remain a mystery.

Contributions are welcome to translate the rest of the fields.

## Usage

```python
from time import sleep
from things_cloud import ThingsClient
from things_cloud.models import TodoItem

ACCOUNT = "<your-account-id>"
# current head index of Cloud database (if you know it)
OFFSET = 1234
# otherwise
OFFSET = None

things = ThingsClient(ACCOUNT, initial_offset=OFFSET)
# create a project
project = TodoItem("Things Cloud Project").as_project()
# push to Things Cloud
project_uuid = things.create(project) # returns unique ID for project

sleep(10)
# create a todo inside project
todo = TodoItem("Try out Things Cloud")
todo.project = project_uuid
todo_uuid = things.create(todo) # returns unique ID for todo

sleep(20)
# schedule for today
todo.today()
things.edit(todo_uuid, todo)
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

none that I know of

### Disclaimer

This project is not affiliated with Cultured Code. They make a fantastic product, and I hope they will provide an official way of interacting with the API one day. If you want to learn more about it, visit [culturedcode.com](https://culturedcode.com/things/).
