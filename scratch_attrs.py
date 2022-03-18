import cattrs
from attrs import asdict, define, field, fields, filters
from cattrs.gen import make_dict_structure_fn, make_dict_unstructure_fn, override


@define
class User:
    _id: int
    name: str
    password: str
    _areas: list[str] = field(init=False, factory=list)

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, id: int):
        self._id = id

    @property
    def area(self) -> str:
        return self._areas[0]

    @area.setter
    def area(self, area: str):
        self._areas = [area]


user = User(1, "disrupted", ":supersecret:")
user.id = 999
user.area = "area51"

# basic dict conversion
d = asdict(user, filter=filters.exclude(fields(User).password))
print(d)

# default unstructuring
d = cattrs.unstructure(user)
print(d)

# custom unstructuring
converter = cattrs.Converter()
unst_hook = make_dict_unstructure_fn(
    User,
    converter,
    _id=override(rename="id"),
    password=override(omit=True),
    _areas=override(rename="areas"),
)
st_hook = make_dict_structure_fn(User, converter, _id=override(rename="id"))
converter.register_unstructure_hook(User, unst_hook)
converter.register_structure_hook(User, st_hook)  # type: ignore
d = converter.unstructure(user)
print(d)
# this is nice!
