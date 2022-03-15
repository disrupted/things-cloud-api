# Things Cloud Python client

> work in progress, expect breaking changes

Things is an excellent to-do manager for Apple devices, specifically the Mac, iPad, iPhone and Watch. Unfortunately there is no support outside these devices. Like many other users, I encountered this limitation after spending years using Things daily to plan nearly every aspect of my life and work.

> "A life without Things is possible, but pointless." — Loriot (German humorist)

This is an attempt of recreating some basic functionality Things Cloud has to offer, to help automate some recurring tasks (e.g. inside of Home Assistant).

Since there's no documentation, I've been analyzing the requests made by the Mac app. The exchanged data is often difficult to understand, because none of the fields use clear names. So far, figuring out the meaning of the to-do item fields, has been a mixed success. I was able to document some fields, while others remain a mystery.

Contributions are welcome to translate the rest of the fields.

## Progress

- [x] Todos
  - [x] create
  - [ ] edit
  - [ ] list
- [ ] Projects
  - [ ] create
- [ ] Areas
  - [ ] Today
  - [ ] Inbox
