import itertools
from typing import Dict, Iterable, Optional

import attr


@attr.s(repr=False)
class Variant:
    owner: 'BaseSource' = attr.ib(repr=False)
    version: str = attr.ib()

    def __repr__(self):
        return self.version

    def __str__(self):
        return repr(self)

def product(sources: Iterable['BaseSource']):
    siblings = [source.versions() for source in sources]
    return itertools.product(*siblings)

def context(variant) -> Dict[str, Variant]:
    var_list = list(variant)
    return {var.owner.local: var for var in var_list}

def to_str(variant):
    return ",".join([ str(i) for i in list(variant)])

def to_source(name: str, variant: Dict[str, Variant]) -> Optional['BaseSource']:
    return variant[name].owner if name in variant else None
