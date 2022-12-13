import abc
import enum
import typing as tp

import attr


# pylint: disable=too-few-public-methods
@attr.s(frozen=True)
class Message:
    pass


MessageT = tp.Type[Message]


@attr.s(frozen=True)
class Event(Message):
    pass


@attr.s(frozen=True)
class Command(Message):
    pass


class LayerState(enum.Enum):
    PRESENT = 1
    ABSENT = 2


@attr.s(frozen=True)
class Layer(abc.ABC):
    """
    A layer represents a filesystem layer in a container image.

    Layers can be 'virtual' in the sense that they do not lead to changes
    in the container image filesystem, e.g. setting up the build context.

    This more or less represents commands/statements available in buildah
    or Dockerfiles.

    Examples:
        buildah add -> AddLayer
        buildah copy -> CopyLayer
        buildah from -> FromLayer
    """


# pylint: enable=too-few-public-methods
@attr.s(frozen=True)
class FromLayer(Layer):
    base: str = attr.ib()

    def __str__(self) -> str:
        return f'FROM {self.base}'


@attr.s(frozen=True)
class AddLayer(Layer):
    sources: tp.Tuple[str, ...] = attr.ib()
    destination: str = attr.ib()

    def __str__(self) -> str:
        sources = ' '.join(self.sources)
        return f'ADD {sources} self.destination'


@attr.s(frozen=True)
class CopyLayer(Layer):
    sources: tp.Tuple[str, ...] = attr.ib()
    destination: str = attr.ib()

    def __str__(self) -> str:
        sources = ' '.join(self.sources)
        return f'COPY {sources} {self.destination}'


def immutable_kwargs(
    kwargs: tp.Dict[str, str]
) -> tp.Tuple[tp.Tuple[str, str], ...]:
    """
    Convert str-typed kwargs into a hashable tuple.
    """
    return tuple((k, v) for k, v in kwargs.items())


@attr.s(frozen=True)
class RunLayer(Layer):
    command: str = attr.ib()
    args: tp.Tuple[str, ...] = attr.ib()
    kwargs: tp.Tuple[tp.Tuple[str, str],
                     ...] = attr.ib(converter=immutable_kwargs)

    def __str__(self) -> str:
        args = ' '.join(self.args)
        return f'RUN {self.command} {args}'


@attr.s(frozen=True)
class ContextLayer(Layer):
    func: tp.Callable[[], None] = attr.ib()

    def __str__(self) -> str:
        return 'CONTEXT custom build context modification'


@attr.s(frozen=True)
class UpdateEnv(Layer):
    env: tp.Tuple[tp.Tuple[str, str], ...] = attr.ib(converter=immutable_kwargs)

    def __str__(self) -> str:
        return f'ENV {len(self.env)} entries'


@attr.s(frozen=True)
class WorkingDirectory(Layer):
    directory: str = attr.ib()

    def __str__(self) -> str:
        return f'CWD {self.directory}'


@attr.s(frozen=True)
class EntryPoint(Layer):
    command: tp.Tuple[str, ...] = attr.ib()

    def __str__(self) -> str:
        command = ' '.join(self.command)
        return f'ENTRYPOINT {command}'


@attr.s(frozen=True)
class SetCommand(Layer):
    command: tp.Tuple[str, ...] = attr.ib()

    def __str__(self) -> str:
        command = ' '.join(self.command)
        return f'CMD {command}'


@attr.s(frozen=True)
class Mount:
    source: str = attr.ib()
    target: str = attr.ib()

    def __str__(self) -> str:
        return f'{self.source}:{self.target}'


@attr.s(eq=False)
class Image:
    name: str = attr.ib()
    from_: FromLayer = attr.ib()
    layers: tp.List[Layer] = attr.ib()
    events: tp.List[Message] = attr.ib(attr.Factory(list))
    env: tp.Dict[str, str] = attr.ib(attr.Factory(dict))
    mounts: tp.List[Mount] = attr.ib(attr.Factory(list))
    layer_index: tp.Dict[Layer, LayerState] = attr.ib(attr.Factory(dict))

    def update_env(self, **kwargs: str) -> None:
        self.env.update(kwargs)

    def append(self, *layers: Layer) -> None:
        for layer in layers:
            self.layers.append(layer)
            self.layer_index[layer] = LayerState.ABSENT

    def present(self, layer: Layer) -> None:
        if layer in self.layer_index:
            self.layer_index[layer] = LayerState.PRESENT

    def is_present(self, layer: Layer) -> bool:
        return layer in self.layer_index and self.layer_index[
            layer] == LayerState.PRESENT

    def is_complete(self) -> bool:
        return all([
            state == LayerState.PRESENT for state in self.layer_index.values()
        ])

    def prepend(self, layer: Layer) -> None:
        old_layers = self.layers
        self.layers = [layer]
        self.layers.extend(old_layers)
        self.layer_index[layer] = LayerState.ABSENT


MaybeImage = tp.Optional[Image]


@attr.s(eq=False)
class Container:
    container_id: str = attr.ib()
    image: Image = attr.ib()
    context: str = attr.ib()
    name: str = attr.ib()

    events: tp.List[Message] = attr.ib(attr.Factory(list))


MaybeContainer = tp.Optional[Container]
