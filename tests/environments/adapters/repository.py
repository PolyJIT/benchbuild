"""
Fake inteaction with a buildah container registry.
"""
import typing as tp
import uuid

import attr

from benchbuild.environments.adapters import repository
from benchbuild.environments.domain import model


@attr.s
class FakeRegistry(repository.AbstractRegistry):
    image_db: tp.Dict[str, model.Image] = attr.ib(default=attr.Factory(set))

    def _create(self, tag: str, layers: tp.List[model.Layer]):
        from_ = [l for l in layers if isinstance(l, model.FromLayer)].pop(0)
        image = model.Image(tag, from_, layers[1:])

        self.image_db[tag] = image

        return model.Container(str(uuid.uuid4()), image, '')

    def _get(self, tag: str) -> model.MaybeImage:
        return self.image_db.get(tag, None)
