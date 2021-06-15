from dataclasses import dataclass, field

from dataclasses_json import config
from dataclasses_json.api import DataClassJsonMixin

from things import Destination


@dataclass
class TodoItem(DataClassJsonMixin):
    index: int = field(metadata=config(field_name="ix"))
    destination: int = field(metadata=config(field_name="st"))


# @dataclass
# class TodoItem(DataClassJsonMixin):
#     index: int
#     destination: Destination

#     def to_dict(self) -> dict:
#         return {
#             "ix": self.index,
#             "st": self.destination.value,
#         }

#     def to_json(self) -> str:
#         return json.dumps(self.to_dict())

if __name__ == "__main__":
    item = TodoItem(index=123, destination=Destination.TODAY)
    print(item.to_dict())
    print(item.to_json())
