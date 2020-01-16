from typing import Any, Iterable, Dict

import attr


@attr.s(repr=False)
class Variant:
    owner: Any = attr.ib(repr=False)
    version: str = attr.ib()

    def __repr__(self):
        return self.version

    def __str__(self):
        return repr(self)


VariantTuple = Iterable[Variant]
VariantContext = Dict[str, Variant]


def context(variant: VariantTuple) -> VariantContext:
    var_list = list(variant)
    return {var.owner.local: var for var in var_list}


def to_str(variant: Iterable) -> str:
    return ",".join([str(i) for i in list(variant)])
