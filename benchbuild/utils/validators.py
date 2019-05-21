"""
    Collection of reusable validators for usage in attr.s.
"""
from __future__ import annotations

import collections
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable


def attribute_not_empty(attribute: str) -> Callable[..., None]:
    def check_attr(self, _, new_attr_val) -> None:
        if not new_attr_val:
            raise ValueError(attribute + ' attribute must not be empty.')

    return check_attr


def usable_schema(self, _, new_schema) -> bool:
    if new_schema is None:
        return True
    if isinstance(new_schema, collections.abc.Iterable):
        return True
    return False
