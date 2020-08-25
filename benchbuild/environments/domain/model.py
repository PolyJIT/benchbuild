import abc
import typing as tp

import attr

from benchbuild.environments.domain import events


@attr.s
class Layer(abc.ABC):
    pass


@attr.s(frozen=True)
class FromLayer(Layer):
    base: str = attr.ib()


@attr.s(frozen=True)
class AddLayer(Layer):
    sources: tp.List[str] = attr.ib()
    destination: str = attr.ib()


@attr.s(frozen=True)
class CopyLayer(Layer):
    sources: tp.List[str] = attr.ib()
    destination: str = attr.ib()


@attr.s(frozen=True)
class RunLayer(Layer):
    command: str = attr.ib()
    args: tp.List[str] = attr.ib()
    kwargs: tp.Dict[str, str] = attr.ib()


@attr.s(frozen=True)
class ContextLayer(Layer):
    func: tp.Callable[[], None] = attr.ib()


@attr.s(frozen=True)
class UpdateEnv(Layer):
    env = attr.ib()  # type: tp.Dict[str, str]


@attr.s(eq=False)
class Image:
    name: str = attr.ib()
    from_: FromLayer = attr.ib()
    layers: tp.List[Layer] = attr.ib()
    events = attr.ib(factory=list)  # type: tp.List[events.Event]
    env = attr.ib(factory=dict)  # type: tp.Dict[str, str]

    def update_env(self, **kwargs) -> None:
        self.env.update(kwargs)

    def append(self, layer: Layer) -> None:
        self.layers.append(layer)

    def prepend(self, layer: Layer) -> None:
        self.layers = [layer].extend(self.layers)


MaybeImage = tp.Optional[Image]


@attr.s(eq=False)
class Container:
    container_id: str = attr.ib()
    image: Image = attr.ib()
    context: str = attr.ib()

    events = attr.ib(factory=list)  # type: tp.List[events.Event]
