import abc
import typing as tp

import attr

from benchbuild.environments.domain import events


# pylint: disable=too-few-public-methods
@attr.s
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
    sources: tp.Iterable[str] = attr.ib()
    destination: str = attr.ib()

    def __str__(self) -> str:
        sources = ' '.join(self.sources)
        return f'ADD {sources} self.destination'


@attr.s(frozen=True)
class CopyLayer(Layer):
    sources: tp.Iterable[str] = attr.ib()
    destination: str = attr.ib()

    def __str__(self) -> str:
        sources = ' '.join(self.sources)
        return f'COPY {sources} self.destination'


@attr.s(frozen=True)
class RunLayer(Layer):
    command: str = attr.ib()
    args: tp.Tuple[str, ...] = attr.ib()
    kwargs: tp.Dict[str, str] = attr.ib()

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
    env = attr.ib()  # type: tp.Dict[str, str]

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
    events = attr.ib(attr.Factory(list))  # type: tp.List[events.Event]
    env = attr.ib(attr.Factory(dict))  # type: tp.Dict[str, str]
    mounts: tp.List[Mount] = attr.ib(attr.Factory(list))

    def update_env(self, **kwargs: str) -> None:
        self.env.update(kwargs)

    def append(self, layer: Layer) -> None:
        self.layers.append(layer)

    def prepend(self, layer: Layer) -> None:
        old_layers = self.layers
        self.layers = [layer]
        self.layers.extend(old_layers)


MaybeImage = tp.Optional[Image]


@attr.s(eq=False)
class Container:
    container_id: str = attr.ib()
    image: Image = attr.ib()
    context: str = attr.ib()

    events = attr.ib(attr.Factory(list))  # type: tp.List[events.Event]

    @property
    def name(self) -> str:
        return self.image.name
