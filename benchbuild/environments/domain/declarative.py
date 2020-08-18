import typing as tp

import attr

from . import commands


@attr.s
class ContainerImage(list):

    def from_(self, base_image: str) -> 'Environment':
        self.append(commands.CreateFromLayer(base_image))
        return self

    def context(self, func: tp.Callable[[], None]) -> 'ContainerImage':
        self.append(commands.CreateContext(func))
        return self

    def clear_context(self, func: tp.Callable[[], None]) -> 'ContainerImage':
        self.append(commands.ClearContext(func))
        return self

    def add(self, sources: tp.Iterable[str], tgt: str) -> 'ContainerImage':
        self.append(commands.CreateAddLayer(sources, tgt))
        return self

    def copy(self, sources: tp.Iterable[str], tgt: str) -> 'ContainerImage':
        self.append(commands.CreateCopyLayer(sources, tgt))
        return self

    def run(self, command: str, *args: str) -> 'ContainerImage':
        self.append(commands.CreateRunLayer(command, args))
        return self
