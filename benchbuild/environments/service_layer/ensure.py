import sys

from . import unit_of_work

if sys.version_info <= (3, 8):
    from typing_extensions import Protocol
else:
    from typing import Protocol


class ImageNotFound(Exception):
    ...


class NamedCommand(Protocol):

    @property
    def name(self) -> str:
        ...


def image_exists(
    cmd: NamedCommand, uow: unit_of_work.AbstractUnitOfWork
) -> None:
    image = uow.registry.get_image(cmd.name)
    if not image:
        raise ImageNotFound(cmd)
