import typing as tp

from . import unit_of_work


class ImageNotFound(Exception):
    ...


class NamedCommand(tp.Protocol):

    @property
    def name(self) -> str:
        ...


def image_exists(
    cmd: NamedCommand, uow: unit_of_work.AbstractUnitOfWork
) -> None:
    image = uow.registry.get_image(cmd.name)
    if not image:
        raise ImageNotFound(cmd)
