from typing import Any, Iterable

import attr

from benchbuild.typing import Variant as VariantT
from benchbuild.typing import VariantContext, VariantTuple


@attr.s(repr=False)
class Variant(VariantT):
    owner: Any = attr.ib(repr=False)
    version: str = attr.ib()

    def __repr__(self):
        return self.version

    def __str__(self):
        return repr(self)


def context(variant: VariantTuple) -> VariantContext:
    var_list = list(variant)
    return {var.owner.local: var for var in var_list}


def to_str(variant: Iterable) -> str:
    return ",".join([str(i) for i in list(variant)])


def to_tag(variant: Iterable) -> str:
    return "-".join([str(i) for i in list(variant)])
