from typing import overload


@overload
def bool_int(bool_or_int: bool) -> int:
    ...


@overload
def bool_int(bool_or_int: int) -> bool:
    ...


def bool_int(bool_or_int: bool | int) -> int | bool:
    if isinstance(bool_or_int, bool):
        return int(bool_or_int)
    else:
        # bools are also ints in Python :'o
        # so this has to be the else case
        return bool(bool_or_int)
